
import io
from typing import AnyStr, Union

from PIL import Image

from src.clients.aws import awss3


class FileService:

    async def upload_file(self, file_path, file_object) -> Union[dict, AnyStr, None]:
        file_extension = file_path.split('.')[-1]
        file_name = file_path.split('.')[0]
        file_path = f'{file_name}.{file_extension}'
        if file_extension.lower() in ['jpg', 'jpeg', 'png']:
            img = Image.open(file_object)

            # Resize the image, maintaining its aspect ratio
            max_size = (800, 800)
            img.thumbnail(max_size)

            # Save the resized image to a BytesIO object
            buffer = io.BytesIO()
            if file_extension.lower() in ['jpg', 'jpeg']:
                img_format = 'JPEG'
            else:
                img_format = file_extension.upper()
            img.save(buffer, format=img_format)
            buffer.seek(0)

            await awss3.upload_file_to_s3(file_path, buffer)
        else:
            await awss3.upload_file_to_s3(file_path, file_object)
        return {'success': True, 'file_path': file_path}

    async def download_file(self, file_path) -> Union[dict, AnyStr]:
        return await awss3.download_file(file_path)

    async def delete_file(self, file_name: str) -> Union[dict, AnyStr]:
        return await awss3.delete_file(file_name)

    async def signed_url(self, file_name: str) -> Union[dict, AnyStr]:
        return await awss3.signed_url(file_name)

    async def get_url(self, file_name: str) -> str:
        return await awss3.get_file_url(file_name)


file_service = FileService()
