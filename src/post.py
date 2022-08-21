import os
import requests


def download_post():
    print("download post")


def download_all():
    req = requests.get(os.environ.get('BASE_URL'))

    req.close()
