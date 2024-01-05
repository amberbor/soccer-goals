import os
import subprocess
from seleniumwire import webdriver
import chromedriver_autoinstaller


class LivestreamCapturer:
    def __init__(self, url, title, max_segments=3):
        self.url = url
        self.title = title
        chromedriver_autoinstaller.install()
        self.max_segments = max_segments
        self.segments = []  # List to store segment filenames
        self.output_video_path = f"{self.title}/{self.title}_%03d.ts"
        self.driver = None

    def start_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)

    def stop_driver(self):
        if self.driver:
            self.driver.quit()

    def capture_livestream(self):
        print("capture_livestream")
        try:
            self.start_driver()

            # Navigate to the webpage
            self.driver.get(self.url)

            # Wait for the page to load
            self.driver.implicitly_wait(10)

            os.makedirs(self.title, exist_ok=True)

            # Find the first M3U8 URL
            for request in self.driver.requests:
                if "m3u8" in request.url:
                    m3u8_url = request.url
                    print("found" + m3u8_url)
                    print(m3u8_url)

                    ffmpeg_command = [
                        'ffmpeg',
                        '-i', m3u8_url,
                        '-segment_time', '60',
                        '-f', 'segment',
                        '-c', 'copy',
                        '-map', '0',
                        '-bsf:v', 'h264_mp4toannexb',
                        '-reset_timestamps', '1',
                        self.output_video_path  # Use the generated filename
                    ]

                    # Run the ffmpeg command
                    subprocess.Popen(ffmpeg_command)
                else:
                    print("not found")

        except Exception as e:
            print("Error:", e)

        finally:
            self.stop_driver()
