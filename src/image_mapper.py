from bs4 import BeautifulSoup
import requests
import json
import copy
import os
import pprint as pp

from .util import clean_image_url

class ImageMapper():
    output_dir = 'public/images'
    output_file = 'public/images/graph.json'

    def process_featured_image(self, filename, featured_image_url: str):
        urls_map = dict()
        urls_map[featured_image_url] = {
            'original_url': clean_image_url(featured_image_url),
            'is_featured_image': True,
        }
        self.update_graph(urls_map)
        # self.download(filename, clean_image_url(featured_image_url))

    def process_html_images(self, html_content: str):
        parsed_html = BeautifulSoup(html_content, 'html.parser')
        images = parsed_html.find_all('img')
        urls_map = dict()

        for image in images:
            cleaned_url = clean_image_url(image['src'])
            urls_map[image['src']] = {
                'original_url': cleaned_url,
                'alt': image['alt'] if 'alt' in image else None,
                'title': image['title'] if 'title' in image else None,
                'is_featured_image': False,
            }
        
        self.update_graph(urls_map)

    def update_graph(self, new_data: dict):
        new_graph = copy.deepcopy(new_data)
        if os.path.isfile(os.path.join(os.getcwd(), self.output_file)) and os.path.getsize(os.path.join(os.getcwd(), self.output_file)) > 0:
          with open(os.path.join(os.getcwd(), self.output_file), 'r') as f:
              data = json.load(f)
              new_graph = data | new_data

        with open(os.path.join(os.getcwd(), self.output_file), 'w') as f:
            # dump new_graph JSON to file with pretty print format and utf-8 encoding
            json.dump(new_graph, f, indent=4, ensure_ascii=False)
    
    def process_graph(self, post: str):
        with open(os.path.join(os.getcwd(), self.output_file), 'r') as f:
            data = json.load(f)
        
        for key, value in data.items():
            if value['original_url'] in post:
                post = post.replace(value['original_url'], key)
        
        return post