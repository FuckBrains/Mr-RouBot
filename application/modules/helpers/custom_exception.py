# -*- coding: utf-8 -*-
"""
Exceptions personnalisées.
"""


class EmptyDirException(Exception):
    """Empty directory exception"""
    def __init__(self):
        super(EmptyDirException, self).__init__('Aucun fichier présent dans le dossier')


class SshCmdException(Exception):
    """Empty directory exception"""
    def __init__(self):
        super(SshCmdException, self).__init__('Ssh cmd error: ')
