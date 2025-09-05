from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
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
            return True
        except Exception as e:
            logger.error(f"Failed to download video {video_id}: {str(e)}")
            return False


def download(clip_id: str, data_folder: Path, override_existing=False):
    """
    Downloads the YouTube video for the given clip_id.
    Returns clip_id if successful, None otherwise.
    """
    # Ensure input is video ID, not URL
    if is_url(clip_id):
        clip_id = get_youtube_id(clip_id)
        if not clip_id:
            logger.error("Invalid YouTube URL or video ID extraction failed.")
            return None
        
    video_path = Path(data_folder) / clip_id

    # Skip if already exists
    if video_path.is_dir() and not override_existing:
        logger.info(f"Already downloaded, skipping: {clip_id}")
        return clip_id

    logger.info(f"Starting download for clip: {clip_id}")

    # Try downloading
    success = download_video(clip_id, data_folder)

    if success:
        logger.info(f"Successfully downloaded: {clip_id}")
        return clip_id
    else:
        # Clean up partial download folder if exists
        if video_path.exists():
            shutil.rmtree(video_path, ignore_errors=True)
        return None