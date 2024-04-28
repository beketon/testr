import json
import mimetypes

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from starlette.responses import StreamingResponse

from src.config import settings
from src.exceptions import BadRequestS3

session = boto3.session.Session()

class AWSS3:
    def __init__(self):
        self.s3_bucket = settings.S3_BUCKET
        self.endpoint_url = f"https://hb.kz-ast.vkcs.cloud"
        self.s3_client = session.client(service_name='s3', endpoint_url=self.endpoint_url)
    
    async def upload_file_to_s3(self, file_path, file_object) -> None:
        self.s3_client.upload_fileobj(file_object, self.s3_bucket, file_path)

    async def download_file(self, file_path):
        try:
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket, Key=file_path)
            consent_type = mimetypes.guess_type(file_path)[0]
            return StreamingResponse(response['Body'], media_type=consent_type)
        except ClientError:
            raise BadRequestS3()
    
    async def delete_file(self, file_name: str):
        try:
            response = self.s3_client.delete_object(
                Bucket=self.s3_bucket, Key=file_name)
            return response
        except ClientError:
            raise BadRequestS3()

    async def get_file_url(self, file_name):
        try:
            url = self.s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': self.s3_bucket,
                                                                'Key': file_name},
                                                        ExpiresIn=3600)
            return url
        except NoCredentialsError:
            print("Credentials not available")
            return None


awss3 = AWSS3()
