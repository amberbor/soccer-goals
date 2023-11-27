import json
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from seleniumwire import webdriver


def find_m3u8_url(title, stream_game):
    m3u8_url = None
    try:
        # Initialize the Selenium Wire-enabled WebDriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the webpage
        driver.get(stream_game)

        # Wait for the page to load
        driver.implicitly_wait(10)

        # Find the first M3U8 URL
        for request in driver.requests:
            if "m3u8" in request.url:
                m3u8_url = request.url
                break
    except Exception as e:
        print("Error retrieving M3U8 URL:", e)
    finally:
        driver.quit()

    return (m3u8_url, title)


def save_goal(url, title):
    try:
        youtube_dl_output = subprocess.check_output([
            "youtube-dl", "-g", "-f", "best", url
        ])
        video_url = youtube_dl_output.decode().strip()

        ffmpeg_command = [
            "ffmpeg",
            "-t", "60",  # Set the duration to 60 seconds (adjust as needed)
            "-i", video_url,
            "-y", title
        ]

        subprocess.run(ffmpeg_command)
    except subprocess.CalledProcessError as e:
        print("Error executing youtube-dl or ffmpeg:", e)


def main():
    m3u8_urls = []  # List to store M3U8 URLs and titles

    print("Starting get_webbrowser")
    with open('live_goals.json', 'r') as fcc_file:
        fcc_data = json.load(fcc_file)
        with ProcessPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
            futures = []
            for i in fcc_data:
                title = "{}-{}-{}.mp4".format(i["title"], i["score_home"], i["score_away"]).replace(" ", "")
                if i["stream"] != "None":
                    stream_game = i["stream"]
                    future = executor.submit(find_m3u8_url, title, stream_game)
                    futures.append(future)

            for future in futures:
                result = future.result()
                if result[0]:  # Check if a valid M3U8 URL was found
                    m3u8_urls.append(result)

    for url, title in m3u8_urls:
        save_goal(url, title)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(1)
