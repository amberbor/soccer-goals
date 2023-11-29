import os
from datetime import datetime
from seleniumwire import webdriver
import aiofiles
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import requests
import json
import asyncio

from get_m3u8 import LivestreamCapturer


class LivescoreScraper:
    def __init__(self):
        self.driver = None
        self.today_date = datetime.today().strftime('%Y-%m-%d')
        self.file_path = os.path.join("games", f"{self.today_date}.json")
        self.scheduler = None

    async def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    async def stop_driver(self):
        if self.driver:
            self.driver.quit()

    async def get_today_matches(self):
        try:
            await self.start_driver()
            self.driver.get("https://www.livescores.com/?tz=1")

            while True:
                page_source = self.driver.page_source
                bsoup = BeautifulSoup(page_source, 'html.parser')

                match_elements = bsoup.find_all('div', class_='If Mf')

                all_games = []

                for match in match_elements:
                    match_time = match.select_one('.kj .Eg').text
                    home_team_name = match.select_one('.kj .oj .pj').text
                    home_team_score = match.select_one('.kj .oj .mj .uj').text
                    away_team_name = match.select_one('.kj .oj .qj').text
                    away_team_score = match.select_one('.kj .oj .mj .vj').text

                    game = {
                        "title": f"{home_team_name} vs {away_team_name}",
                        "score_home": home_team_score,
                        "score_away": away_team_score,
                        "time": match_time,
                        "is_opened": False
                    }

                    if not os.path.exists(self.file_path):
                        stream_url = await self.get_url_games(home_team_name)
                        if stream_url:
                            game["stream"] = stream_url
                            game_copy = game.copy()
                            all_games.append(game_copy)
                            print(game)
                    else:
                        game_copy = game.copy()
                        all_games.append(game_copy)

                if not os.path.exists(self.file_path):
                    async with aiofiles.open(self.file_path, 'w') as games:
                        await games.write(f"{json.dumps(all_games)}")
                else:
                    await self.update_file(all_games)
                    await self.schedule_tasks()

                await asyncio.sleep(2)
        finally:
            await self.stop_driver()

    async def get_url_games(self, title):
        base_url = "https://bingsport.xyz/"

        response = requests.get("https://bingsport.xyz/football")
        bsoup = BeautifulSoup(response.text, 'html.parser')

        live_stream_elements = bsoup.find_all(class_='item-match')

        for live_stream in live_stream_elements:
            url_link = live_stream.get("href")
            link = base_url + url_link
            if len(url_link.split("/")) == 3:
                http_split = url_link.split("/")[2]
                if "vs" in http_split:
                    split_name = http_split.split("vs")[0].replace('_', " ")
                    team_name = split_name.strip()
                    bing = team_name.lower()
                    livescore = title.lower()
                    if self.are_teams_similar(bing, livescore):
                        print("Getting a new game stream")
                        return link
        else:
            return None

    def are_teams_similar(self, team1, team2, threshold=80):
        ratio = fuzz.partial_ratio(team1.lower(), team2.lower())
        return ratio >= threshold

    async def update_file(self, all_games):
        print("starting update_file")
        fcc_data = await self.read_file()

        file_lock = asyncio.Lock()

        for i in all_games:
            matching_data = next((x for x in fcc_data if x.get("title") == i.get("title")), None)
            if matching_data:
                print(f"Found matching_data for {i['title']}: {matching_data}")
                if i.get("score_home") != matching_data.get("score_home") or i.get("score_away") != matching_data.get(
                        "score_away"):
                    matching_data.update({
                        'score_home': '{}'.format(i.get("score_home")),
                        'score_away': '{}'.format(i.get("score_away")),
                    })

        async with file_lock:
            async with aiofiles.open(self.file_path, 'w') as fcc_file:
                await fcc_file.write(json.dumps(fcc_data))

    async def multithreading(self, url, title):
        print("multithreading")
        capturer = LivestreamCapturer(url, title)
        await asyncio.to_thread(capturer.capture_livestream)

    async def schedule_tasks(self):
        print("scheduler")
        fcc_data = await self.read_file()

        for game in fcc_data:
            if not game.get('is_opened'):
                url, title, time_str = game.get('stream'), game.get('title'), game.get('time')
                scheduled_time = datetime.strptime(time_str, "%H:%M").time()
                current_time = datetime.now().time()
                time_difference = (datetime.combine(datetime.today(), current_time) -
                                   datetime.combine(datetime.today(),
                                                    scheduled_time)).total_seconds() / 60

                if current_time >= scheduled_time:
                    while time_difference < 90:
                        asyncio.create_task(self.check_scheduled_task(url, title))
                        time_difference += 5
                else:
                    pass
            else:
                pass

        await asyncio.sleep(1)

    async def check_scheduled_task(self, url, title):
        print(f"Scheduled task executed for {title} at {datetime.now()}")
        await self.multithreading(url, title)
        await self.update_is_opened_flag(title)

    async def update_is_opened_flag(self, title):
        fcc_data = await self.read_file()
        file_lock = asyncio.Lock()

        for game in fcc_data:
            if game.get('title') == title:
                game['is_opened'] = True
        async with file_lock:
            async with aiofiles.open(self.file_path, 'w') as fcc_file:
                await fcc_file.write(json.dumps(fcc_data))

    async def read_file(self):
        async with aiofiles.open(self.file_path, 'r') as fcc_file:
            fcc_data = json.loads(await fcc_file.read())
            return fcc_data


async def main():
    scraper = LivescoreScraper()
    await scraper.get_today_matches()


if __name__ == "__main__":
    asyncio.run(main())
