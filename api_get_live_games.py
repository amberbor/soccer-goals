import http.client
import time

import aiofiles
import aiohttp
import schedule as schedule
from livestream import get_url_games
import requests
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

API_URL = "https://api-football-beta.p.rapidapi.com/fixtures"


async def fetch_data(url):
    querystring = {"live": "all"}

    headers = {
        "X-RapidAPI-Key": "47406c2fdamshdeb572e33153011p122233jsn4fbb9e035084",
        "X-RapidAPI-Host": "api-football-beta.p.rapidapi.com"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=querystring) as response:
            response.raise_for_status()
            data = await response.json()

    return data


# today matches get all the matches that are live and transform how it is suitable to us
async def get_today_matches():
    print("starting get_today_matches")
    all_matches = await fetch_data(API_URL)
    all_games = []
    all_streams = []
    for match in all_matches["response"]:
        team = match["teams"]
        team_1 = {}
        team_2 = {}
        team_1["name"] = team["home"]["name"]
        team_1["qualifier"] = "home"
        team_1["goals"] = match["goals"]["home"]
        team_2["name"] = team["away"]["name"]
        team_2["qualifier"] = "away"
        team_2["goals"] = match["goals"]["away"]
        minutes = match["fixture"]["status"]["elapsed"]
        game = {"title": "{} vs {}".format(team_1["name"], team_2["name"]),
                "score_home": "{}".format(team_1["goals"]), "score_away": "{}".format(team_2["goals"]),
                "minutes": "{}".format(minutes), "is_opened": True}
        # tab index is the index for each tab that we open with selenium
        if await get_url_games(team_1["name"]) is not None:
            game["stream"] = await get_url_games(team_1["name"])
            game_copy = game.copy()
            all_games.append(game_copy)
        else:
            pass
    await update_file(all_games)
    # await get_stream(all_games)


# update file makes an update if we have an goal
async def update_file(all_games):
    print("starting update_file")
    async with aiofiles.open('data.json', 'r') as fcc_file:
        fcc_data = json.loads(await fcc_file.read())

    all_live_goals = []
    for i in all_games:
        matching_data = next((x for x in fcc_data if x.get("title") == i.get("title")), None)
        if matching_data:
            print(f"Found matching_data for {i['title']}: {matching_data}")
            if i.get("score_home") != matching_data.get("score_home") or i.get("score_away") != matching_data.get(
                    "score_away"):
                live_goals = {"title": '{}'.format(i.get("title")),
                              'score_home': '{}'.format(i.get("score_home")),
                              'score_away': '{}'.format(i.get("score_away")),
                              'from_minutes': '{}'.format(matching_data.get("minutes")),
                              'to_minutes': '{}'.format(i.get("minutes")),
                              'stream': '{}'.format(i.get("stream"))}
                live_goals_copy = live_goals.copy()
                all_live_goals.append(live_goals_copy)

    async with aiofiles.open('live_goals.json', 'w') as live:
        await live.write(json.dumps(all_live_goals))

    async with aiofiles.open('data.json', 'w') as games:
        await games.write(json.dumps(all_games))

    # check if we have any live stream
    async with aiofiles.open('stream.json', 'r') as stream_file:
        stream_data = json.loads(await stream_file.read())
        if len(stream_data) == 0:
            async with aiofiles.open('stream.json', 'w') as stream_games:
                await stream_games.write(json.dumps(all_games))
        else:
            pass

        # find_m3u8_url()


# get_stream will get all the streams and open all of them in tabs
# async def get_stream(all_games):
#     # Keep track of titles of all games that need to be opened
#     titles_to_open = [i["title"] for i in all_games if i.get("stream") is not None and not i.get("is_opened")]
#
#     async with aiofiles.open('stream.json', 'r') as stream_file:
#         stream_data = json.loads(await stream_file.read())
#
#     opened_streams = []
#     for stream in stream_data:
#         if stream["title"] in titles_to_open:
#             print("Opening stream:", stream["title"])
#             opened_streams.append(stream)
#         else:
#             opened_streams.append(stream)
#
#     # Add new streams that were not present in stream_data
#     new_streams = [i for i in all_games if
#                    i.get("stream") is not None and i["title"] not in [s["title"] for s in stream_data]]
#     opened_streams.extend(new_streams)
#
#     async with aiofiles.open('stream.json', 'w') as stream_file:
#         await stream_file.write(json.dumps(opened_streams))


def run_async_function():
    asyncio.run(get_today_matches())


schedule.every(1).seconds.do(run_async_function)
while True:
    schedule.run_pending()
    time.sleep(1)
