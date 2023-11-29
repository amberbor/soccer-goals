# scraper_utils.py
import aiofiles
import json
from concurrent.futures import ThreadPoolExecutor


class ScraperUtils:
    @staticmethod
    async def update_file(all_games, file_path):
        print("starting update_file")
        fcc_data = await ScraperUtils.read_file(file_path)

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

        async with aiofiles.open(file_path, 'w') as fcc_file:
            await fcc_file.write(json.dumps(fcc_data))

    @staticmethod
    async def read_file(file_path):
        async with aiofiles.open(file_path, 'r') as fcc_file:
            fcc_data = json.loads(await fcc_file.read())
            return fcc_data

    @staticmethod
    async def multithreading(url, title):
        # This function can be further extended with any common logic or functionality
        pass
