# database_operations.py
from mysql.connector.pooling import MySQLConnectionPool

class DatabaseOperations:
    def __init__(self, host, user, password, database, port):
        self.db_host = host
        self.db_user = user
        self.db_password = password
        self.db_name = database
        self.port = port

        self.db_pool = MySQLConnectionPool(
            pool_name="soccer_pool",
            pool_size=5,
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name,
            port=self.port
        )

        self.mysql_conn = self.db_pool.get_connection()
        self.mysql_cursor = self.mysql_conn.cursor(dictionary=True)

    def save_match_to_database(self, match_data):
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
        # Perform your update logic here
        self.mysql_cursor.execute(query, values)
        self.mysql_conn.commit()

    def update_match_to_database(self, match_data):
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

    def save_goal_to_database(self, title, match_url, match_id, match_score):
        # Insert goal data in the 'goals' table
        query = "INSERT INTO goals (match_title, match_url, match_id, match_score) VALUES (%s, %s, %s, %s)"
        values = (title, match_url, match_id, match_score)

        self.mysql_cursor.execute(query, values)
        self.mysql_conn.commit()

    def get_today_matches_from_database(self):
        # Get today's matches from the 'matches' table
        query = "SELECT * FROM matches WHERE DATE(start_date) = %s"
        values = (self.today_date,)

        self.mysql_cursor.execute(query, values)
        today_matches = self.mysql_cursor.fetchall()
        return today_matches

    def get_today_matches_from_title(self, title):
        # Get today's matches from the 'matches' table
        query = "SELECT * FROM matches WHERE DATE(start_date) = %s AND title = %s"
        values = (self.today_date,title)

        self.mysql_cursor.execute(query, values)
        today_matches = self.mysql_cursor.fetchall()
        return today_matches

    def get_today_goals_from_database(self):
        # Get today's goals from the 'goals' table
        query = "SELECT * FROM goals WHERE DATE(start_date) = %s"
        values = (self.today_date,)

        self.mysql_cursor.execute(query, values)
        today_goals = self.mysql_cursor.fetchall()
        return today_goals

    def delete_game_by_title(self, title):
        # Delete a game from the 'matches' table based on its title
        query = "DELETE FROM matches WHERE title = %s"
        values = (title,)

        self.mysql_cursor.execute(query, values)
        self.mysql_conn.commit()

        print(f"Game with title '{title}' deleted from the database.")

    def close_connections(self):
        if self.mysql_cursor:
            self.mysql_cursor.close()
        if self.mysql_conn:
            self.mysql_conn.close()
