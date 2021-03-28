import logging

from application.config.config import Config
from application.modules.helpers.mail_helper import MailHelper
from application.modules.helpers.youtube_helper import YoutubeHelper
from application.modules.neo_youtuber.neo_youtuber import NeoYoutuber


def job_neo_youtuber(number_of_videos_to_retrievse: int = None):
    neo_youtuber = NeoYoutuber()
    youtube = YoutubeHelper()

    if number_of_videos_to_retrievse is not None:
        neo_youtuber.max_search_result = number_of_videos_to_retrievse

    try:
        neo_youtuber.search_videos(youtube_helper=youtube)

        for item_number in range(neo_youtuber.max_search_result):
            neo_youtuber.get_last_video_url_and_title(item_number=item_number)
            neo_youtuber.check_if_video_already_exist()

            if not neo_youtuber.is_new_video:
                continue

            neo_youtuber.retreive_last_video()
            neo_youtuber.cut_video_by_scenes()
            neo_youtuber.shuffle_and_create_new_video()
            neo_youtuber.create_new_thumbnail()
            neo_youtuber.upload_to_youtuber()
            neo_youtuber.update_database()

    except Exception as e:
        logging.error(e)

    mail_helper = MailHelper(receiver_email=Config.get_secret("RECEIVER_EMAIL"), subject=neo_youtuber.mail_subject)
    mail_helper.is_ok = neo_youtuber.is_job_success
    mail_helper.send_mail()
