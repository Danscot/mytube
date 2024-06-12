
from django.shortcuts import render

from googleapiclient.discovery import build

import yt_dlp


# Create your views here.

YOUTUBE_API_KEY = 'AIzaSyDV11sdmCCdyyToNU-XRFMbKgAA4IEDOS0'


def downloader(request):

    search_results = []

    links = []

    if request.method == 'POST':

        query = request.POST.get('query')

        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        search_response = youtube.search().list(

            q=query,

            part='snippet',

            maxResults=10

        ).execute()

        search_results = search_response.get('items', [])

    context = {

        'search_results': search_results
    }
    for video in search_results:
        video_id = video.get('id', {}).get('videoId')  # Use .get() to handle missing keys
        if video_id:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            download_url = get_video_download_url(video_url)
            video['download_url'] = download_url
        else:
            video['download_url'] = None
    return render(request, 'downloader.html', context)


def get_video_download_url(video_url):

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',

        'merge_output_format': 'mp4',  # Ensure the output is merged into an mp4 file
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info_dict = ydl.extract_info(video_url, download=False)

        formats = info_dict.get('formats', [])

        # Look for a format with both video and audio
        video_audio_format = [f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none']

        if video_audio_format:

            best_format = max(video_audio_format, key=lambda f: f.get('height', 0))

            return best_format.get('url')

        # If no combined format is found, find the best video and audio separately

        video_format = max([f for f in formats if f.get('vcodec') != 'none'], key=lambda f: f.get('height', 0),
                           default=None)
        audio_format = max([f for f in formats if f.get('acodec') != 'none'], key=lambda f: f.get('abr', 0),
                           default=None)

        if video_format and audio_format:

            video_url = video_format.get('url')

            audio_url = audio_format.get('url')

            return video_url, audio_url

        return None


