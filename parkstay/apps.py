from __future__ import unicode_literals

import os

from django.apps import AppConfig


class ParkstayConfig(AppConfig):
    name = 'parkstay'

    def ready(self):
        from django.conf import settings
        session_path = getattr(settings, 'SESSION_FILE_PATH', None)
        if session_path:
            try:
                os.makedirs(session_path, exist_ok=True)
            except PermissionError:
                fallback = os.path.join(settings.BASE_DIR, 'session_store')
                os.makedirs(fallback, exist_ok=True)
                settings.SESSION_FILE_PATH = fallback
