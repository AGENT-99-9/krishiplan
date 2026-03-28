from django.apps import AppConfig


import threading
import os
import sys

class AssistantConfig(AppConfig):
    name = 'assistant'

    def ready(self):
        # Prevent running twice or in migrations
        if 'runserver' not in sys.argv and 'gunicorn' not in sys.argv[0]:
            return
        
        # Avoid reloading during autoreload spawned processes unless it's the actual server
        if os.environ.get('RUN_MAIN', None) != 'true':
            # This is the outer process of runserver, skip loading here
            return

        from .views import _preload_rag
        print("🤖 [KrishiSaarthi] Django Startup: Initiating background load of SentenceTransformer / RAG Engine...")
        threading.Thread(target=_preload_rag, daemon=True, name="rag-preload-startup").start()
