# -*- coding: utf-8 -*-
"""
Exceptions personnalisées.
"""


class EmptyDirException(Exception):
    """Empty directory exception"""
    def __init__(self):
        super(EmptyDirException, self).__init__('Aucun fichier présent dans le dossier')


class NoYoutubeVideo(Exception):
    """Empty directory exception"""
    def __init__(self):
        super(NoYoutubeVideo, self).__init__('Aucune nouvelle vidéo à créer')
