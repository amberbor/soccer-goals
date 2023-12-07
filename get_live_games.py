import os
import subprocess
import time
from datetime import datetime

from moviepy.video.io.VideoFileClip import VideoFileClip
from seleniumwire import webdriver
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from threading import Lock
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler
from get_m3u8 import LivestreamCapturer


class LivescoreScraper:
    def __init__(self):
        self.segments = []
        self.driver = None
        self.today_date = datetime.today().strftime('%Y-%m-%d')
        self.file_path = os.path.join("games", f"{self.today_date}.json")
        self.livestream_executor = ProcessPoolExecutor(max_workers=3)
        self.main_executor = ThreadPoolExecutor()
        self.file_lock = Lock()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def stop_driver(self):
        if self.driver:
            self.driver.quit()

    def get_today_matches(self):
        try:
            self.start_driver()
            self.driver.get("https://www.livescores.com/?tz=1")

            while True:
                page_source = self.driver.page_source
                bsoup = BeautifulSoup(page_source, 'html.parser')

                match_elements = bsoup.find_all('div', class_=['Af Ef', 'Af Ef Df'])

                all_games = []

                for match in match_elements:
                    match_time = match.select_one('.dj .wg').text or match.select_one('.dj .wg .Ag').text
                    home_team_name = match.select_one('.dj .ij .kj').text
                    home_team_score = match.select_one('.dj .hj .fj .nj').text
                    away_team_name = match.select_one('.dj .jj .kj').text
                    away_team_score = match.select_one('.dj .hj .fj .oj').text

                    game = {
                        "title": f"{home_team_name} vs {away_team_name}",
                        "score_home": home_team_score,
                        "score_away": away_team_score,
                        "time": match_time,
                        "is_opened": False
                    }

                    if not os.path.exists(self.file_path):
                        stream_url = self.get_url_games(home_team_name)
                        if stream_url:
                            game["stream"] = stream_url
                            game_copy = game.copy()
                            all_games.append(game_copy)
                            print(game)
                    else:
                        game_copy = game.copy()
                        all_games.append(game_copy)

                if not os.path.exists(self.file_path):
                    with open(self.file_path, 'w') as games:
                        games.write(json.dumps(all_games))
                else:
                    self.update_file(all_games)
                    self.schedule_tasks()

                time.sleep(2)
        finally:
            self.stop_driver()

    def get_url_games(self, title):
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

    def update_file(self, all_games):
        print("starting update_file")
        try:
            with self.file_lock:
                fcc_data = self.read_file()

                for i in all_games:
                    matching_data = next((x for x in fcc_data if x.get("title") == i.get("title")), None)
                    if matching_data:
                        print(f"Found matching_data for {i['title']}: {matching_data}")
                        if i.get("score_home") != matching_data.get("score_home") or i.get(
                                "score_away") != matching_data.get(
                                "score_away"):
                            self.save_goal(title=matching_data.get("title"),     filename=f"{matching_data.get('title')}_{i.get('score_home')}-{i.get('score_away')}.mp4")
                            matching_data.update({
                                'score_home': '{}'.format(i.get("score_home")),
                                'score_away': '{}'.format(i.get("score_away")),
                            })

                with open(self.file_path, 'w') as fcc_file:
                    fcc_file.write(json.dumps(fcc_data))

        except Exception as e:
            print(f"Error in update_file: {e}")
            # Handle the exception as needed
        finally:
            if self.file_lock.locked():
                print("file released")
                self.file_lock.release()

    def multiproccess(self, url, title):
        print("multiproccess")
        capturer = LivestreamCapturer(url, title)
        self.livestream_executor.submit(capturer.capture_livestream)

    def schedule_tasks(self):
        print("scheduler")
        try:
            with self.file_lock:
                fcc_data = self.read_file()

                for game in fcc_data:
                    url, title, time_str = game.get('stream'), game.get('title'), game.get('time')
                    if self.is_valid_time_format(time_str):
                        scheduled_time = datetime.strptime(time_str, "%H:%M").time()
                        current_time = datetime.now().time()
                        time_difference = (datetime.combine(datetime.today(), current_time) -
                                           datetime.combine(datetime.today(),
                                                            scheduled_time)).total_seconds() / 60

                        if current_time >= scheduled_time and not game.get('is_opened'):
                            game['is_opened'] = True
                            self.check_scheduled_task(url, title)

                            # Remove game if time difference exceeds 120 minutes
                        if time_difference >= 150:
                            fcc_data.remove(game)

                self.write_file(fcc_data)
        except Exception as e:
            print(f"Error in update_file: {e}")
            # Handle the exception as needed
        finally:
            if self.file_lock.locked():
                print("file released")
                self.file_lock.release()

        time.sleep(1)

    def check_scheduled_task(self, url, title):
        print(f"Scheduled task executed for {title} at {datetime.now()}")
        self.multiproccess(url, title)

    def read_file(self):
        with open(self.file_path, 'r') as fcc_file:
            fcc_data = json.loads(fcc_file.read())
            return fcc_data

    def write_file(self, fcc_data):
        with open(self.file_path, 'w') as fcc_file:
            fcc_file.write(json.dumps(fcc_data))

    def is_valid_time_format(self, time_str):
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    def is_valid_video(self,file_path):
        try:
            VideoFileClip(file_path)
            return True
        except Exception as e:
            print(f"Invalid video file: {file_path}. Error: {e}")
            return False

    def save_goal(self, title, filename):
        print("Goaaaaaaaaaal")

        folder_path = os.path.join(os.getcwd(), title)

        if os.path.exists(folder_path):
            ts_files = [filename for filename in os.listdir(folder_path) if
                        filename.endswith(".ts") and self.is_valid_video(os.path.join(folder_path, filename))]

            ts_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)) if os.path.isfile(
                os.path.join(folder_path, x)) else 0, reverse=True)

            latest_ts_files = ts_files[:2][::-1]

            if len(latest_ts_files) == 2:
                ts_file_paths = [os.path.join(folder_path, ts_file) for ts_file in latest_ts_files]

                with open(os.path.join(folder_path, 'file_list.txt'), 'w') as file_list:
                    for ts_file in ts_file_paths:
                        file_list.write(f"file '{ts_file}'\n")

                ffmpeg_command = (
                    f'ffmpeg -f concat -safe 0 -i "{os.path.join(folder_path, "file_list.txt")}" '
                    f'-c copy "{os.path.join(folder_path, filename)}"'
                )

                subprocess.run(ffmpeg_command, shell=True)

                os.remove(os.path.join(folder_path, 'file_list.txt'))

                print(f"Successfully created {os.path.join(folder_path, 'final.mp4')}")
            else:
                print("Not enough valid '.ts' files to create an MP4")
        else:
            print(f"Folder not found: {folder_path}")

    def run_parallel(self):
        # Submit both main code and livestream captures to the process pool
        main_future = self.main_executor.submit(self.get_today_matches)
        main_future.result()
        # Schedule tasks separately using APScheduler
        # Sleep for a short time to avoid high CPU usage
        time.sleep(2)



def main():
    scraper = LivescoreScraper()
    scraper.run_parallel()


if __name__ == "__main__":
    main()
