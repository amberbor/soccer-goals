from flask import Flask, jsonify,request
from datetime import datetime
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from database.models import db, Match, Goal
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@mysql:3306/soccer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

@app.route('/matches', methods=['GET'])
def get_matches():
    try:
        now = datetime.now()
        today_date = now.strftime('%Y-%m-%d')

        matches_with_scores = Match.query.filter(
            Match.start_date.startswith(today_date),
            Match.score_home != "",
            Match.score_away != ""
        ).all()

        remaining_matches = Match.query.filter(
            Match.start_date.startswith(today_date),
            Match.score_home == "",
            Match.score_away == ""
        ).order_by(Match.match_time.asc()).all()
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
            goals = Goal.query.filter_by(match_id=match_id).all()
        else:
            goals = Goal.query.all()
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
    app.run(host='0.0.0.0', port=5000)
