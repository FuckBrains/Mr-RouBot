import os

import googleapiclient.discovery
import googleapiclient.errors

from google.oauth2.service_account import Credentials

from application.config.config import Config
from googleapiclient.http import MediaFileUpload


class YoutubeHelper:

    def __init__(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        self._api_service_name = "youtube"
        self._api_version = "v3"
        self._service_accpount_secrets = Config.get_secret("yt_json_credentials")
        self._credentials = Credentials.from_service_account_file(self._service_accpount_secrets)
        self.youtube = googleapiclient.discovery.build(self._api_service_name, self._api_version,
                                                       credentials=self._credentials)

    def upload_video(self, path_to_video):
        request = self.youtube.videos().insert(
            body={},
            # TODO: For this request to work, you must replace "YOUR_FILE"
            #       with a pointer to the actual file you are uploading.
            media_body=MediaFileUpload(path_to_video)
        )
        response = request.execute()

        print(response)
