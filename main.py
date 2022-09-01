import os
from dotenv import load_dotenv

from src.post import PostList

if __name__ == '__main__':
    load_dotenv()

    post_list = PostList(str(os.environ.get('BASE_URL')))
    post_list.fetch()

    posts = post_list.posts

    for post in posts:
        if post.id == 4:
            print(f"fetching POST with ID {post.id}")
            post.fetch()
