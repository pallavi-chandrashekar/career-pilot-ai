"""Typed structured-claim extraction provider boundary."""

import json
from dataclasses import dataclass
from typing import Protocol

from openai import OpenAI

from careerpilot_api.claims.prompt import SYSTEM_PROMPT


@dataclass(frozen=True)
class ExtractedClaim:
    claim_type: str
    canonical_statement: str
    start_line: int
    end_line: int


class ClaimExtractionProvider(Protocol):
    name: str

    def extract(self, *, model: str, parsed_text: str) -> tuple[ExtractedClaim, ...]:
        """Return only source-grounded claim candidates from supplied text."""


class ProviderRegistry:
    def __init__(self, providers: tuple[ClaimExtractionProvider, ...]) -> None:
        self._providers = {provider.name: provider for provider in providers}

    def get(self, provider_name: str) -> ClaimExtractionProvider:
        try:
            return self._providers[provider_name]
        except KeyError as error:
            raise ValueError("The selected LLM provider is not enabled.") from error


class OpenAIClaimExtractionProvider:
    """OpenAI structured-output adapter; never logs parsed resume text."""

    name = "openai"

    def __init__(self, api_key: str) -> None:
        self._client = OpenAI(api_key=api_key)

    def extract(self, *, model: str, parsed_text: str) -> tuple[ExtractedClaim, ...]:
        response = self._client.responses.create(
            model=model,
            instructions=SYSTEM_PROMPT,
            input=parsed_text,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "candidate_claims",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "claims": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "claim_type": {"type": "string"},
                                        "canonical_statement": {"type": "string"},
                                        "start_line": {"type": "integer", "minimum": 1},
                                        "end_line": {"type": "integer", "minimum": 1},
                                    },
                                    "required": [
                                        "claim_type",
                                        "canonical_statement",
                                        "start_line",
                                        "end_line",
                                    ],
                                    "additionalProperties": False,
                                },
                            }
                        },
                        "required": ["claims"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        try:
            payload = json.loads(response.output_text)
            return tuple(ExtractedClaim(**claim) for claim in payload["claims"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ValueError("The LLM returned an invalid claim extraction response.") from error


class DeterministicClaimExtractionProvider:
    """Test-only provider with configured fictional structured output."""

    name = "deterministic"

    def __init__(self, claims: tuple[ExtractedClaim, ...]) -> None:
        self._claims = claims

    def extract(self, *, model: str, parsed_text: str) -> tuple[ExtractedClaim, ...]:
        return self._claims
