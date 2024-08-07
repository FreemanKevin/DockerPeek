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
        response.raise_for_status()  # 觸發異常，如果HTTP狀態代碼表明有錯誤
        print("DEBUG: Response Headers:", response.headers)
        print("DEBUG: Response Body:", response.json())  # 假設返回的是JSON格式
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print("DEBUG: HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("DEBUG: Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("DEBUG: Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("DEBUG: Oops: Something Else", err)
        return None  # 返回 None 在錯誤時

def get_docker_hub_tags(image, pattern):
    if '/' in image:
        url = f"https://registry.hub.docker.com/v2/repositories/{image}/tags"
    else:
        url = f"https://registry.hub.docker.com/v2/repositories/library/{image}/tags"

    valid_tags = []
    
    while url and len(valid_tags) < 10:
        data = fetch_docker_tags(url, image)  # 使用新的 fetch_docker_tags 函數
        if not data:
            print(f"DEBUG: Failed to fetch data for {image}")
            return
        
        if 'results' not in data:
            print(f"DEBUG: Missing 'results' in response data for {image}")
            return

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