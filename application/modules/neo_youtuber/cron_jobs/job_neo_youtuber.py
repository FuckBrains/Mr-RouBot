import logging

from application.config.config import Config
from application.modules.helpers.custom_exception import NoYoutubeVideo
from application.modules.helpers.mail_helper import MailHelper
from application.modules.neo_youtuber.neo_youtuber import NeoYoutuber


def job_neo_youtuber():
    neo_youtuber = NeoYoutuber()

    try:

        neo_youtuber.retreive_last_video()

        if neo_youtuber.last_video_title is None:
            raise NoYoutubeVideo

        neo_youtuber.retreive_thumbnail()
        neo_youtuber.cut_and_create_new_video()
        neo_youtuber.create_new_thumbnail()
        neo_youtuber.upload_to_youtuber()

    except NoYoutubeVideo as e:
        logging.info(e)
    except Exception as e:
        logging.info(e)

    mail_helper = MailHelper(receiver_email=Config.get_secret("RECEIVER_EMAIL"), subject=neo_youtuber.mail_subject)
    mail_helper.is_ok = neo_youtuber.is_job_success
    mail_helper.send_mail()
