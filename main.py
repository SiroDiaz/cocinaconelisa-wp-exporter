import os
from dotenv import load_dotenv

from src.post import PostList, download_images

if __name__ == '__main__':
    load_dotenv()

    post_list = PostList(str(os.environ.get('BASE_URL')))
    post_list.fetch()

    posts = post_list.posts

    for post in posts:
        post.save_to_file()

    download_images()
    
    for post in posts:
        post.replace_urls_in_md_file()

