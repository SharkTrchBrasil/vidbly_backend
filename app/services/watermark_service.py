import os
import tempfile
import subprocess
from app.services.s3_storage import get_s3_client
from app.core.config import settings

def generate_watermark(s3_key_original: str) -> str:
    s3_client = get_s3_client()
    
    # Generate the watermarked key
    path_parts = s3_key_original.split('/')
    if len(path_parts) >= 3 and path_parts[1] == 'videos' and path_parts[2] == 'original':
        # format: {user_id}/videos/original/{filename}
        filename = path_parts[-1]
        watermarked_s3_key = f"{path_parts[0]}/videos/watermarked/{filename}"
    else:
        # fallback formatting
        filename = path_parts[-1]
        watermarked_s3_key = f"watermarked/{filename}"

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "output.mp4")
        
        # Download from S3
        s3_client.download_file(settings.AWS_BUCKET_NAME, s3_key_original, input_path)
        
        # Apply watermark with FFmpeg
        # diagonal semi-transparent "VIDBLY" text
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-vf", "drawtext=text='VIDBLY':fontcolor=white@0.3:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2:angle=45",
            "-c:a", "copy",
            output_path
        ]
        
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Upload back to S3
        s3_client.upload_file(
            output_path,
            settings.AWS_BUCKET_NAME,
            watermarked_s3_key,
            ExtraArgs={'ContentType': 'video/mp4'}
        )
        
    return watermarked_s3_key
