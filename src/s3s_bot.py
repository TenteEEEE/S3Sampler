import re
import json
import time
import requests
import argparse
from requests_oauthlib import OAuth1Session


class twitter:
    def __init__(self, secret, is_debug=False):
        self.client = OAuth1Session(secret['API-KEY'], secret['API-SECRET'], secret['ACESS-TOKEN'], secret['ACESS-TOKEN-SECRET'])
        self.master_url = "https://api.github.com/repos/tenteeeee/s3sampler/branches/master"
        with open('database/song_db.json', 'r') as f:
            self.db = json.load(f)
        time.sleep(5)
        self.commit_msg = self.get_commit_msg()
        print('Commit Message: ' + self.commit_msg)
        self.is_debug = is_debug

    def tweet(self, msg):
        print('Tweet:' + msg)
        if self.is_debug is False:
            url = "https://api.twitter.com/1.1/statuses/update.json"
            params = {"status": msg}
            time.sleep(3)
            res = self.client.post(url, params=params)
            if res.status_code == 200:
                return 1
            else:
                return 0

    def get_commit_msg(self):
        res = requests.get(self.master_url)
        github_info = json.loads(res.content)
        msg = github_info['commit']['commit']['message']
        return msg

    def find_songs(self, msg):
        date = re.search(r'[0-9]{8}', msg)
        try:
            msg = msg[date.span()[-1] + 6:]  # 6: removes ". New:"
        except:
            return None
        songs = msg.split(', ')
        if songs[0] != '':
            return songs
        else:
            return None

    def make_song_tweet(self, name):
        song = self.db[name][0]
        song['Title'] = name
        print(song)
        return f"New Ranked Song! {song['Title']}, {song['Star Difficulty']}★, PP:{song['PP']} https://beatsaver.com/beatmap/{song['Key']} #NewRankedSong"

    def notify(self):
        if 'updated' in self.commit_msg:
            self.tweet("Ranked Song Database has been updated. https://docs.google.com/spreadsheets/d/1NZpCVfejZgJBtrJL0AukMz4KODm_MKKEPhxN9CR34BE/edit?usp=sharing")
            songs = self.find_songs(self.commit_msg)
            if songs is None:
                return
            for name in songs:
                msg = self.make_song_tweet(name)
                self.tweet(msg)


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='is_debug mode', action='store_true')
    parser.add_argument('-m', '--manual', help='tweet a song manually', type=str)
    parser.add_argument('-l', '--list', help='tweet using a song list', type=str)
    args = parser.parse_args()
    return args


def main(args):
    with open('secret.json', 'r') as f:
        secret = json.load(f)
    tw = twitter(secret, is_debug=args.debug)
    if args.manual is not None:
        msg = tw.make_song_tweet(args.manual)
        tw.tweet(msg)
    elif args.list is not None:
        with open(args.list, 'r') as f:
            songs = f.readlines()
        for s in songs:
            msg = tw.make_song_tweet(s.rstrip("\n"))
            tw.tweet(msg)
    else:
        tw.notify()


if __name__ == '__main__':
    args = setup()
    main(args)
