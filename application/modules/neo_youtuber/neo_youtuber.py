import json
import logging
import os
import requests
import urllib.request
import pytube

from application.config.config import Config
from application.modules.base_module.base_module import BaseModule
from application.modules.helpers.youtube_helper import YoutubeHelper


class NeoYoutuber(BaseModule):
    def __init__(self):
        super().__init__(job_name="Neo_Youtuber")
        self.is_new_video = False
        self.mail_subject = [self.job_name]
        self.last_video_title = None
        self.last_video_id = None
        self.last_video_url = None
        self.thumbnail_url = None
        self.path_to_videos = f"{self.path_to_elements}/videos"
        self.path_to_thumbnails = f"{self.path_to_elements}/thumbnails"
        self.yt_id_to_steal_from = "UCzn2gx8zzhF0A4Utk8TEDNQ"
        self.yt_url_to_steal_from = "https://www.youtube.com/channel/UCzn2gx8zzhF0A4Utk8TEDNQ"
        self.yt_api_key = Config.get_secret("yt_api_key")
        self.database = None

    def get_last_video_url_and_title(self, youtube_helper: YoutubeHelper):
        try:
            request = youtube_helper.youtube.search().list(
                part="snippet",
                maxResults=1,
                channelId=self.yt_id_to_steal_from,
                order="date"
            )
            response = request.execute()
            self.last_video_title = response.get('items')[0].get('snippet').get('title')
            self.last_video_id = response.get('items')[0].get('id').get('videoId')
            self.last_video_url = f"https://www.youtube.com/watch?v={self.last_video_id}"
            self.thumbnail_url = response.get('items')[0].get('snippet').get('thumbnails').get('high').get('url')
            print('get_last_video_url_and_title')
        except Exception as e:
            logging.error(e)

    def check_if_video_already_exist(self):
        try:
            with open(f'{os.getcwd()}/roubot_dabatase.json') as database:
                data = json.load(database)
                if self.last_video_id not in data.get('neo_youtuber').get('all_added_videos'):
                    self.is_new_video = True
            print('check_if_video_already_exist')
        except Exception as e:
            logging.error(e)

    def retreive_thumbnail(self):
        try:
            urllib.request.urlretrieve(self.thumbnail_url, f"{self.path_to_thumbnails}/{self.last_video_id}.jpg")
        except Exception as e:
            logging.error(e)

    def retreive_last_video(self):
        try:
            py_youtube = pytube.YouTube(self.last_video_url)
            video = py_youtube.streams.get_highest_resolution()
            video.download(self.path_to_videos, filename=self.last_video_id)
            print('retreive_last_video')
        except Exception as e:
            logging.error(e)

    def cut_and_create_new_video(self):
        pass

    def upload_to_youtuber(self):
        pass

    def create_new_thumbnail(self):
        pass


