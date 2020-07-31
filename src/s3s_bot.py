import re
import json
import time
import requests
import argparse
from requests_oauthlib import OAuth1Session


class twitter:
    def __init__(self, secret, debug=False):
        self.client = OAuth1Session(secret['API-KEY'], secret['API-SECRET'], secret['ACESS-TOKEN'], secret['ACESS-TOKEN-SECRET'])
        self.master_url = "https://api.github.com/repos/tenteeeee/s3sampler/branches/master"
        with open('database/song_db.json', 'r') as f:
            self.db = json.load(f)
        time.sleep(5)
        self.commit_msg = self.get_commit_msg()
        print(self.commit_msg)
        self.debug = debug

    def tweet(self, msg):
        if self.debug is False:
            url = "https://api.twitter.com/1.1/statuses/update.json"
            params = {"status": msg}
            time.sleep(3)
            res = self.client.post(url, params=params)
            if res.status_code == 200:
                return 1
            else:
                return 0
        else:
            print(msg)

    def get_commit_msg(self):
        res = requests.get(self.master_url)
        github_info = json.loads(res.content)
        msg = github_info['commit']['commit']['message']
        return msg

    def find_songs(self, msg):
        date = re.search(r'[0-9]{8}', msg)
        try:
            msg = msg[date.span()[-1] + 2:]
        except:
            return None
        songs = msg.split(', ')
        if songs[0] != '':
            return songs
        else:
            return None

    def make_tweet_msg(self, song):
        return f"New Ranked Song! {song['Title']} https://beatsaver.com/beatmap/{song['Key']} #NewRankedSong"

    def notify(self):
        self.tweet("Ranked Song Database has been updated: https://docs.google.com/spreadsheets/d/1NZpCVfejZgJBtrJL0AukMz4KODm_MKKEPhxN9CR34BE/edit?usp=sharing")
        songs = self.find_songs(self.commit_msg)
        if songs is None:
            return
        for name in songs:
            song = self.db[name][0]
            song['Title'] = name
            msg = self.make_tweet_msg(song)
            self.tweet(msg)


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
    args = parser.parse_args()
    return args


def main(args):
    with open('secret.json', 'r') as f:
        secret = json.load(f)
    tw = twitter(secret, debug=args.debug)
    tw.notify()


if __name__ == '__main__':
    args = setup()
    main(args)
