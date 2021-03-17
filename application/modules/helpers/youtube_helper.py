import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.service_account import Credentials

from application.config.config import Config


class YoutubeHelper:
    def __init__(self):
        self._api_service_name = "youtube"
        self._api_version = "v3"
        self._service_accpount_secrets = Config.get_secret("yt_json_credentials")
        self._scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        self._credentials = Credentials.from_service_account_file(self._service_accpount_secrets)
        self.youtube = googleapiclient.discovery.build(self._api_service_name, self._api_version,
                                                       credentials=self._credentials)
