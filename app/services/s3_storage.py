import boto3
from botocore.exceptions import ClientError
from ..core.config import settings

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME
    )

def generate_presigned_url(object_name: str, content_type: str = "video/mp4", expiration: int = 3600):
    """
    Generate a presigned URL for the client to upload a file directly to S3.
    """
    s3_client = get_s3_client()
    try:
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_BUCKET_NAME,
                'Key': object_name,
                'ContentType': content_type
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(e)
        return None
    return response

def generate_presigned_view_url(object_name: str, expiration: int = 3600):
    """
    Generate a presigned URL to view/download a private file from S3.
    """
    s3_client = get_s3_client()
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_BUCKET_NAME,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(e)
        return None
    return response
