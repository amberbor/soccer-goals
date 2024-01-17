import os
import subprocess
import time
from datetime import datetime, timedelta

from mysql.connector.pooling import MySQLConnectionPool
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
import cloudinary
from cloudinary.uploader import upload
from database_operations import DatabaseHelper


class LivescoreScraper:
    def __init__(self):
        self.logger = None
        self.driver = None
        self.today_date = datetime.today().strftime('%Y-%m-%d')
        self.livestream_executor = ProcessPoolExecutor(max_workers=3)
        self.main_executor = ThreadPoolExecutor()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.current_time = datetime.now().time()
        self.end_time = (datetime.combine(datetime.today(), self.current_time) + timedelta(hours=2)).time()
        # MySQL connection parameters
        self.db_host = '127.0.0.1'
        self.db_user = 'root'
        self.db_password = ''
        self.db_name = 'soccer'
        self.port = 3308

        self.db_helper = DatabaseHelper(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name,
            port=self.port,
            save_goal=self.save_goal,
        )

        # Establish MySQL connection
        # self.db_pool = MySQLConnectionPool(
        #     pool_name="soccer_pool",
        #     pool_size=5,
        #     host=self.db_host,
        #     user=self.db_user,
        #     password=self.db_password,
        #     database=self.db_name,
        #     port= self.port
        # )

        self.mysql_conn = None
        self.db_pool = None
        self.mysql_cursor = None
        # self.mysql_conn = self.db_pool.get_connection()
        # self.mysql_cursor = self.mysql_conn.cursor(dictionary=True)

    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def stop_driver(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"Error while stopping driver: {e}")
        finally:
            self.db_helper.close_database_connection()

    def upload_to_cloudinary(self,video_path, public_id):
        cloudinary.config(
            cloud_name='dqmjatfqz',
            api_key='719444776498496',
            api_secret='x6y_LAtPUsixeVIwW5K_s2NLhiQ'
        )

        result = upload(video_path, public_id=public_id, resource_type="video")

        return result['secure_url']

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
                        "match_time": match_time,
                        "home_team_name": home_team_name,
                        "away_team_name": away_team_name,
                        "is_opened": False,
                        "is_finished": False,
                    }

                    stream_info = self.get_url_games(home_team_name)
                    today_matches_from_title = self.db_helper.get_today_matches_from_title(game["title"])
                    if stream_info and not today_matches_from_title:
                        print("Matches are creating")
                        stream_url, league_name = stream_info
                        game["stream"] = stream_url
                        game["league_name"] = league_name
                        self.db_helper.save_match_to_database(game)
                    elif stream_info and today_matches_from_title:
                        print("Matches are updating")
                        self.db_helper.update_match_to_database(game)
                        self.schedule_tasks(today_matches_from_title)

                time.sleep(10)
        finally:
            self.stop_driver()
            if self.mysql_cursor:
                self.mysql_cursor.close()
            if self.mysql_conn:
                self.mysql_conn.close()

    def get_url_games(self, title):
        base_url = "https://bingsport.xyz/"

        response = requests.get("https://bingsport.xyz/football")
        bsoup = BeautifulSoup(response.text, 'html.parser')

        live_stream_elements = bsoup.find_all(class_='item-match')

        for live_stream in live_stream_elements:
            league_name = live_stream.find(class_='league-name').text.strip()
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
                        return link, league_name
        else:
            return None

    def are_teams_similar(self, team1, team2, threshold=80):
        ratio = fuzz.partial_ratio(team1.lower(), team2.lower())
        return ratio >= threshold

    def multiproccess(self, url, title):
        print("multiproccess")
        capturer = LivestreamCapturer(url, title)
        self.livestream_executor.submit(capturer.capture_livestream)

    def schedule_tasks(self, today_matches_from_title):
        print("scheduler")
        try:
            for match in today_matches_from_title:
                url, title, time_str = match["stream"], match["title"], match["match_time"]
                if self.is_valid_time_format(time_str):
                    scheduled_time = datetime.strptime(time_str, "%H:%M").time()
                    current_time = datetime.now().time()
                    time_difference = (datetime.combine(datetime.today(), current_time) -
                                       datetime.combine(datetime.today(), scheduled_time)).total_seconds() / 60

                    if current_time >= scheduled_time and not match["is_opened"] and not match["is_finished"]:
                        # Set 'is_opened' in the database
                        self.db_helper.set_match_opened(match["id"])

                        self.check_scheduled_task(url, title)

                    # Remove match if time difference exceeds 150 minutes
                    if time_difference >= 150:
                        self.db_helper.set_match_finished(match["id"])
                else:
                    self.db_helper.set_match_finished(match["id"])
        except Exception as e:
            print(f"Error in schedule_tasks: {e}")
        time.sleep(1)

    def check_scheduled_task(self, url, title):
        print(f"Scheduled task executed for {title} at {datetime.now()}")
        self.multiproccess(url, title)

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
        print("Goaaaaaaaaaal", title)

        folder_path = os.path.join(os.getcwd(), title)

        if os.path.exists(folder_path):
            ts_files = [filename for filename in os.listdir(folder_path) if
                        filename.endswith(".ts") and self.is_valid_video(os.path.join(folder_path, filename))]

            # Find the latest numeric part without sorting
            numeric_parts = sorted([int(''.join(filter(str.isdigit, ts_file))) for ts_file in ts_files], reverse=True)

            # Find the latest and second latest numeric parts
            file_1, file_2, file_3 = numeric_parts[1], numeric_parts[2], numeric_parts[3]

            file_3_filename = f"{title}_{file_3:03d}.ts"
            file_2_filename = f"{title}_{file_2:03d}.ts"
            file_1_filename = f"{title}_{file_1:03d}.ts"

            ts_file_paths = [os.path.join(folder_path, file_1_filename), os.path.join(folder_path, file_2_filename), os.path.join(folder_path, file_3_filename)]

            with open(os.path.join(folder_path, 'file_list.txt'), 'w') as file_list:
                for ts_file in ts_file_paths:
                    file_list.write(f"file '{ts_file}'\n")

            ffmpeg_command = (
                f'ffmpeg -f concat -safe 0 -i "{os.path.join(folder_path, "file_list.txt")}" '
                f'-c copy -async 1 "{os.path.join(folder_path, filename)}"'
            )

            subprocess.run(ffmpeg_command, shell=True)

            os.remove(os.path.join(folder_path, 'file_list.txt'))

            base_filename, extension = os.path.splitext(filename)
            public_id = base_filename
            secure_url = self.upload_to_cloudinary(os.path.join(folder_path, filename),
                                                   public_id)
            print("secure_url")
            return secure_url
        else:
            print(f"Folder not found: {folder_path}")

    def run_parallel(self):
        try:
            self.db_helper.open_database_connection()

            while True:
                try:
                    self.get_today_matches()
                except Exception as e:
                    print(f"Error in run_continuous: {e}")

                time.sleep(5)
        finally:
            self.db_helper.close_database_connection()


def main():
    scraper = LivescoreScraper()
    scraper.run_parallel()


if __name__ == "__main__":
    main()
