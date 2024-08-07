import requests
import json
import os
import re

def save_tags_to_json(image, tag_data):
    if not os.path.exists('data'):
        os.makedirs('data')
    filename = f"{image.split('/')[-1]}_versions.json"
    filepath = os.path.join('data', filename)
    with open(filepath, 'w') as file:
        json.dump(tag_data, file, indent=4)

def fetch_docker_tags(url, image):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 触发异常，如果HTTP状态码表明有错误
        return response.json()
    except requests.exceptions.HTTPError as errh:
        return None  # 返回 None 在错误时
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException:
        return None

def get_docker_hub_tags(image, pattern):
    if '/' in image:
        url = f"https://registry.hub.docker.com/v2/repositories/{image}/tags"
    else:
        url = f"https://registry.hub.docker.com/v2/repositories/library/{image}/tags"

    valid_tags = []
    
    while url and len(valid_tags) < 10:
        data = fetch_docker_tags(url, image)
        if not data:
            return
        
        if 'results' not in data:
            return

        for result in data['results']:
            tag_name = result['name']
            if 'latest' in tag_name:
                continue
            if re.match(pattern, tag_name):
                archs = set(detail['architecture'] for detail in result['images'] if 'architecture' in detail)
                if 'amd64' in archs and 'arm64' in archs:
                    architecture = 'x86 & arm64'
                elif 'amd64' in archs:
                    architecture = 'x86'
                else:
                    architecture = 'unknown'

                push_time = result['tag_last_pushed']
                push_date = push_time.split('T')[0].replace('-', '')
                tag_info = {
                    'version': tag_name,
                    'date': push_date,
                    'architecture': architecture
                }
                valid_tags.append(tag_info)
        
        url = data.get('next')

    save_tags_to_json(image, valid_tags)

image_patterns = {
    "nginx": r"^1\.\d+\.\d+$",
    "elasticsearch": r"^([8-9]|\d{2,})\.\d+\.\d+$",
    "nacos/nacos-server": r"^v2\.\d+\.\d+.*$",
    "minio/minio": r"^RELEASE\.202[4-9]-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$",
    "rabbitmq": r"^v?[3-9]\.\d+\.\d+-management-alpine$",
    "redis": r"^v?7\.\d+\.\d+$",
    "oscarfonts/geoserver": r".*"
}

middlewares = ["nginx", "nacos/nacos-server", "redis", "elasticsearch", "minio/minio", "rabbitmq", "oscarfonts/geoserver"]
for middleware in middlewares:
    pattern = image_patterns.get(middleware, r".*")
    get_docker_hub_tags(middleware, pattern)