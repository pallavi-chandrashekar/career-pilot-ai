"""Authenticated, evidence-grounded draft claim extraction endpoints."""

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from careerpilot_api.auth.api import current_user
from careerpilot_api.claims.provider import ProviderRegistry
from careerpilot_api.claims.repository import ClaimRepository
from careerpilot_api.claims.service import extraction_idempotency_key, validate_claims
from careerpilot_api.db.models import (
    CandidateClaimModel,
    ClaimVerificationStatus,
    UserModel,
    WorkflowRunModel,
    WorkflowStatus,
)
from careerpilot_api.documents.crypto import ParsedContentCipher
from careerpilot_api.documents.repository import DocumentRepository

router = APIRouter(prefix="/api/v1", tags=["claims"])


class ExtractionRequest(BaseModel):
    provider: str | None = None
    model: str | None = Field(default=None, max_length=128)


class WorkflowResponse(BaseModel):
    id: UUID
    status: WorkflowStatus


class ClaimResponse(BaseModel):
    id: UUID
    source_document_id: UUID
    claim_type: str
    canonical_statement: str
    source_locator: dict[str, int]
    verification_status: ClaimVerificationStatus


def _claims(request: Request) -> ClaimRepository:
    return cast(ClaimRepository, request.app.state.claim_repository)


@router.post("/documents/{document_id}/extract-claims", response_model=WorkflowResponse)
async def extract_claims(
    document_id: UUID,
    payload: ExtractionRequest,
    request: Request,
    user: Annotated[UserModel, Depends(current_user)],
) -> WorkflowResponse:
    document = await cast(DocumentRepository, request.app.state.document_repository).get_by_id(
        user_id=user.id, document_id=document_id
    )
    if (
        document is None
        or document.parsed_text_encrypted is None
        or document.parser_version is None
    ):
        raise HTTPException(
            status_code=409, detail="Document must be parsed before claim extraction."
        )
    settings = request.app.state.settings
    provider_name = payload.provider or settings.llm_default_provider
    model = payload.model or settings.llm_default_model
    key = extraction_idempotency_key(
        user_id=user.id,
        document_checksum=document.checksum,
        parser_version=document.parser_version,
        provider=provider_name,
        model=model,
    )
    repository = _claims(request)
    existing = await repository.get_workflow_by_key(key)
    if existing is not None:
        return WorkflowResponse(id=existing.id, status=existing.status)
    try:
        parsed_text = cast(ParsedContentCipher, request.app.state.parsed_content_cipher).decrypt(
            document.parsed_text_encrypted
        )
        proposed = (
            cast(ProviderRegistry, request.app.state.claim_provider_registry)
            .get(provider_name)
            .extract(model=model, parsed_text=parsed_text)
        )
        claims = validate_claims(claims=proposed, parsed_text=parsed_text)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    workflow = WorkflowRunModel(
        user_id=user.id,
        workflow_type="CLAIM_EXTRACTION",
        idempotency_key=key,
        status=WorkflowStatus.COMPLETED,
        provider=provider_name,
        model=model,
        prompt_version="claim-extraction-v1",
    )
    records = [
        CandidateClaimModel(
            user_id=user.id,
            source_document_id=document.id,
            claim_type=claim.claim_type,
            canonical_statement=claim.canonical_statement,
            source_locator={"start_line": claim.start_line, "end_line": claim.end_line},
            verification_status=ClaimVerificationStatus.DRAFT,
            provider=provider_name,
            model=model,
            prompt_version="claim-extraction-v1",
        )
        for claim in claims
    ]
    saved = await repository.create_workflow_with_claims(workflow, records)
    return WorkflowResponse(id=saved.id, status=saved.status)


@router.get("/candidate-claims", response_model=list[ClaimResponse])
async def list_claims(
    request: Request, user: Annotated[UserModel, Depends(current_user)]
) -> list[ClaimResponse]:
    return [
        ClaimResponse(
            id=claim.id,
            source_document_id=claim.source_document_id,
            claim_type=claim.claim_type,
            canonical_statement=claim.canonical_statement,
            source_locator=claim.source_locator,
            verification_status=claim.verification_status,
        )
        for claim in await _claims(request).list_claims(user_id=user.id)
    ]
