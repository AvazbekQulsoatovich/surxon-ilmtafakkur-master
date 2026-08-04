import os
import sys

from django.core.management import execute_from_command_line


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.stdout = open(os.path.join(BASE_DIR, "runserver.log"), "a", encoding="utf-8")
sys.stderr = open(os.path.join(BASE_DIR, "runserver.err.log"), "a", encoding="utf-8")

os.chdir(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

execute_from_command_line([
    "manage.py",
    "runserver",
    "127.0.0.1:8000",
    "--noreload",
])
