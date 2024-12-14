import os
import uuid
from io import BytesIO
from typing import Optional

import boto3
from PIL import Image
from botocore.config import Config
from fastapi import UploadFile
from filetype import filetype

from core.config import settings
from core.enums import ImageSize


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

        self.size_configs = {
            ImageSize.X1: 1,
            ImageSize.X2: 2,
            ImageSize.X3: 3
        }

    def _generate_filename(self, original_filename: str, folder: str) -> str:
        """생성된 UUID와 원본 파일 확장자로 새로운 파일명 생성"""
        _, ext = os.path.splitext(original_filename)
        return f"{folder}/{uuid.uuid4()}{ext}"

    def _resize_image(
            self,
            image: Image,
            base_width: int,
            size_multiplier: int
    ) -> Image:
        """이미지 리사이징"""
        if size_multiplier == 1:
            return image

        new_width = base_width * size_multiplier
        ratio = new_width / float(image.size[0])
        new_height = int(float(image.size[1]) * ratio)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    async def upload_image(
            self,
            file: UploadFile,
            folder: str = "ingredients",
            base_width: int = 100
    ) -> Optional[dict]:
        try:
            contents = await file.read()

            # 파일 타입 확인
            kind = filetype.guess(contents)
            if not kind or not kind.mime.startswith('image/'):
                raise ValueError("Not an image file")

            # 원본 이미지 로드
            image = Image.open(BytesIO(contents))

            # 기본 파일명 생성 (확장자 제외)
            base_filename = self._generate_filename(file.filename, folder)
            filename_without_ext, ext = os.path.splitext(base_filename)

            # 각 사이즈별로 이미지 업로드
            urls = {}
            for size_name, multiplier in self.size_configs.items():
                # 이미지 리사이징
                resized = self._resize_image(image, base_width, multiplier)

                # BytesIO로 변환
                buffer = BytesIO()
                resized.save(buffer, format=image.format)
                buffer.seek(0)

                # 파일명 생성
                filename = f"{filename_without_ext}_{size_name.value}{ext}"

                # S3에 업로드
                self.s3.put_object(
                    Bucket=self.bucket,
                    Key=filename,
                    Body=buffer.getvalue(),
                    ContentType=kind.mime,
                    ACL='public-read'
                )

                # URL 저장
                urls[size_name] = f"https://{self.bucket}.kr.object.ncloudstorage.com/{filename}"

            return {
                "key": filename_without_ext,
                "urls": urls
            }

        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None

    def delete_image(self, key: str) -> bool:
        """모든 사이즈의 이미지 삭제"""
        try:
            # 파일 확장자 찾기
            for obj in self.s3.list_objects(Bucket=self.bucket, Prefix=key)['Contents']:
                if obj['Key'].startswith(key):
                    ext = os.path.splitext(obj['Key'])[1]
                    break

            # 각 사이즈별 이미지 삭제
            for size in ImageSize:
                filename = f"{key}_{size}{ext}"
                self.s3.delete_object(
                    Bucket=self.bucket,
                    Key=filename
                )
            return True

        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

    def get_image_urls(self, key: str) -> Optional[dict]:
        """저장된 이미지의 각 크기별 URL 반환"""
        if not key:
            return None

        base_url = f"https://{self.bucket}.kr.object.ncloudstorage.com"

        return {
            "1x": f"{base_url}/{key}_{ImageSize.X1.value}.png",
            "2x": f"{base_url}/{key}_{ImageSize.X2.value}.png",
            "3x": f"{base_url}/{key}_{ImageSize.X3.value}.png"
        }


# 싱글톤 인스턴스
object_storage = ObjectStorage()
