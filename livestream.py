import json
import aiofiles
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz


# update file makes an update if we have a goal
async def update_file(all_games):
    print("starting update_file")
    async with aiofiles.open('data.json', 'r') as fcc_file:
        fcc_data = json.loads(await fcc_file.read())

    for i in all_games:
        matching_data = next((x for x in fcc_data if x.get("title") == i.get("title")), None)
        if matching_data:
            print(f"Found matching_data for {i['title']}: {matching_data}")
            if i.get("score_home") != matching_data.get("score_home") or i.get("score_away") != matching_data.get("score_away"):
                matching_data.update({
                    'score_home': '{}'.format(i.get("score_home")),
                    'score_away': '{}'.format(i.get("score_away")),
                })



#get m3u8

def main():
    m3u8_urls = []  # List to store M3U8 URLs and titles

    print("Starting get_webbrowser")
    with open('live_goals.json', 'r') as fcc_file:
        fcc_data = json.load(fcc_file)
        with ProcessPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
            futures = []
            for i in fcc_data:
                title = "{}-{}-{}.mp4".format(i["title"], i["score_home"], i["score_away"]).replace(" ", "")
                if i["stream"] != "None":
                    stream_game = i["stream"]
                    future = executor.submit(find_m3u8_url, title, stream_game)
                    futures.append(future)

            for future in futures:
                result = future.result()
                if result[0]:  # Check if a valid M3U8 URL was found
                    m3u8_urls.append(result)

    for url, title in m3u8_urls:
        save_goal(url, title)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(1)

