import os
import json
import yaml
from typing import List
from urllib.parse import urlparse
from markdownify import markdownify as md

from .scraper import Scraper
from .image_mapper import ImageMapper
from .util import download_graph_images, get_image_filename_from_url

class PostItem():
    base_url: str
    endpoint: str = '/wp/v2/posts'
    metadata: dict = {}

    def __init__(self, base_url: str, id: int):
        self.base_url = base_url
        self.id = id
        self.scraper = Scraper(base_url + self.endpoint + '/' + str(self.id))

    def fetch(self):
        res = self.scrape()
        post = res.json()

        excerpt = md(post['excerpt']['rendered'])
        
        return {
            'id': post['id'],
            'title': post['title']['rendered'],
            'date': post['date'],
            'link': post['link'],
            'featured_image': post['jetpack_featured_media_url'],
            'slug': post['slug'],
            'categories': post['categories'],
            'excerpt': excerpt,
            'html_content': post['content']['rendered'],
        }

    def scrape(self, **kwargs):
        return self.scraper.scrape(**kwargs)

    def save_to_file(self):
        data = self.fetch()
        filename = f"{data['slug']}.mdx"
        filepath = os.path.join(os.getcwd(), 'output', 'posts', filename)

        yml_wanted_attrs = ['title', 'date', 'link', 'slug', 'featured_image', ]
        filtered_data = {k: v for k, v in data.items() if k in yml_wanted_attrs}

        featured_image_format = urlparse(filtered_data['featured_image']).path.split('.')[-1]
        image_mapper = ImageMapper()
        
        image_mapper.process_html_images(data['html_content'])
        image_mapper.process_featured_image(f"{data['slug']}.{featured_image_format}", data['featured_image'])

        # write markdown content
        md_rendered = md(image_mapper.process_graph(data['html_content']))
        self.metadata = filtered_data
        metadata = yaml.safe_dump(filtered_data, allow_unicode=True)

        f = open(filepath, 'w', encoding='utf-8')
        f.write('---\n')
        f.write(f"{metadata}")
        f.write("---\n\n")
        f.write(md_rendered)
        f.close()

    def replace_urls_in_md_file(self):
        image_mapper = ImageMapper()
        print(self.metadata['slug'])
        with open(image_mapper.output_file, 'r') as f:
            graph = json.load(f)

        mdx_content = ''

        with open(os.path.join(os.getcwd(), 'output', 'posts', f"{self.metadata['slug']}.mdx"), 'r', encoding='utf-8') as f:
            mdx_content = f.read()
            
            for key, value in graph.items():
                print(f"Replacing {key} with /images/{get_image_filename_from_url(value['original_url'])}")
                mdx_content = mdx_content.replace(
                    key,
                    '/images/' + get_image_filename_from_url(value['original_url']),
                )

            f = open(os.path.join(os.getcwd(), 'output', 'posts', f"{self.metadata['slug']}.mdx"), 'w', encoding='utf-8')
            f.write(mdx_content)
            f.close()

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

def download_images():
        image_mapper = ImageMapper()
        with open(image_mapper.output_file, 'r') as f:
            download_graph_images(json.load(f), image_mapper.output_dir)
