import json
import logging
import os
import glob
import random
from PIL import Image, ImageDraw, ImageFont

import pytube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import concatenate_videoclips, VideoFileClip

from application.config.config import Config
from application.modules.base_module.base_module import BaseModule
from application.modules.helpers.utils import find_scenes, to_secondes
from application.modules.helpers.youtube_helper import YoutubeHelper
from application.modules.helpers.json_database import JsonDatabase


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
        self.path_to_cutted_videos = f"{self.path_to_elements}/cutted_videos"
        self.path_to_final_result_videos = f"{self.path_to_elements}/final_result_videos"
        self.path_to_cat_dog_dataset = f"{self.path_to_elements}/cat_dog_dataset/PetImages"
        self.path_to_intro = f"{self.path_to_elements}/intro_outro"
        self.yt_id_to_steal_from = "UCzn2gx8zzhF0A4Utk8TEDNQ"
        self.yt_url_to_steal_from = "https://www.youtube.com/channel/UCzn2gx8zzhF0A4Utk8TEDNQ"
        self.yt_api_key = Config.get_secret("yt_api_key")
        self.database = None
        self.number_of_scenes = 0
        self.cutted_videos = []
        self.database_table_name = "neo_youtuber.json"
        self.max_search_result = 1
        self.search_response = None

    def search_videos(self, youtube_helper: YoutubeHelper):
        try:
            request = youtube_helper.youtube.search().list(
                part="snippet",
                maxResults=self.max_search_result,
                channelId=self.yt_id_to_steal_from,
                order="date"
            )
            self.search_response = request.execute()
            print('search_videos: DONE')
        except Exception as e:
            logging.error(e)

    def get_last_video_url_and_title(self, item_number: int):
        try:
            self.last_video_title = self.search_response.get('items')[item_number].get('snippet').get('title')
            self.last_video_id = self.search_response.get('items')[item_number].get('id').get('videoId')
            self.last_video_url = f"https://www.youtube.com/watch?v={self.last_video_id}"
            self.thumbnail_url = self.search_response.get('items')[item_number].get('snippet').get('thumbnails').get('high').get('url')
            print('get_last_video_url_and_title: DONE')
        except Exception as e:
            logging.error(e)

    def check_if_video_already_exist(self):
        try:
            data = JsonDatabase.retrieve_database(json_file=self.database_table_name)
            if self.last_video_id not in data.get('neo_youtuber').get('all_added_videos'):
                self.is_new_video = True
            print('check_if_video_already_exist: DONE')
        except Exception as e:
            logging.error(e)

    def retreive_last_video(self):
        try:
            py_youtube = pytube.YouTube(self.last_video_url)
            video = py_youtube.streams.get_highest_resolution()
            video.download(self.path_to_videos, filename=self.last_video_id)
            print('retreive_last_video: DONE')
        except Exception as e:
            logging.error(e)

    def cut_video_by_scenes(self):
        try:
            scenes = find_scenes(video_path=f"{self.path_to_videos}/{self.last_video_id}.mp4", threshold=50.0)
            self.number_of_scenes = len(scenes[5:-5])
            for index, scene in enumerate(scenes[5:-5]):
                start_scene_seconds = to_secondes(time=str(scene[0]), time_format="%H:%M:%S.%f")
                end_scene_seconds = to_secondes(time=str(scene[1]), time_format="%H:%M:%S.%f")
                if int(end_scene_seconds) - int(start_scene_seconds) < 15:
                    continue
                # Enlever les deux premières secondes pour corriger les erreurs de cuts
                start_scene_seconds = start_scene_seconds + 2
                ffmpeg_extract_subclip(filename=f"{self.path_to_videos}/{self.last_video_id}.mp4",
                                       t1=start_scene_seconds, t2=end_scene_seconds,
                                       targetname=f"{self.path_to_cutted_videos}/{self.last_video_id}_{index}.mp4")
                self.cutted_videos.append(f"{self.last_video_id}_{index}")
            print('cut_video_by_scenes: DONE')
        except Exception as e:
            logging.error(e)

    def shuffle_and_create_new_video(self):
        try:
            clips = [VideoFileClip(f"{self.path_to_intro}/intro.mp4")]
            shuffled_sub_videos = random.sample(self.cutted_videos, len(self.cutted_videos))
            for sub_video in shuffled_sub_videos:
                clips.append(VideoFileClip(f"{self.path_to_cutted_videos}/{sub_video}.mp4",
                                           target_resolution=(1920, 1080)))
            final_result_video = concatenate_videoclips(clips=clips)
            final_result_video.write_videofile(f"{self.path_to_final_result_videos}/new_{self.last_video_id}.mp4",
                                               fps=30)
            print('shuffle_and_create_new_video: DONE')
        except Exception as e:
            logging.error(e)

    def create_new_thumbnail(self):
        cat_or_dog = random.choice(['Cat', 'Dog'])
        images = glob.glob(f"{self.path_to_cat_dog_dataset}/{cat_or_dog}/*.jpg")
        thumbnail = random.choice(images)
        thumbnail_img = Image.open(thumbnail)
        width, height = thumbnail_img.size
        draw = ImageDraw.Draw(thumbnail_img)
        # font = ImageFont.truetype(<font-file>, <font-size>)
        font = ImageFont.truetype(f"{os.getcwd()}/application/static/fonts/newsserifbold.ttf", 30)
        # draw.text((x, y),"Sample Text",(r,g,b))
        rect_color = "#fca311"
        text_color = "#14213d"
        draw.rectangle(((20, height-52), (470, height-25)), fill="#e5e5e5")
        draw.rectangle(((0, 0), (10, height)), fill=rect_color)
        draw.rectangle(((0, 0), (width, 10)), fill=rect_color)
        draw.rectangle(((width, 0), (width-10, height)), fill=rect_color)
        draw.rectangle(((0, height), (width, height - 10)), fill=rect_color)

        data = JsonDatabase.retrieve_database(json_file=self.database_table_name)
        data.get('neo_youtuber')['thumbnail_number'] += 1
        draw.text((30, height-50), f"FUNNY TIKTOK ANIMALS #{data.get('neo_youtuber').get('thumbnail_number')}",
                  text_color, font=font)
        thumbnail_img.save(f"{self.path_to_thumbnails}/{data.get('neo_youtuber').get('thumbnail_number')}.jpg")

        with open(f'{os.getcwd()}/roubot_dabatase.json', 'w') as database:
            json.dump(data, database)

        print('create_new_thumbnail: DONE')

    def upload_to_youtuber(self):
        print("Upload not implemented yet")

    def update_database(self):
        try:
            data = JsonDatabase.retrieve_database(json_file=self.database_table_name)
            data.get('neo_youtuber').get('all_added_videos').append(self.last_video_id)
            data.get('neo_youtuber')['thumbnail_number'] += 1
            JsonDatabase.update_database(data=data, json_file=self.database_table_name)
            self.is_new_video = False
        except Exception as e:
            logging.error(e)
