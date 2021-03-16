"""
Class générique utilisable pour les connexions FTP
"""
import os
from ftplib import FTP_TLS
from application.config.config import Config


class FtpHelper:
    def __init__(self, host, port, user, password):
        self.ftp = FTP_TLS()
        self.ftp.connect(host=host, port=int(port))
        self.ftp.login(user=user, passwd=password)
        self.ftp.prot_p()

    def list_files(self, path=None):
        """
        Lister les fichiers présents dans un dossier
        Parameters
        ----------
        path: Path vers le dossier

        Return Liste des fichier présents dans le dossier
        -------
        """
        if Config.get_secret('WORKING_ENV') == 'LOCAL':
            return [file for file in os.listdir(Config.get_secret('ZIP_FILES_PATH'))]
        files = []
        if path is not None:
            self.ftp.cwd(path)
        self.ftp.dir(files.append)
        return [filename.split(' ')[-1] for filename in files]
