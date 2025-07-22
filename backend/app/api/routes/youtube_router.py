from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import StreamingResponse
from unidecode import unidecode

from app.schemas.response_schema import ModelResponse
from app.schemas.yt_converter_schema import VideoResponse
from app.tools.yt_converter import get_youtube_service
from app.utils import messages
from app.utils.logger import get_logger

logger = get_logger()

router = APIRouter(
    prefix="/tools/youtube",
    tags=["Tools"]
)


@router.get('/video-info',
            status_code=200,
            response_model=ModelResponse[VideoResponse],
            response_model_exclude_none=True
            )
async def get_video_info(url: str, youtube_service=Depends(get_youtube_service)):
    response = await youtube_service.get_video_info(url)
    return ModelResponse(
        message=messages.Tools.GET_VIDEO_INFO_SUCCESS,
        data=response
    )


@router.get('/download-mp3')
async def download_audio_mp3(url: str, youtube_service=Depends(get_youtube_service)):
    try:
        info = await youtube_service.get_video_info(url)
        video_title = info.title
        safe_fallback_filename = "".join(
            c for c in unidecode(video_title) if c.isalnum() or c in " ._-"
        ).strip() + ".mp3"

        logger.info(f"Safe fallback filename: {safe_fallback_filename}")

        mp3_buffer = await youtube_service.get_mp3_stream_buffer(url)

        headers = {
            'Content-Disposition': f'attachment; filename="{safe_fallback_filename}"'
        }

        return StreamingResponse(mp3_buffer, media_type="audio/mpeg", headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
