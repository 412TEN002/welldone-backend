import uuid
from typing import Optional

import boto3
from botocore.config import Config
from fastapi import UploadFile

from core.config import settings


class ObjectStorage:
    def __init__(self):
        self.access_key = settings.NAVER_CLOUD_ACCESS_KEY
        self.secret_key = settings.NAVER_CLOUD_SECRET_KEY
        self.endpoint = settings.NAVER_CLOUD_ENDPOINT
        self.region = settings.NAVER_CLOUD_REGION
        self.bucket = settings.NAVER_CLOUD_BUCKET

        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(
                signature_version='s3v4',
                region_name=self.region
            )
        )

    def _generate_filename(self, original_filename: str, folder: str) -> str:
        """생성된 UUID로 새로운 파일명 생성"""
        return f"{folder}/{uuid.uuid4()}.svg"

    async def upload_image(
            self,
            file: UploadFile,
            folder: str = "ingredients",
            is_home: bool = False
    ) -> Optional[dict]:
        try:
            contents = await file.read()

            # SVG 파일 검증
            if not file.filename.lower().endswith('.svg'):
                raise ValueError("Only SVG files are allowed")

            # 홈화면용 이미지는 다른 경로에 저장
            if is_home:
                folder = f"home/{folder}"

            filename = self._generate_filename(file.filename, folder)

            self.s3.put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=contents,
                ContentType='image/svg+xml',
                ACL='public-read'
            )

            url = f"https://{self.bucket}.kr.object.ncloudstorage.com/{filename}"

            return {
                "key": filename,
                "url": url
            }

        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None

    def delete_image(self, key: str, is_home: bool = False) -> bool:
        """이미지 삭제"""
        try:
            self.s3.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False


# 싱글톤 인스턴스
object_storage = ObjectStorage()
