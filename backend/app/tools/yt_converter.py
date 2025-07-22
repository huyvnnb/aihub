import asyncio
import io
import subprocess
from typing import List

import yt_dlp

from app.schemas.yt_converter_schema import VideoResponse, Resolution
from app.utils.logger import get_logger, Module
from app.utils.utils import run_in_threadpool
logger = get_logger(Module.YOUTUBE)


class YoutubeService:

    @staticmethod
    def _format_url(url: str) -> str:
        index = url.find("&list")
        return url[:index] if index != -1 else url

    def _get_video_info_sync(self, url: str):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info

    async def get_video_info(self, url: str) -> VideoResponse:
        """
        Prints available MP4 video formats (format ID, resolution, and size) for a given video URL.

        :param url: The URL of the video to inspect.
        """
        try:
            formatted_url = self._format_url(url)
            video_info = await run_in_threadpool(self._get_video_info_sync, formatted_url)

            # print(f"Tiêu đề: {video_info.get('title')}")
            # print(f"Thumbnail: {video_info.get('thumbnail')}")
            # print(f"Thời lượng: {video_info.get('duration_string')}")

            resolutions: List[Resolution] = []
            for f in video_info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                    filesize_mb = f.get('filesize') or f.get('filesize_approx')
                    if filesize_mb:
                        filesize_mb = round(filesize_mb / 1024 / 1024, 2)
                        resolution = Resolution(
                            id=f.get('format_id'),
                            resolution=f.get('resolution', 'audio-only'),
                            size=filesize_mb
                        )
                        resolutions.append(resolution)
                        # print(f"{f.get('format_id'):<8} | {f.get('resolution', 'audio-only'):<12} | {filesize_mb:>7} MB")

            response = VideoResponse(
                title=video_info.get('title'),
                thumbnail=video_info.get('thumbnail'),
                duration=video_info.get('duration_string'),
                resolutions=resolutions
            )

            return response
        except Exception as e:
            raise Exception(f"Failed to get video info: {e}")

    def _convert_mp3_sync(self, url: str):
        # ffmpeg_location = r"D:\ffmpeg\bin"
        # user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        #               "Chrome/120.0.0.0 Safari/537.36")
        command = [
            "yt-dlp",
            "--ignore-config",
            # "--user-agent", user_agent,
            # "--ffmpeg-location", ffmpeg_location,
            "--limit-rate", "5M",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            self._format_url(url),
            "-o", "-"
        ]
        try:
            logger.info(f"Executing command: {' '.join(command)}")

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout, stderr = process.communicate(timeout=300)

            if process.returncode != 0:
                error_message = stderr.decode('utf-8', errors='ignore')
                print(f"ERROR from yt-dlp (return code {process.returncode}): {error_message}")
                raise Exception(f"yt-dlp failed: {error_message}")

            return stdout
        except subprocess.TimeoutExpired:
            process.kill()
            print("ERROR: Conversion process timed out.")
            raise Exception("Conversion process timed out after 5 minutes.")
        except FileNotFoundError:
            raise Exception(
                "yt-dlp or ffmpeg not found. Please ensure they are in the system's PATH or specified correctly.")

    async def get_mp3_stream_buffer(self, url: str) -> io.BytesIO:
        mp3_bytes = await run_in_threadpool(self._convert_mp3_sync, url)
        return io.BytesIO(mp3_bytes)

    # This function is used for chunking, but it is not support in Windows
    async def stream_audio_mp3(self, url: str):
        """
        Downloads the audio from a video and converts it to MP3 format.

        :param url: The URL of the video to extract audio from.
        :param output_path: Output path template for saving the MP3 file.
        """
        formatted_url = self._format_url(url)
        command = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            formatted_url,
            "-o", "-"
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while True:
            chunk = await process.stdout.read(8192)
            if not chunk:
                break
            yield chunk

        await process.wait()
        if process.returncode != 0:
            error = await process.stderr.read()
            logger.error(f"yt-dlp/ffmpeg error: {error.decode()}")
            raise Exception(f"Failed to process and stream MP3. Error: {error.decode()}")


def get_youtube_service():
    return YoutubeService()