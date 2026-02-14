import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import BinaryIO, Optional
import aioboto3
from app.config import settings
import structlog

logger = structlog.get_logger()


class S3Storage:
    def __init__(self):
        self.session = aioboto3.Session()
        self.config = Config(
            max_pool_connections=settings.AWS_S3_MAX_CONNECTIONS,
            region_name=settings.AWS_REGION,
        )

    async def upload(self, bucket: str, key: str, data: BinaryIO, content_type: str) -> str:
        async with self.session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value() if settings.AWS_SECRET_ACCESS_KEY else None,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            config=self.config,
        ) as s3:
            await s3.upload_fileobj(
                data,
                bucket,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            logger.info("File uploaded to S3", bucket=bucket, key=key)
            return key

    async def download(self, bucket: str, key: str) -> Optional[bytes]:
        async with self.session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value() if settings.AWS_SECRET_ACCESS_KEY else None,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            config=self.config,
        ) as s3:
            try:
                response = await s3.get_object(Bucket=bucket, Key=key)
                return await response["Body"].read()
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    return None
                raise

    async def delete(self, bucket: str, key: str) -> None:
        async with self.session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value() if settings.AWS_SECRET_ACCESS_KEY else None,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            config=self.config,
        ) as s3:
            await s3.delete_object(Bucket=bucket, Key=key)
            logger.info("File deleted from S3", bucket=bucket, key=key)

    async def generate_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        async with self.session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value() if settings.AWS_SECRET_ACCESS_KEY else None,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            config=self.config,
        ) as s3:
            url = await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
