import urllib.parse
import urllib.request
import urllib.response
import zlib
import json
import os.path
import glob


USERAGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64) ' \
            'AppleWebKit/537.36 (KHTML, like Gecko) ' \
            'Chrome/41.0.2272.101 Safari/537.36'
VEVOAPI = 'https://apiv2.vevo.com'
VEVOAUTH = 'https://www.vevo.com/auth'
VEVOWATCH = 'https://www.vevo.com/watch/'
VEVOKEY = 'SPupX1tvqFEopQ1YS6SS'
USERNAME = ''
PASSWORD = ''
ARTISTURL = VEVOAPI + '/artists?page=1&size=200'
VIDEOURL = VEVOAPI + '/artist/{}/videos?page=1&size=200'


class VevoApi:

    defaultheaders = {'User-Agent': USERAGENT,
                      'Accept': "application/json, text/javascript, text/html,*/*",
                      'Accept-Encoding': 'gzip,deflate,sdch',
                      'Accept-Language': 'en-US,en;q=0.8'
                      }

    def log(self, txt):
        try:
            print(txt)
        except:
            pass

    def getrequest(self, url, udata=None, headers=defaultheaders, dopost=False):
        # self.log('getrequest URL: ' + str(url))
        # self.log('getrequest headers: ' + str(headers))
        req = urllib.request.Request(url, udata, headers)
        if dopost:
            method = 'POST'
            req.get_method = lambda: method
        # try:
        response = urllib.request.urlopen(req)
        page = response.read()
        if response.info().get('Content-Encoding') == 'gzip':
            page = zlib.decompress(page, zlib.MAX_WBITS + 16)
        page = page.decode(encoding='utf-8')
        # except:
        #     page = ''
        return page

    def getautho(self, test=False):
        udata = urllib.parse.urlencode({'username': USERNAME,
                                        'password': PASSWORD,
                                        'grant_type': 'password',
                                        'client_id': VEVOKEY,
                                        }).encode(encoding='utf-8')
        uheaders = self.defaultheaders.copy()
        uheaders['X-Requested-With'] = 'XMLHttpRequest'
        uheaders['Connection'] = 'keep-alive'
        # url = 'https://accounts.vevo.com/token'
        url = VEVOAUTH
        html = self.getrequest(url, udata, uheaders)
        a = json.loads(html)
        if not test:
            return a['access_token']
        # in test mode we can do whatever to test the api
        uheaders['Authorization'] = 'Bearer %s' % a['access_token']
        html = self.getrequest(VEVOAPI + '/artist/anna-d/videos?size=50&page=1&sort=MostRecent&token={}'.format(a['access_token']), None, uheaders)
        # html = self.getrequest(VEVOAPI + '/artists?page=1&size=200&token={}'.format(a['access_token']), None, uheaders)
        b = json.loads(html)
        self.log('me:')
        self.log(b)
        return a['access_token']

    def getapi(self, token, url, filename, mode):
        url = url + '&token={}'.format(token)
        html = self.getrequest(url, None, self.defaultheaders)
        apidata = json.loads(html)
        with open(filename, 'a') as file:
            for entry in apidata[mode]:
                tag = None
                if mode == 'artists':
                    tag = 'urlSafeName'
                elif mode == 'videos':
                    tag = 'isrc'
                file.write(entry[tag] + '\n')
        if apidata.get('paging'):
            if apidata['paging'].get('next'):
                self.getapi(token, apidata['paging'].get('next'), filename, mode)


def main():
    vevo = VevoApi()
    # authorize against vevo first
    token = vevo.getautho()
    # get a list of every artist and write it to a file
    vevo.getapi(token, ARTISTURL, 'artists.list', 'artists')
    # now go through each artist and write out all of their video isrc ids to a file
    with open('artists.list', 'r') as file:
        for line in file:
            print(line[:-1])
            if os.path.isfile(line[:-1] + '.txt'):
                print('skipping')
                continue
            vevo.getapi(token, VIDEOURL.format(urllib.parse.quote(line[:-1])), line[:-1] + '.txt', 'videos')
    # FIXME: there is one artist called ???-??????? and of course you cant use that as a filename
    # vevo.getapi(token, VIDEOURL.format(urllib.parse.quote('???-???????')), 'QQQ-QQQQQQQ' + '.txt', 'videos')
    # parse each of the files and combine them into one list without duplicates
    print('collecting isrc values')
    videos = glob.glob('*.txt')
    isrclist = set()
    for filename in videos:
        with open(filename, 'r') as file:
            for line in file:
                # print(line[:-1])
                isrclist.add(line[:-1])
    print(str(len(isrclist)) + ' entries')
    jsonlist = dict()
    count = 0
    # dump the whole list into a json object in a file
    print('creating json object')
    for entry in isrclist:
        jsonlist.update({count: entry})
        count = count + 1
    # print(jsonlist)
    with open('vevo.json', 'w') as file:
        json.dump(jsonlist, file)
    print('finished')


if __name__ == '__main__':
    main()
