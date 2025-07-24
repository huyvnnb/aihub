import io

from fastapi import APIRouter, UploadFile, File, Depends
from starlette.responses import StreamingResponse

from app.tools.remove_bg import get_image_service, ImageService
from app.utils.utils import run_in_threadpool

router = APIRouter(
    prefix="/tools/image",
    tags=["Tools"]
)


@router.post('/remove-background')
async def remove_background(file: UploadFile = File(...), service: ImageService=Depends(get_image_service)):
    image = await file.read()
    output = await run_in_threadpool(service.remove_background, image)
    return StreamingResponse(
        io.BytesIO(output), media_type="image/png"
    )