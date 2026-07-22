"""Authenticated document upload and owner-scoped status APIs."""

from datetime import datetime
from pathlib import Path
from typing import Annotated, cast
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from pydantic import BaseModel

from careerpilot_api.auth.api import current_user
from careerpilot_api.db.models import DocumentModel, DocumentStatus, UserModel
from careerpilot_api.documents.repository import DocumentRepository
from careerpilot_api.documents.service import document_checksum, validate_upload
from careerpilot_api.storage.s3 import ObjectStorage

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    id: UUID
    document_type: str
    filename: str
    mime_type: str
    checksum: str
    status: DocumentStatus
    created_at: datetime


def _repository(request: Request) -> DocumentRepository:
    return cast(DocumentRepository, request.app.state.document_repository)


def _storage(request: Request) -> ObjectStorage:
    return cast(ObjectStorage, request.app.state.object_storage)


def _response(document: DocumentModel) -> DocumentResponse:
    return DocumentResponse(
        id=document.id,
        document_type=document.document_type,
        filename=document.filename,
        mime_type=document.mime_type,
        checksum=document.checksum,
        status=document.status,
        created_at=document.created_at,
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    response: Response,
    file: Annotated[UploadFile, File()],
    user: Annotated[UserModel, Depends(current_user)],
) -> DocumentResponse:
    filename = Path(file.filename or "upload").name
    mime_type = file.content_type or ""
    content = await file.read()
    try:
        document_type = validate_upload(content=content, filename=filename, mime_type=mime_type)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    checksum = document_checksum(content)
    repository = _repository(request)
    existing = await repository.get_by_checksum(user_id=user.id, checksum=checksum)
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        return _response(existing)

    document_id = uuid4()
    storage_key = f"users/{user.id}/documents/{document_id}"
    try:
        _storage(request).put_bytes(key=storage_key, content=content, content_type=mime_type)
    except Exception as error:
        raise HTTPException(status_code=503, detail="Document storage is unavailable.") from error

    document = await repository.create(
        DocumentModel(
            id=document_id,
            user_id=user.id,
            document_type=document_type,
            filename=filename,
            mime_type=mime_type,
            storage_key=storage_key,
            checksum=checksum,
            status=DocumentStatus.UPLOADED,
        )
    )
    return _response(document)


@router.get("/{document_id}/status", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
) -> DocumentResponse:
    document = await _repository(request).get_by_id(user_id=user.id, document_id=document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return _response(document)
