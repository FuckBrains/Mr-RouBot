# coding: utf-8
import os

"""
Ce fichier contien la class Config qui permet de récupérer les identifiants depuis Openshift ou en Local
"""


class Config:
    def __init__(self):
        pass

    @staticmethod
    def get_secret(name):
        """
        Permet de récupérer les identifiants depuis Openshift ou en Local
        """
        try:
            secrets = os.environ
            return secrets[name]
        except:
            from application.config.local_config import local_config
            return local_config[name]
