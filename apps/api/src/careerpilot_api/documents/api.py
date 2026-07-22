"""Authenticated document upload and owner-scoped status APIs."""

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, cast
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from pydantic import BaseModel

from careerpilot_api.auth.api import current_user
from careerpilot_api.db.models import DocumentModel, DocumentStatus, UserModel
from careerpilot_api.documents.crypto import ParsedContentCipher
from careerpilot_api.documents.parser import PARSER_VERSION, parse_document
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
    parser_version: str | None


def _repository(request: Request) -> DocumentRepository:
    return cast(DocumentRepository, request.app.state.document_repository)


def _storage(request: Request) -> ObjectStorage:
    return cast(ObjectStorage, request.app.state.object_storage)


def _cipher(request: Request) -> ParsedContentCipher:
    return cast(ParsedContentCipher, request.app.state.parsed_content_cipher)


def _response(document: DocumentModel) -> DocumentResponse:
    return DocumentResponse(
        id=document.id,
        document_type=document.document_type,
        filename=document.filename,
        mime_type=document.mime_type,
        checksum=document.checksum,
        status=document.status,
        created_at=document.created_at,
        parser_version=document.parser_version,
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


@router.post("/{document_id}/parse", response_model=DocumentResponse)
async def parse_uploaded_document(
    document_id: UUID,
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
) -> DocumentResponse:
    repository = _repository(request)
    document = await repository.get_by_id(user_id=user.id, document_id=document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        parsed = parse_document(
            content=_storage(request).get_bytes(key=document.storage_key),
            mime_type=document.mime_type,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="Document storage is unavailable.") from error

    sections = [section.__dict__ for section in parsed.sections]
    cipher = _cipher(request)
    saved = await repository.save_parse_result(
        user_id=user.id,
        document_id=document_id,
        parsed_text_encrypted=cipher.encrypt(parsed.text),
        parsed_sections_encrypted=cipher.encrypt(json.dumps(sections)),
        parser_version=PARSER_VERSION,
    )
    if saved is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return _response(saved)


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
