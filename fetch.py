import json
import youtube_dl
import sqlite3


VEVOWATCH = 'https://www.vevo.com/watch/'
ITERATIONS = 500


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print('ERROR: ' + msg)


def my_hook(d):
    if d['status'] == 'finished':
        conn = sqlite3.connect('finished.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, isrc INTEGER UNIQUE)')
        cur.execute('INSERT INTO videos (isrc) VALUES (?)', (d['filename'][-16:-4],))
        conn.commit()
        conn.close()
        print('finished ' + d['filename'][-16:-4])
    elif d['status'] == 'downloading':
        speed = 0
        index = 0
        count = 0
        if d.get('speed'):
            speed = int(d.get('speed') * 8 / 1024)
        if d.get('fragment_index'):
            index = d.get('fragment_index')
        if d.get('fragment_count'):
            count = d.get('fragment_count')
        print(str(index) + '/' + str(count) + ' ' + str(speed) + 'kBit')


def main():
    count = 0
    with open('vevo.json', 'r') as file:
        isrclist = json.load(file)
        for entry in isrclist.values():
            conn = sqlite3.connect('finished.db')
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, isrc INTEGER UNIQUE)')
            conn.commit()
            cur.execute('SELECT isrc FROM videos WHERE isrc = :isrc', {'isrc': entry})
            stuff = cur.fetchall()
            if len(stuff) > 0:
                print('skipping ' + entry)
                conn.close()
                continue
            conn.close()
            print('downloading ' + entry)
            ydl_opts = {'logger': MyLogger(),
                        'progress_hooks': [my_hook],
                        'outtmpl': 'videos/%(title)s-%(id)s.%(ext)s',
                        'updatetime': True
                        }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([VEVOWATCH + entry])
                except:
                    with open('failed.txt', 'a') as file:
                        file.write(entry + '\n')
            count = count + 1
            if count == ITERATIONS:
                break


if __name__ == '__main__':
    main()
