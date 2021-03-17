import logging

from application.config.config import Config
from application.modules.helpers.custom_exception import NoNewYoutubeVideo
from application.modules.helpers.mail_helper import MailHelper
from application.modules.helpers.youtube_helper import YoutubeHelper
from application.modules.neo_youtuber.neo_youtuber import NeoYoutuber


def job_neo_youtuber():
    neo_youtuber = NeoYoutuber()
    youtube = YoutubeHelper()

    try:

        neo_youtuber.get_last_video_url_and_title(youtube_helper=youtube)
        neo_youtuber.check_if_video_already_exist()

        if not neo_youtuber.is_new_video:
            raise NoNewYoutubeVideo

        neo_youtuber.retreive_last_video()
        neo_youtuber.retreive_thumbnail()
        neo_youtuber.cut_and_create_new_video()
        neo_youtuber.create_new_thumbnail()
        neo_youtuber.upload_to_youtuber()

    except NoNewYoutubeVideo as e:
        logging.warning(e)
    except Exception as e:
        logging.warning(e)

    mail_helper = MailHelper(receiver_email=Config.get_secret("RECEIVER_EMAIL"), subject=neo_youtuber.mail_subject)
    mail_helper.is_ok = neo_youtuber.is_job_success
    mail_helper.send_mail()
