import json
import aiofiles
import requests
from bs4 import BeautifulSoup


async def get_url_games(title):
    existing_stream = await check_title_in_file(title)
    base_url = "https://bingsport.xyz/"

    if existing_stream:
        print("Already have this stream")
        return existing_stream
    else:
        response = requests.get("https://bingsport.xyz/football")

        bsoup = BeautifulSoup(response.text, 'html.parser')

        live_stream_elements = bsoup.find_all(class_='list-match-sport-live-stream')

        for live_stream in live_stream_elements:
            a_link = live_stream.find('a')
            link = base_url + a_link.get("href")
            url_link = a_link.get("href")
            if len(url_link.split("/")) == 3:
                http_split = url_link.split("/")[2]
                if "vs" in http_split:
                    split_name = http_split.split("vs")[0].replace('_', " ")
                    team_name = split_name.strip()
                    bing = team_name.lower()
                    livescore = title.lower()
                    if bing in livescore:
                        print("Getting a new game stream")
                        return link
            else:
                pass


async def check_title_in_file(title_to_check):
    async with aiofiles.open('data.json', 'r') as fcc_file:
        fcc_data = json.loads(await fcc_file.read())

    if not fcc_data:
        return None

    for dictionary in fcc_data:
        if title_to_check in dictionary.get("title") and dictionary.get("stream") is not None:
            return dictionary.get("stream")

    return None