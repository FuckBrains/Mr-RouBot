from application.config.config import Config
from application.modules.base_module.base_module import BaseModule
import pytube


class NeoYoutuber(BaseModule):
    def __init__(self):
        super().__init__(job_name="Neo_Youtuber")
        self.mail_subject = [self.job_name]
        self.last_video_title = None
        self.path_to_videos = f"{self.path_to_elements}/videos"
        self.path_to_thumbnails = f"{self.path_to_elements}/thumbnails"
        self.yt_id_to_steal_from = "UCzn2gx8zzhF0A4Utk8TEDNQ"
        self.yt_url_to_steal_from = "https://www.youtube.com/channel/UCzn2gx8zzhF0A4Utk8TEDNQ"
        self.yt_api_key = Config.get_secret("yt_api_key")

    def get_last_video_url(self):
        return ''

    def retreive_last_video(self):
        youtube = pytube.YouTube(self.get_last_video_url())

    def cut_and_create_new_video(self):
        pass

    def upload_to_youtuber(self):
        pass

    def retreive_thumbnail(self):
        pass

    def create_new_thumbnail(self):
        pass

