from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    home_team_name = db.Column(db.Text(collation='utf8mb4_general_ci'), nullable=False)
    away_team_name = db.Column(db.Text(collation='utf8mb4_general_ci'), nullable=False)
    match_time = db.Column(db.Text)
    is_opened = db.Column(db.Boolean)
    is_finished = db.Column(db.Boolean)
    start_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    stream = db.Column(db.Text, nullable=False)
    score_home = db.Column(db.Text)
    score_away = db.Column(db.Text)
    league_name = db.Column(db.Text)
    task_id = db.Column(db.String(255))

    def __repr__(self):
        return f"<Todo {self.id}, {self.title}>"

class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    match_title = db.Column(db.Text)
    match_url = db.Column(db.Text)
    start_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    match_id = db.Column(db.Integer)
    match_score = db.Column(db.Text)

    def __repr__(self):
        return f"<Todo {self.id}, {self.match_title}>"
