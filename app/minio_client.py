from minio import Minio
from minio.error import S3Error
from app.config import settings
from app.logger import setup_logger

logger = setup_logger()

client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False
)

def download_file(object_name, file_path):
    try:
        client.fget_object(settings.MINIO_BUCKET, object_name, file_path)
        logger.info(f"Downloaded {object_name} to {file_path}")
    except S3Error as e:
        logger.error(f"MinIO download failed: {e}")
        raise
