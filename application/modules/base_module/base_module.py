from application.config.config import Config


class BaseModule:
    def __init__(self, job_name):
        self.job_name = job_name
        self.path_to_elements = Config.get_secret(f"Path_Elements_{self.job_name}")
        self.is_job_success = True
