import os
import json
from typing import List
import requests
from markdownify import markdownify as md

from .scraper import Scraper


class PostItem():
    base_url: str
    endpoint: str = '/wp/v2/posts'

    def __init__(self, base_url: str, id: int):
        self.base_url = base_url
        self.id = id
        self.scraper = Scraper(base_url + self.endpoint + '/' + str(self.id))

    def fetch(self):
        res = self.scrape()
        post = res.json()

        print(post['id'], post['title']['rendered'],
              post['date'], post['link'], post['slug'])

        excerpt = md(post['excerpt']['rendered'])
        content = md(post['content']['rendered'])

        print(content)

    def scrape(self, **kwargs):
        return self.scraper.scrape(**kwargs)

    def convert_html_to_markdown(self):
        print('convert to md')

    def save(self):
        print('save')


class PostList():
    base_url: str
    endpoint: str = '/wp/v2/posts'
    posts: List[PostItem] = []

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.scraper = Scraper(base_url + self.endpoint)

    def fetch(self, page=1, per_page=10):
        has_more_posts = True
        keys_wanted = {'id', 'excerpt', 'title',
                       'jetpack_sharing_enabled'
                       'jetpack_featured_media_url',
                       'tags',
                       'categories',
                       '_links',
                       'slug', 'link', 'date', 'content'}

        while has_more_posts:
            res = self.scrape(page=page, per_page=per_page)
            body = res.json()

            if res.status_code >= 400:
                has_more_posts = False
            else:
                if type(body) == list:
                    posts_in_page = [post for post in body]
                    all_keys = set(posts_in_page[0].keys())
                    unwanted_keys = all_keys - keys_wanted

                    for p in posts_in_page:
                        for k in list(unwanted_keys):
                            if k in p.keys():
                                del p[k]
                        self.posts.append(
                            PostItem(self.base_url, int(p['id']))
                        )

                page += 1

    def scrape(self, **kwargs):
        return self.scraper.scrape(**kwargs)
