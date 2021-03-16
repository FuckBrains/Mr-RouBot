"""
Class générique à utiliser pour l'envoi de mails
"""

import os
import smtplib
from application.config.config import Config
from email.mime.text import MIMEText


class MailHelper:
    def __init__(self, receiver_email, subject):
        self.smtp_server = Config.get_secret("SMTP_SERVER")
        self.sender_email = Config.get_secret("SENDER_EMAIL")
        if Config.get_secret("WORKING_ENV") == "PROD":
            self.server = smtplib.SMTP(self.smtp_server)
        self.receiver_email = receiver_email
        self.subject = subject
        self.is_ok = True

    def create_mail(self):
        """
        Crétion de la structure du mail à envoyer en utilisant les template html
        --------------
        return: html_content: Objet contenant toutes les informations nécessaire du mail
        """
        file_dir = os.path.dirname(os.path.realpath('__file__'))
        if self.is_ok:
            html = open(os.path.join(file_dir, 'application/static/email/email-ok.html'), encoding='utf-8')
            html_content = MIMEText(html.read(), 'html')
            html_content["Subject"] = f"{self.subject}[{Config.get_secret('WORKING_ENV')}] - OK"
        else:
            html = open(os.path.join(file_dir, 'application/static/email/email-ko.html'), encoding='utf-8')
            html_content = MIMEText(html.read(), 'html')
            html_content["Subject"] = f"{self.subject}[{Config.get_secret('WORKING_ENV')}] - KO"
        html_content["From"] = self.sender_email
        html_content["To"] = self.receiver_email
        html.close()
        return html_content

    def send_mail(self):
        """
        Envoi du mail et fermeture du serveur.
        """
        try:
            # Todo à utiliser plutard en prod ("python -m smtpd -c DebuggingServer -n localhost:1025")
            if Config.get_secret("WORKING_ENV") == "PROD":
                self.server.sendmail(self.sender_email, self.receiver_email.split(','), self.create_mail().as_string())
        except Exception as e:
            # Print any error messages to stdout
            print(f"Probleme lors de l'envoi du mail: {e}")
