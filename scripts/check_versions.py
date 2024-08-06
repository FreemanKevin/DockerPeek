import requests
import json
import os

def save_tags_to_json(image, tag_data):
    if not os.path.exists('data'):
        os.makedirs('data')
    filename = f"{image}_versions.json"
    filepath = os.path.join('data', filename)
    with open(filepath, 'w') as file:
        json.dump(tag_data, file, indent=4)

def get_docker_hub_tags(image):
    url = f"https://registry.hub.docker.com/v2/repositories/library/{image}/tags"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching data for {image}: {response.status_code} - {response.text}")
        return  # 终止当前镜像的处理

    data = response.json()
    
    if 'results' not in data:
        print(f"Missing 'results' in response data for {image}")
        return  # 终止当前镜像的处理

    valid_tags = []
    for result in data['results']:
        if 'latest' in result['name']:
            continue
        archs = [detail['architecture'] for detail in result['images']]
        if 'amd64' in archs and 'arm64' in archs:
            push_time = result['tag_last_pushed']
            push_date = push_time.split('T')[0].replace('-', '')
            tag_info = {
                'version': result['name'],
                'date': push_date,
                'architecture': 'x86 & arm64'
            }
            valid_tags.append(tag_info)
        
        if len(valid_tags) >= 10:
            break

    save_tags_to_json(image, valid_tags)

middlewares = ["nginx", "nacos", "redis", "elasticsearch", "minio", "rabbitmq", "geoserver"]
for middleware in middlewares:
    get_docker_hub_tags(middleware)