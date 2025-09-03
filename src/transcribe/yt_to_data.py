from datetime import datetime, timezone
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import validators
import logging
from yt_dlp import YoutubeDL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_url(string):
    return validators.url(string) is True


def get_youtube_id(url):
    parsed_url = urlparse(url)
    
    # Check if the URL is a valid YouTube link
    if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
        query_params = parse_qs(parsed_url.query)
        return query_params.get("v", [None])[0]  # Get the 'v' parameter
    elif parsed_url.netloc in ["youtu.be"]:  
        return parsed_url.path.lstrip("/")  # Extract video ID from short URLs
    return None  # Not a valid YouTube URL


def hook_function(status):
    if status['status'] == 'error':
        if 'retrying' in status['message'] and 'HTTP Error 400' in status['message']:
            logger.error(f"Stopping retries after a critical failure for video ID {status.get('filename', 'Unknown')}")
            raise Exception("Critical error encountered. Stopping download.")


def download_video(video_id: str, data_folder: Path):
    params = {
        "quiet": True,
        "format": "bestvideo*+bestaudio/best",
        "extract_audio": True,
        "outtmpl": "%(id)s/%(id)s.%(ext)s",
        "writeautomaticsub": True,
        "writesubtitles": True,
        "subtitlesformat": "vtt",
        "paths": {"home": str(data_folder)},
        "writeinfojson": True,
        "clean_infojson": True,
        "getcomments": True,
        "writeannotations": True,
        "agelimit": 99,
        "finalext": "webm",
        "postprocessors": [
        {
            "key" : "FFmpegVideoRemuxer", 
            "preferedformat" : "mp4"
        },
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        },
        ],
        "keepvideo": True,
        "logger": logger,
        "progress_hooks": [hook_function],
    }

    urls = [f"https://www.youtube.com/watch?v={video_id}"]
    with YoutubeDL(params) as ydl:
        try:
            ydl.download(urls)
        except Exception as e:
            logger.error(f"Failed to download video {video_id}: {str(e)}")


def download(clip_id: str, data_folder: Path, override_existing=False):
    if isinstance(clip_id, str):
        if not is_url(clip_id):
            url = [f"https://www.youtube.com/watch?v={clip_id}"]

        print(f"starting {url}")
        try:            
            if is_url(url):
                clip_id = get_youtube_id(url)

            if not clip_id:
                raise ValueError("Invalid YouTube URL or Video ID extraction failed.")

            video_path = Path(data_folder) / clip_id 
            if not override_existing and os.path.isdir(video_path):
                return clip_id

            download_video(
                video_id=clip_id,
                data_folder=data_folder,
            )
            
        except Exception as e:
            print(f"Failed to download video {clip_id}: {e}")
            
        print(f"done {clip_id}")

        return clip_id