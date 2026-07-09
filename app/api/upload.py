from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import uuid
import time
from ..core.dependencies import get_current_active_user
from ..models.user import User
from ..services.s3_storage import generate_presigned_url

router = APIRouter()

class UploadRequest(BaseModel):
    file_type: str # ex: 'video/mp4', 'image/jpeg'
    file_extension: str # ex: 'mp4', 'jpg'

class UploadResponse(BaseModel):
    upload_url: str
    file_key: str

@router.post("/presigned-url", response_model=UploadResponse)
def get_upload_url(
    request: UploadRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna uma URL temporária (pre-signed URL) para fazer upload direto pro S3.
    Dessa forma, o arquivo pesado não passa pelo nosso servidor FastAPI.
    """
    # Create a unique file name
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    
    # Structure: user_id / type / timestamp_uuid.ext
    # Example: 1234-5678-abcd/video/162817281_1a2b3c.mp4
    folder = "videos" if "video" in request.file_type else "images"
    file_key = f"{current_user.id}/{folder}/{timestamp}_{unique_id}.{request.file_extension}"
    
    presigned_url = generate_presigned_url(
        object_name=file_key, 
        content_type=request.file_type
    )
    
    if not presigned_url:
        raise HTTPException(status_code=500, detail="Could not generate upload URL")
        
    return {
        "upload_url": presigned_url,
        "file_key": file_key
    }
