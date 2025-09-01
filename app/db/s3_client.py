import boto3
from botocore.exceptions import ClientError
from typing import BinaryIO
from core.config import settings


class S3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_s3_region
        )
        self.bucket_name = settings.aws_s3_bucket

    def upload_file(self, file_obj: BinaryIO, s3_key: str, content_type: str = "application/pdf") -> bool:
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            return True
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False

    def generate_s3_key(self, user_id: str, session_id: str, document_id: str, filename: str) -> str:
        extension = filename.split('.')[-1] if '.' in filename else 'pdf'
        return f"{user_id}/{session_id}/{document_id}.{extension}"

    def get_file_url(self, s3_key: str, expires_in: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return ""


# Global instance
s3_client = S3Client()