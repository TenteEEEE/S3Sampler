from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import re
import time
import json
import argparse
import requests
import chromedriver_binary
import numpy as np
import pandas as pd


class scoresaber_scraper:
    def __init__(self, interval=5, unranked=False, headless=True, restart=False):
        self.baseurl = 'https://scoresaber.com'
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=640,480')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        if headless:
            options.add_argument('--headless')
        if os.name != 'nt':
            # On Linux case, you may need to install chromedriver manually
            self.driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=options)
        else:
            try:
                self.driver = webdriver.Chrome(options=options)
            except:
                self.driver = webdriver.Chrome('C:/Program Files/chromedriver_win32/chromedriver', options=options)
        self.unranked = unranked
        self.restart = restart
        self.previous = 0
        if self.restart:
            try:
                fname = sorted(os.listdir('tmp'))[0]
                with open('./tmp/' + fname) as f:
                    self.song_database = json.load(f)
                self.previous = int(fname[:4])
            except:
                self.song_database = {}
        if interval <= 1.5:
            print('Interval must be bigger than 0.5, so it set to 5.')
            interval = 5
        self.interval = interval
        self.intervalf = lambda: np.random.poisson(self.interval - 1.5) + np.random.rand() + 1  # like human access
        self.maxretry = 3
        links, leaderboards = self.cook_songlist_page()
        self.pages = self.find_num_pages(links)

    def __del__(self):
        self.driver.quit()

    def cook_songlist_page(self, index=None):
        if index is None:
            self.driver.get(self.baseurl)
        else:
            self.driver.get(f'{self.baseurl}/?page={index+1}')
        ranked = self.driver.find_element_by_xpath("//input[@id='ranked']")
        if self.unranked:
            if ranked.is_selected() is True:
                ranked.click()  # disable ranked option
        else:
            if ranked.is_selected() is not True:
                ranked.click()  # Enalbe ranked option
        cats = self.driver.find_element_by_xpath("//select[@id='cats']")
        cats = Select(cats)
        cats.select_by_visible_text("Date Ranked")
        time.sleep(5)
        self.driver.find_element_by_xpath(".//input[@type='radio' and @id='asc']").click()
        maxstar = self.driver.find_element_by_xpath("//input[@id='sliderWithValue']")
        # maxstar.send_keys("50")
        starmove = ActionChains(self.driver)
        starmove.click_and_hold(maxstar).move_by_offset(300, 0).release().perform()
        update_button = self.driver.find_element_by_xpath("//button[@onclick='if (!window.__cfRLUnblockHandlers) return false; onToggle2()']")
        update_button.click()
        time.sleep(5)
        soup = None
        counter = 0
        while soup is None and counter < self.maxretry:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            time.sleep(self.intervalf())
            counter += 1
            try:
                links = self.extract_links(soup)
                leaderboards = self.find_leaderborads(links)
                if len(leaderboards) == 0:
                    soup = None
                    leaderboards = None
            except:
                soup = None
        return links, leaderboards

    def cook_song_page(self, leaderboard):
        res = requests.get(self.baseurl + leaderboard)
        soup = None
        counter = 0
        while soup is None and counter < self.maxretry:
            soup = BeautifulSoup(res.text, 'html.parser')
            time.sleep(self.intervalf())
            counter += 1
            try:
                title, info = self.find_song_info(soup)
            except:
                soup = None
        return title, info

    def extract_links(self, soup):
        links = [url.get('href') for url in soup.find_all('a')]
        links = [link for link in links if link is not None]
        return links

    def find_num_pages(self, links):
        pages = [link for link in links if ("page" in link)]
        return int(pages[-1][6:])

    def find_leaderborads(self, links):
        leaderboards = [link for link in links if ("leaderboard" in link)]
        return leaderboards

    def find_active_level(self, soup):
        return soup.find('li', attrs={'class': 'is-active'}).get_text()

    def find_song_info(self, soup):
        infotype = ['Level', 'Mapped by', 'Status', 'Scores', 'Total Scores', 'Star Difficulty', 'Note Count', 'BPM', 'ID', 'PP']
        info = dict.fromkeys(infotype)

        title = soup.find('meta', attrs={'property': 'og:title'}).get('content')
        info['Level'] = self.find_active_level(soup)

        div = soup.find('div', attrs={"class": "column", "style": "padding: 6px;"})
        tmp = {infotype[i + 1]: b.get_text() for i, b in enumerate(div.find_all('b'))}
        info.update(tmp)

        if info['Star Difficulty'] is not None:  # ranked song
            info['Star Difficulty'] = info['Star Difficulty'][:-1]  # remove star icon
        else:  # unranked song
            info['Star Difficulty'] = '-'
        info['ID'] = re.findall(r'ID: +[A-Za-z0-9]*', soup.text)[0][4:]
        info['PP'] = re.findall(r'[0-9]+.[0-9]+pp', soup.text)[0][:-2]
        return title, info

    def find_beatsaver_info(self, title):
        self.driver.get(f'https://beatsaver.com/?q={title}&ranked=true')
        time.sleep(self.intervalf() / 2)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        try:
            song_key = soup.findAll('div', attrs={'class': 'info'})[0].find_all('a')[0].get('href').split('/')[-1]
        except:
            return None

        self.driver.get(f'https://beatsaver.com/maps/{song_key}')
        time.sleep(self.intervalf() / 2)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        ranks = soup.findAll('div', attrs={'class': 'list-group mapstats'})[0].get_text(' ').split(' ')
        ranks = [r for r in ranks if r in ['Expert+', 'Expert', 'Hard', 'Normal', 'Easy']]
        details = soup.findAll('div', attrs={'class': 'stats'})
        # tags = ['Stars', 'Notes', 'Bombs', 'Walls', 'Note jump speed', 'Notes per second', 'Lights']
        tags = ['Bombs', 'Walls', 'Note jump speed', 'Notes per second', 'Lights']
        info = {}
        for rank, detail in zip(ranks, details):
            detail = detail.get_text(' ').split(' ')[2:] # remove stars and notes since we already know that
            if 'k' in detail[-1]:
                detail[-1] = float(detail[-1][:-1]) * 1000
            info[rank] = dict(zip(tags, detail))
        return song_key, info

    def to_dataframe(self):
        properties = ['Title', 'Mapped by', 'Level', 'Status', 'Scores', 'Total Scores', 'Star Difficulty',
                      'Note Count', 'BPM', 'PP', 'Key', 'Bombs', 'Walls', 'Note jump speed', 'Notes per second', 'Lights', 'ID']
        db = self.song_database  # copy
        songdf = pd.DataFrame(columns=properties)
        for title in db.keys():
            song = db[title]
            for s in song:
                s['Title'] = title
                if s['Key'] is not None:
                    s['Key'] = '!bsr ' + s['Key']
                tmp = pd.DataFrame.from_dict(s, orient='index').T
                songdf = songdf.append(tmp, ignore_index=True)
        return songdf

    def scrape(self, pagerange=None):
        if self.restart is False:
            self.song_database = {}
        if pagerange is not None:
            itr = pagerange
        else:
            itr = range(self.previous, self.pages)
        for pageindex in itr:  # scrape from scoresaber
            print(f'Scraping Page: {pageindex+1:03}/{self.pages:03}')
            links, leaderboards = self.cook_songlist_page(pageindex)
            for song in tqdm(leaderboards):
                title, info = self.cook_song_page(song)
                if title in self.song_database.keys():
                    self.song_database[title].append(info)
                else:
                    self.song_database[title] = [info]
            try:
                os.remove(f'./tmp/{pageindex:04}.json')
            except:
                pass
            with open(f'./tmp/{pageindex+1:04}.json', 'w') as f:  # store temporary database
                json.dump(self.song_database, f)
        print('Scraping additional information from Beatsaver...')
        for title in tqdm(self.song_database.keys()):  # scrape from beatsaver
            song = self.song_database[title]
            try:
                key, info = self.find_beatsaver_info(title)
            except:
                key = None
            if key is not None:
                for s in song:
                    s.update({'Key': key})
                    try:
                        s.update(info[s['Level']])
                    except:
                        pass
            else:
                for s in song:
                    s.update({'Key': None})


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--unranked', help='Scrape unranked songs too', action='store_true')
    parser.add_argument('-v', '--view', help='Show the browser', action='store_true')
    parser.add_argument('-r', '--restart', help='Restart from temporary files', action='store_true')
    parser.add_argument('-i', '--interval', help='Interval of scraping (Default:5, and it must be bigger than 1.5)', type=float, default=5.)
    args = parser.parse_args()
    return args


def check_new_songs(scraper):
    try:
        with open('database/song_db.json', 'r') as f:
            before = set(json.load(f).keys())
    except:
        return None
    after = set(scraper.song_database.keys())
    return list(after - before)


def main():
    args = setup()
    os.makedirs('./tmp', exist_ok=True)
    os.makedirs('./database', exist_ok=True)
    scraper = scoresaber_scraper(interval=args.interval, unranked=args.unranked, headless=not(args.view), restart=args.restart)
    scraper.scrape()
    # Print new songs if it exists
    new_songs = check_new_songs(scraper)
    if len(new_songs) > 0:
        print('New songs have been detected!')
        for s in new_songs:
            print(s)
        try:
            with open('./database/newsongs', 'w') as f:
                f.write(', '.join(new_songs))
            with open('./database/newsongs4tw', 'w') as f:
                f.write('\n'.join(new_songs))
        except:
            pass
    else:
        print("No new songs.")
    # Original json database
    with open('./database/song_db.json', 'w') as f:
        json.dump(scraper.song_database, f)
    # Flattened csv table
    songdf = scraper.to_dataframe()
    songdf.to_csv('./database/song_db.csv', index=False)


if __name__ == '__main__':
    main()
