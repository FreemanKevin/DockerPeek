import requests
import json
import os
import re

def save_tags_to_json(image, tag_data):
    if not os.path.exists('data'):
        os.makedirs('data')
    filename = f"{image}_versions.json"
    filepath = os.path.join('data', filename)
    with open(filepath, 'w') as file:
        json.dump(tag_data, file, indent=4)

def get_docker_hub_tags(image, pattern):
    url = f"https://registry.hub.docker.com/v2/repositories/library/{image}/tags"
    valid_tags = []
    
    while url and len(valid_tags) < 10:  # Ensure we only collect up to 10 tags
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error fetching data for {image}: {response.status_code} - {response.text}")
            return  # 终止当前镜像的处理

        data = response.json()
        
        if 'results' not in data:
            print(f"Missing 'results' in response data for {image}")
            return  # 终止当前镜像的处理

        for result in data['results']:
            tag_name = result['name']
            if 'latest' in tag_name:
                continue
            if re.match(pattern, tag_name):
                archs = [detail['architecture'] for detail in result['images'] if 'architecture' in detail]
                if 'amd64' in archs and 'arm64' in archs:
                    push_time = result['tag_last_pushed']
                    push_date = push_time.split('T')[0].replace('-', '')
                    tag_info = {
                        'version': tag_name,
                        'date': push_date,
                        'architecture': 'x86 & arm64'
                    }
                    valid_tags.append(tag_info)
        
        url = data.get('next')  # Proceed to the next page if exists

    save_tags_to_json(image, valid_tags)

# 定义镜像及其版本匹配规则
image_patterns = {
    "nginx": r"^1\.\d+\.\d+$",
    "elasticsearch": r"^v8\.\d+\.\d+$",
    "nacos/nacos-server": r"^v2\.\d+\.\d+(?:\.\d+)?$",
    "minio/minio": r"^RELEASE\.202[4-9]-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$",
    "rabbitmq": r"^v?[3-9]\.\d+\.\d+-management-alpine$",
    "redis": r"^v?7\.\d+\.\d+$",
    "oscarfonts/geoserver": r"^v?3\.\d+\.\d+$"  # Assuming a similar pattern for geoserver
}

middlewares = ["nginx", "nacos/nacos-server", "redis", "elasticsearch", "minio/minio", "rabbitmq", "oscarfonts/geoserver"]
for middleware in middlewares:
    pattern = image_patterns.get(middleware.split('/')[0], r".*")  # default to any if specific not found
    get_docker_hub_tags(middleware, pattern)