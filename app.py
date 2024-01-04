from flask import Flask, jsonify,request
from datetime import datetime
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3308/soccer'
db = SQLAlchemy(app)

class Matches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team_name = db.Column(db.String(255))
    away_team_name = db.Column(db.String(255))
    score_home = db.Column(db.String(10))
    score_away = db.Column(db.String(10))
    match_time = db.Column(db.String(20))
    league_name = db.Column(db.String(255))
    start_date = db.Column(db.String(20))  # Assuming the start_date column is a string

class Goals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_title = db.Column(db.Text)
    match_url = db.Column(db.Text)
    start_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    match_id = db.Column(db.Integer, default=None)
    match_score = db.Column(db.Text)

@app.route('/matches', methods=['GET'])
def get_matches():
    try:
        now = datetime.now()
        today_date = now.strftime('%Y-%m-%d')

        matches_with_scores = Matches.query.filter(
            Matches.start_date.startswith(today_date),
            Matches.score_home != "",
            Matches.score_away != ""
        ).all()

        remaining_matches = Matches.query.filter(
            Matches.start_date.startswith(today_date),
            Matches.score_home == "",
            Matches.score_away == ""
        ).order_by(Matches.match_time.asc()).all()
        all_matches = matches_with_scores + remaining_matches

        serialized_matches = [
            {
                "id": match.id,
                "home_team_name": match.home_team_name,
                "away_team_name": match.away_team_name,
                "score_home": match.score_home,
                "score_away": match.score_away,
                "match_time": match.match_time,
                "league_name": match.league_name,
                "start_date": match.start_date,
            }
            for match in all_matches
        ]
        return jsonify(serialized_matches)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/goals', methods=['GET'])
def get_goals():
    try:
        match_id = request.args.get('matchId')  # Get matchId from query parameters
        if match_id:
            goals = Goals.query.filter_by(match_id=match_id).all()
        else:
            goals = Goals.query.all()
        serialized_goals = [
            {
                "id": goal.id,
                "match_title": goal.match_title,
                "match_url": goal.match_url,
                "start_date": goal.start_date,
                "match_id": goal.match_id,
                "match_score": goal.match_score,
            }
            for goal in goals
        ]
        return jsonify(serialized_goals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
