import re
import requests

def extract_segment_urls(m3u8_url):
    response = requests.get(m3u8_url)
    if response.status_code == 200:
        playlist_content = response.text
        segment_urls = re.findall(r'#EXTINF:\d+\.\d+,\s*\n([^\s]+\.ts)', playlist_content)
        return segment_urls
    else:
        print(f"Failed to fetch M3U8 playlist. Status code: {response.status_code}")
        return []

m3u8_url = "https://tens.rfbnassiahub.com/hls/71.m3u8?md5=iC7KwejTbP7qo1swAsuLRg&expires=1706020991"
segment_urls = extract_segment_urls(m3u8_url)

for url in segment_urls:
    print(url)
