from dotenv import load_dotenv

from src.post import download_post

if __name__ == '__main__':
	load_dotenv()
    print('hello world!')
    download_post()
