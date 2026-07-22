"""Typed S3-compatible storage adapter; document bytes are never logged."""

from typing import Protocol, cast

import boto3  # type: ignore[import-untyped]

from careerpilot_api.config import Settings


class S3Client(Protocol):
    def put_object(self, *, Bucket: str, Key: str, Body: bytes, ContentType: str) -> object:
        """Persist an S3 object."""

    def get_object(self, *, Bucket: str, Key: str) -> object:
        """Retrieve an S3 object."""


class ObjectStorage(Protocol):
    """The minimum object-store operations required by document upload."""

    def put_bytes(self, *, key: str, content: bytes, content_type: str) -> None:
        """Store bytes at an opaque application-generated key."""

    def get_bytes(self, *, key: str) -> bytes:
        """Retrieve bytes using an opaque application-generated key."""


class S3ObjectStorage:
    """S3-compatible adapter intended for MinIO locally and managed S3 in production."""

    def __init__(self, client: S3Client, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def put_bytes(self, *, key: str, content: bytes, content_type: str) -> None:
        self._client.put_object(
            Bucket=self._bucket, Key=key, Body=content, ContentType=content_type
        )

    def get_bytes(self, *, key: str) -> bytes:
        response = cast(dict[str, object], self._client.get_object(Bucket=self._bucket, Key=key))
        body = cast("S3Body", response["Body"])
        try:
            return body.read()
        finally:
            body.close()


class S3Body(Protocol):
    def read(self) -> bytes: ...

    def close(self) -> None: ...


def create_object_storage(settings: Settings) -> ObjectStorage:
    """Create a synchronous S3-compatible adapter without testing connectivity."""

    client = boto3.client(
        "s3",
        endpoint_url=settings.object_storage_endpoint,
        aws_access_key_id=settings.object_storage_access_key,
        aws_secret_access_key=settings.object_storage_secret_key.get_secret_value(),
        region_name="us-east-1",
    )
    return S3ObjectStorage(cast(S3Client, client), settings.object_storage_bucket)
