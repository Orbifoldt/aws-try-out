from collections.abc import Iterator
from typing import TYPE_CHECKING

import boto3
from dishka import Provider, Scope, provide

from app.settings import Settings

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client
else:
    from botocore.client import BaseClient as S3Client


class S3ClientProvider(Provider):
    @provide(scope=Scope.APP)
    def s3_client(self, settings: Settings) -> Iterator[S3Client]:
        if bool(settings.aws_access_key_id) != bool(settings.aws_secret_access_key):
            raise ValueError(
                "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be configured together"
            )

        client_args: dict[str, str | None] = {
            "region_name": settings.aws_region,
            "endpoint_url": settings.s3_endpoint_url,
        }
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            client_args["aws_access_key_id"] = settings.aws_access_key_id
            client_args["aws_secret_access_key"] = settings.aws_secret_access_key

        client: S3Client = boto3.client("s3", **client_args)  # ty: ignore[no-matching-overload]
        try:
            yield client
        finally:
            client.close()
