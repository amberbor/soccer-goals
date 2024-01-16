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

    def open_database_connection(self):
        try:
            if not self.db_pool:
                self.db_pool = MySQLConnectionPool(
                    pool_name="soccer_pool",
                    pool_size=5,
                    host=self.db_host,
                    user=self.db_user,
                    password=self.db_password,
                    database=self.db_name,
                    port=self.port
                )

            if not self.mysql_conn:
                self.mysql_conn = self.db_pool.get_connection()
                self.mysql_cursor = self.mysql_conn.cursor(dictionary=True)
        except Exception as e:
            print(f"Error while opening database connection: {e}")
    def close_database_connection(self):
        try:
            if self.mysql_cursor:
                self.mysql_cursor.close()
            if self.mysql_conn:
                print("Closing database connection...")
                self.mysql_conn.close()
                print("Database connection closed.")
        except AttributeError as attr_error:
            print(f"AttributeError while closing database connection: {attr_error}")
        except Exception as e:
            print(f"Error while closing database connection: {e}")

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
            self.close_database_connection()

    def update_match_to_database(self, match_data):
        print("Update file Match was found")

        today_matches = self.get_time_matches_from_title(match_data['title'])

        if today_matches[0]:
            existing_match_data = today_matches[0]

            query = (
                "UPDATE matches "
                "SET score_home = %s, "
                "    score_away = %s, "
                "    is_opened = %s "
                "WHERE title = %s"
            )

            values = (
                match_data['score_home'],
                match_data['score_away'],
                match_data['is_opened'],
                match_data['title']
            )

            self.mysql_cursor.execute(query, values)
            self.mysql_conn.commit()

            if (
                    (match_data["score_home"] != existing_match_data["score_home"]
                     or match_data["score_away"] != existing_match_data["score_away"])
                    and (match_data["score_home"] != "0" or match_data["score_away"] != "0")
            ):
                print("Goal was made", match_data["title"])
                secure_url = self.save_goal(
                    title=match_data["title"],
                    filename=f"{match_data['title']}_{match_data['score_home']}-{match_data['score_away']}.mp4",
                )
                self.save_goal_to_database(
                    title=match_data["title"],
                    match_score="{}-{}".format(match_data['score_home'], match_data['score_away']),
                    match_id=existing_match_data["id"],
                    match_url=secure_url,
                )

    def save_match_to_database(self, match_data):
        # Insert or update match data in the 'matches' table

        try:
            # self.open_database_connection()

            today_matches = self.get_today_matches_from_title(match_data['title'])

            if not today_matches:
                print('No matches')
                query = (
                    "INSERT INTO matches (title, home_team_name, away_team_name, score_home, score_away, match_time, is_opened, stream, league_name) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE "
                    "home_team_name = VALUES(home_team_name), "
                    "away_team_name = VALUES(away_team_name), "
                    "score_home = VALUES(score_home), "
                    "score_away = VALUES(score_away), "
                    "match_time = VALUES(match_time), "
                    "is_opened = VALUES(is_opened), "
                    "stream = VALUES(stream),"
                    "league_name = VALUES(league_name)"
                )

                values = (
                    match_data['title'],
                    match_data['home_team_name'],
                    match_data['away_team_name'],
                    match_data['score_home'],
                    match_data['score_away'],
                    match_data['match_time'],
                    match_data['is_opened'],
                    match_data.get('stream', None),
                    match_data.get('league_name', None)
                )
                self.mysql_cursor.execute(query, values)
                self.mysql_conn.commit()
            else:
                print("Update file Match was found")
                existing_match_data = today_matches[0]

                query = (
                    "UPDATE matches "
                    "SET score_home = %s, "
                    "    score_away = %s, "
                    "    is_opened = %s "
                    "WHERE title = %s"
                )

                values = (
                    match_data['score_home'],
                    match_data['score_away'],
                    match_data['is_opened'],
                    match_data['title']
                )

                # Perform your update logic here
                self.mysql_cursor.execute(query, values)
                self.mysql_conn.commit()

                if (
                        (match_data["score_home"] != existing_match_data["score_home"]
                        or match_data["score_away"] != existing_match_data["score_away"])
                        and (match_data["score_home"] != "0" or match_data["score_away"] != "0")
                ):
                    print("Goal was made", match_data["title"])
                    secure_url = self.save_goal(
                        title=match_data["title"],
                        filename=f"{match_data['title']}_{match_data['score_home']}-{match_data['score_away']}.mp4",
                    )
                    self.save_goal_to_database(
                        title=match_data["title"],
                        match_score="{}-{}".format(match_data['score_home'], match_data['score_away']),
                        match_id=existing_match_data["id"],
                        match_url=secure_url,
                    )
        except Exception as e:
            self.logger.error(f"Error in save_match_to_database: {e}")


    def save_goal_to_database(self, title, match_url, match_id, match_score):
        # Insert goal data in the 'goals' table
        try:
            # self.open_database_connection()
            query = "INSERT INTO goals (match_title, match_url, match_id, match_score) VALUES (%s, %s, %s, %s)"
            values = (title, match_url, match_id, match_score)

            self.mysql_cursor.execute(query, values)
            self.mysql_conn.commit()
        except Exception as e:
            self.logger.error(f"Error in save_match_to_database: {e}")


    # def get_today_matches_from_database(self):
    #     # Get today's matches from the 'matches' table
    #     try:
    #         # self.open_database_connection()
    #         query = "SELECT * FROM matches WHERE DATE(start_date) = %s"
    #         values = (self.today_date,)
    #
    #         self.mysql_cursor.execute(query, values)
    #         today_matches = self.mysql_cursor.fetchall()
    #         return today_matches
    #     except Exception as e:
    #         self.logger.error(f"Error in get_today_matches_from_database: {e}")

    def get_today_matches_from_title(self, title):
        # Get today's matches from the 'matches' table
        try:
            # self.open_database_connection()
            query = "SELECT * FROM matches WHERE DATE(start_date) = %s AND title = %s"
            values = (self.today_date,title)

            self.mysql_cursor.execute(query, values)
            today_matches = self.mysql_cursor.fetchall()
            return today_matches
        except Exception as e:
            self.logger.error(f"Error in get_today_matches_from_title: {e}")

    def get_time_matches_from_title(self, title):
        # Get today's matches from the 'matches' table
        try:
            # self.open_database_connection()
            query = "SELECT * FROM matches WHERE DATE(start_date) = %s AND title = %s AND (STR_TO_DATE(match_time, '%%H:%%i') >= %s OR STR_TO_DATE(match_time, '%%H:%%i') <= %s)"
            values = (self.today_date,title, self.current_time , self.end_time)

            self.mysql_cursor.execute(query, values)
            today_matches = self.mysql_cursor.fetchall()
            return today_matches
        except Exception as e:
            self.logger.error(f"Error in get_today_matches_from_title: {e}")



    def get_today_goals_from_database(self):
        # Get today's goals from the 'goals' table
        try:
            # Open database connection
            # self.open_database_connection()

            query = "SELECT * FROM goals WHERE DATE(start_date) = %s"
            values = (self.today_date,)

            self.mysql_cursor.execute(query, values)
            today_goals = self.mysql_cursor.fetchall()
            return today_goals
        except Exception as e:
            self.logger.error(f"Error in get_today_goals_from_database: {e}")


    def delete_game_by_title(self, title):
        # Delete a game from the 'matches' table based on its title
        try:
            # Open database connection
            # self.open_database_connection()
            query = "DELETE FROM matches WHERE title = %s"
            values = (title,)

            self.mysql_cursor.execute(query, values)
            self.mysql_conn.commit()

            print(f"Game with title '{title}' deleted from the database.")
        except Exception as e:
            self.logger.error(f"Error in delete_game_by_title: {e}")


    def upload_to_cloudinary(self,video_path, public_id):
        cloudinary.config(
            cloud_name='dqmjatfqz',
            api_key='719444776498496',
            api_secret='x6y_LAtPUsixeVIwW5K_s2NLhiQ'
        )

        result = upload(video_path, public_id=public_id, resource_type="video")

        return result['secure_url']

    def set_match_opened(self, match_id):
        try:
            # Update the 'is_opened' column in the 'matches' table
            # self.open_database_connection()
            query = "UPDATE matches SET is_opened = TRUE WHERE id = %s"
            values = (match_id,)

            self.mysql_cursor.execute(query, values)
            self.mysql_conn.commit()
            print(f"Match with ID {match_id} marked as opened.")
        except Exception as e:
            print(f"Error in set_match_opened: {e}")
            # Handle the exception as needed

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
                        "is_opened": False
                    }

                    stream_info = self.get_url_games(home_team_name)
                    today_matches_from_title = self.get_today_matches_from_title(game["title"])
                    if stream_info and today_matches_from_title is None:
                        print("Matches are creating")
                        stream_url, league_name = stream_info
                        game["stream"] = stream_url
                        game["league_name"] = league_name
                        self.save_match_to_database(game)
                    elif stream_info and today_matches_from_title is not None:
                        print("Matches are updating")
                        self.update_match_to_database(game)
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

                    if current_time >= scheduled_time and not match["is_opened"]:
                        # Set 'is_opened' in the database
                        self.set_match_opened(match["id"])

                        self.check_scheduled_task(url, title)

                    # Remove match if time difference exceeds 150 minutes
                    if time_difference >= 150:
                        self.delete_game_by_title(match["title"])
                else:
                    self.delete_game_by_title(match["title"])
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
        while True:
            try:
                self.open_database_connection()
                self.get_today_matches()
            except Exception as e:
                print(f"Error in run_continuous: {e}")
            finally:
                self.close_database_connection()

            time.sleep(5)


def main():
    scraper = LivescoreScraper()
    scraper.run_parallel()


if __name__ == "__main__":
    main()
