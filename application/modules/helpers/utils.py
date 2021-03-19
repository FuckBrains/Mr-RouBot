import datetime
import logging

from scenedetect import VideoManager
from scenedetect import SceneManager

from scenedetect.detectors import ContentDetector


def find_scenes(video_path, threshold=30.0):
    try:
        # Create our video & scene managers, then add the detector.
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(
            ContentDetector(threshold=threshold))

        # Improve processing speed by downscaling before processing.
        video_manager.set_downscale_factor()

        # Start the video manager and perform the scene detection.
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)

        # Each returned scene is a tuple of the (start, end) timecode.
        return scene_manager.get_scene_list()
    except Exception as e:
        logging.error(e)


def to_secondes(time: str, time_format: str):
    try:
        time_scene = datetime.datetime.strptime(time, time_format)
        time_seconds = (60 * time_scene.minute) + (60 * 60 * time_scene.hour) + time_scene.second
        return time_seconds
    except Exception as e:
        logging.error(e)
