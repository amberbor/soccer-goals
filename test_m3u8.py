import os
from datetime import datetime, timedelta, timezone

import requests
import subprocess
from seleniumwire import webdriver
from urllib.parse import urljoin

# Initialize Selenium WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the webpage
    driver.get("https://bingsport.xyz/live-stream/35569/Corinthians_vs_Bahia")

    # Wait for the page to load
    driver.implicitly_wait(10)

    # Find the first M3U8 URL
    for request in driver.requests:
        if "m3u8" in request.url:
            m3u8_url = request.url
            print("found" + m3u8_url)
            print(m3u8_url)

            # Replace this with the duration you want to capture before the current time
            duration_to_capture = "00:03:00"

            # Replace this with the desired output path and filename
            output_video_path = "output_video.mp4"

            # Call the function to capture the livestream segment using FFmpeg

            ffmpeg_command = [
                'ffmpeg',
                '-ss', "00:03:00",  # Replace with your desired start time
                '-i', m3u8_url,
                '-segment_time', '30',
                '-f', 'segment',
                '-c', 'copy',
                '-map', '0',
                '-bsf:v', 'h264_mp4toannexb',
                '-reset_timestamps', '1',
                'output_video%03d.ts'
            ]

            # Run the ffmpeg command
            subprocess.run(ffmpeg_command)
        else:
            print("not found")

except Exception as e:
    print("Error:", e)

finally:
    # Quit the Selenium WebDriver
    driver.quit()