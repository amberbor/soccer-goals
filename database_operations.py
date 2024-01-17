from mysql.connector.pooling import MySQLConnectionPool

class DatabaseHelper:
    def __init__(self, host, user, password, database, port, save_goal):
        self.db_host = host
        self.db_user = user
        self.db_password = password
        self.db_name = database
        self.port = port
        self.db_pool = None
        self.mysql_conn = None
        self.mysql_cursor = None
        self.save_goal = save_goal

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

    def update_match_to_database(self, match_data):
        today_matches = self.get_time_matches_from_title(match_data['title'])

        if today_matches and today_matches[0]:
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
        today_matches = self.get_today_matches_from_title(match_data['title'])

        if not today_matches:
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

    def save_goal_to_database(self, title, match_url, match_id, match_score):
        query = "INSERT INTO goals (match_title, match_url, match_id, match_score) VALUES (%s, %s, %s, %s)"
        values = (title, match_url, match_id, match_score)

        self.mysql_cursor.execute(query, values)
        self.mysql_conn.commit()

    def get_today_matches_from_title(self, title):
        query = "SELECT * FROM matches WHERE DATE(start_date) = %s AND title = %s"
        values = (self.today_date, title)

        self.mysql_cursor.execute(query, values)
        today_matches = self.mysql_cursor.fetchall()
        return today_matches

    def get_time_matches_from_title(self, title):
        query = "SELECT * FROM matches WHERE DATE(start_date) = %s AND title = %s AND (STR_TO_DATE(match_time, '%%H:%%i') >= %s OR STR_TO_DATE(match_time, '%%H:%%i') <= %s)"
        values = (self.today_date, title, self.current_time , self.end_time)

        self.mysql_cursor.execute(query, values)
        today_matches = self.mysql_cursor.fetchall()
        return today_matches

    def get_today_goals_from_database(self):
        query = "SELECT * FROM goals WHERE DATE(start_date) = %s"
        values = (self.today_date,)

        self.mysql_cursor.execute(query, values)
        today_goals = self.mysql_cursor.fetchall()
        return today_goals

    def delete_game_by_title(self, title):
        query = "DELETE FROM matches WHERE title = %s"
        values = (title,)

        self.mysql_cursor.execute(query, values)
        self.mysql_conn.commit()

    def set_match_opened(self, match_id):
        try:
            # Update the 'is_opened' column in the 'matches' table
            query = "UPDATE matches SET is_opened = TRUE WHERE id = %s"
            values = (match_id,)

            self.mysql_cursor.execute(query, values)
            self.mysql_conn.commit()
            print(f"Match with ID {match_id} marked as opened.")
        except Exception as e:
            print(f"Error in set_match_opened: {e}")
            # Handle the exception as needed

    def set_match_finished(self, match_id):
        try:
            query = "UPDATE matches SET is_finished = TRUE WHERE id = %s"
            values = (match_id,)

            self.mysql_cursor.execute(query, values)
            self.mysql_conn.commit()
            print(f"Match with ID {match_id} marked as finished.")
        except Exception as e:
            print(f"Error in set_match_finished: {e}")
            # Handle the exception as needed
