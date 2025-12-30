import cloudinary
import os
from cloudinary.uploader import upload
from dotenv import load_dotenv
from fastapi import HTTPException, status, UploadFile
import io

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

async def upload_image(image: UploadFile):
    if not image:
        return None
    try:
        # Read the file bytes asynchronously
        file_bytes = await image.read()

        # Wrap bytes in a file-like object for Cloudinary
        file_like = io.BytesIO(file_bytes)

        # Cloudinary upload (synchronous)
        upload_result = upload(file_like)
        file_url = upload_result.get('secure_url')
        return file_url

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image Upload Failed: {e}"
        )





# import cloudinary
# import os
# from cloudinary.uploader import upload
# from dotenv import load_dotenv
# from fastapi import  HTTPException,status, UploadFile
#
#
# load_dotenv()
#
#
# cloudinary.config(
#     cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
#     api_key=os.getenv("CLOUDINARY_API_KEY"),
#     api_secret=os.getenv("CLOUDINARY_API_SECRET")
# )
#
# async def upload_image(image: UploadFile):
#     try:
#         upload_result = upload(image.file)
#         file_url = upload_result['secure_url']
#         return file_url
#
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading images: {e}")