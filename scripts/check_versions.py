import requests
import json
import os

def save_tags_to_json(image, tag_data):
    # 确保 data 目录存在
    if not os.path.exists('data'):
        os.makedirs('data')

    # 根据镜像名称生成文件名
    filename = f"{image}_version.json"
    filepath = os.path.join('data', filename)

    # 写入 JSON 文件
    with open(filepath, 'w') as file:
        json.dump(tag_data, file, indent=4)

def get_docker_hub_tags(image):
    url = f"https://registry.hub.docker.com/v2/repositories/library/{image}/tags"
    response = requests.get(url)
    data = response.json()

    # 过滤出包含 x86 和 arm64 的 tags，排除 latest
    valid_tags = []
    for result in data['results']:
        if 'latest' in result['name']:
            continue

        # 检查是否支持 x86 和 arm64
        archs = [detail['architecture'] for detail in result['images']]
        if 'amd64' in archs and 'arm64' in archs:
            # 获取发布日期
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

# 中间件列表
middlewares = ["nginx", "nacos", "redis", "elasticsearch", "minio", "rabbitmq", "geoserver"]
for middleware in middlewares:
    get_docker_hub_tags(middleware)