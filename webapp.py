# -*- encoding: utf-8 -*-
"""
Fichier à partir duquel sont lancés tous les cronjobs
"""

# python modules
import sys

# App modules
from application.modules.neo_youtuber.cron_jobs.job_neo_youtuber import job_neo_youtuber

if __name__ == '__main__':
    if str(sys.argv[1]) == "neo_youtuber":
        job_neo_youtuber()
