import json
from urllib.parse import urlparse
import requests

subscription_key = ''
vision_base_url = "https://eastus.api.cognitive.microsoft.com/vision/v2.0/"
analyze_url = vision_base_url + "describe"

reddit_url = 'https://www.reddit.com/r/ArchitecturePorn/.json?limit=20'
response = requests.get(reddit_url, headers={'User-agent': 'your-bot-name 0.1'})
if not response.ok:
    print("Error", response.status_code)
    exit()

url_list = []
data = response.json()['data']['children']
for post in data:
    url = post['data']['url']
    url_list.append(url)

print(url_list)


# Set image_url to the URL of an image that you want to analyze.

def print_caption(sub_key, analyze_url, image_url):
    headers = {'Ocp-Apim-Subscription-Key': sub_key}
    params = {'maxCandidates': '1', 'language': 'en'}
    content = {'url': image_url}
    response = requests.post(analyze_url, headers=headers,
                             params=params, json=content)
    response.raise_for_status()

    # The 'analysis' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    analysis = response.json()
    try:
        image_caption = analysis["description"]["captions"][0]['text'].capitalize()
        image_tags = analysis["description"]["tags"]
        print(image_caption + ": " + image_url + '\n')
    except IndexError as e:
        print(e)


for url in url_list:
    try:
        print_caption(subscription_key, analyze_url, url)
    except requests.exceptions.HTTPError as e:
        continue
