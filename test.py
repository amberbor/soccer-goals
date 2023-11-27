import asyncio
from selenium import webdriver
from bs4 import BeautifulSoup

async def scrape_live_scores():
    # Set up a headless browser using Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.livescore.com/en/football/live/")

        # Wait for the page to load (you might need to adjust the wait time)
        # driver.implicitly_wait(5)

        while True:
            # Get the page source after JavaScript has rendered it
            page_source = driver.page_source

            bsoup = BeautifulSoup(page_source, 'html.parser')

            # Find all match elements
            match_elements = bsoup.find_all('div', class_='dp hp gp')

            for match in match_elements:
                match_time = match.select_one('.Ft.It').text  # Get the match time
                home_team_name = match.select_one('.kp .lp .np').text
                home_team_score = match.select_one('.rp .sp').text
                away_team_name = match.select_one('.kp .mp .np').text
                away_team_score = match.select_one('.rp .tp').text

                print("Match Time:", match_time)
                print("Home Team Name:", home_team_name)
                print("Home Team Score:", home_team_score)
                print("Away Team Name:", away_team_name)
                print("Away Team Score:", away_team_score)
                print("\n")

    finally:
        driver.quit()

# Create an event loop and run the async scraping function
loop = asyncio.get_event_loop()
loop.run_until_complete(scrape_live_scores())
