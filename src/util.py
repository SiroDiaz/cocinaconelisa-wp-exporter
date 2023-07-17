import json
import os
import yaml
import requests

def read_metadata_from_mdx(mdx_file: str) -> dict:
    """
    Read metadata from mdx file
    """
    with open(mdx_file, 'r') as f:
        lines = f.readlines()
        metadata = yaml.safe_load(''.join(lines[1:lines.index('---\n', 1)]))
        return metadata


def get_content_from_mdx(mdx_file: str) -> str:
    """
    Get content from mdx file
    """
    with open(mdx_file, 'r') as f:
        lines = f.readlines()
        return ''.join(lines[lines.index('---\n', 1) + 1:])

def clean_image_url(image: str) -> str:
    """
    Clean image url
    """
    return image.split('?')[0]


def get_image_filename_from_url(image: str) -> str:
    """
    Get image filename from url
    """
    return image.split('/')[-1].split('?')[0]


def get_image_extension_from_filename(image: str) -> str:
    """
    Get image extension from filename
    """
    return image.split('.')[-1]

def replace_urls_in_md_file(md_file: str, urls_map: dict) -> None:
    """
    Replace urls in md file
    """
    with open(md_file, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            for cleaned_url, value in urls_map.items():
                if value['original_url'] in lines[i]:
                    lines[i] = lines[i].replace(value['original_url'], cleaned_url)
    
    with open(md_file, 'w') as f:
        f.writelines(lines)

def download_graph_images(graph: dict, output_path: str) -> None:
    """
    Download graph images
    """
    for key, value in graph.items():
        if os.path.exists(os.path.join(os.getcwd(), output_path, get_image_filename_from_url(value['original_url']))):
          print(f"File {get_image_filename_from_url(value['original_url'])} already exists")
          continue

        if value['is_featured_image']:
              download(os.path.join(os.getcwd(), output_path, get_image_filename_from_url(value['original_url'])), key)
        else:
            download(os.path.join(os.getcwd(), output_path, get_image_filename_from_url(value['original_url'])), key)


def download(filename: str, img_src: str) -> None:
    """
    Download image
    """
    r = requests.get(img_src, allow_redirects=True)
    
    with open(os.path.join(os.getcwd(), filename), 'wb') as f:
        f.write(r.content)
