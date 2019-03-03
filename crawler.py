import os
import json
import time
import traceback
import pituophis

# Ignored types
ignore_types = ['i', '3', 'h']
crawl_types = ['1']

robotstxt = {}
db = {'menus': {}, 'selectors': {}}

pathmuststartwith = '/'
limithost = False
onlyrecordhost = True

dbfilename = 'db.json'
delay = 10

if os.path.isfile(dbfilename):
    with open(dbfilename, 'r') as fp:
        db = json.load(fp)


def save():
    db_out = json.dumps(db, indent=4)
    with open(dbfilename, 'w') as outfile:
        outfile.write(db_out)
        outfile.close()
    print('Saved!')


def allowed_to_crawl(url):
    req = pituophis.parse_url(url)
    if req.host not in robotstxt:
        try:
            resp = req.get()
            robotstxt[req.host] = resp.text()
        except:
            robotstxt[req.host] = ''
    robots = robotstxt[req.host]
    allowed = True
    for line in robots.replace('\r\n', '\n').split('\n'):
        if line.startswith('Disallow:'):
            line = line.replace('Disallow: ', '').replace('Disallow:', '').strip('/')
            if line in req.path:
                allowed = False
    if allowed:
        if ('Disallow: ' + req.path) in robots:
            allowed = False
        else:
            if 'Disallow: *' in robots:
                allowed = False
    return allowed


def crawl(url, cooldown=(86400 * 1)):
    tocrawl = []
    req = pituophis.parse_url(url)
    if req.url() in db['menus']:
        if not (time.time() >= (db['menus'][req.url()]['last_crawled'] + cooldown)):
            print('Not crawling', url, 'due to', str(cooldown) + 'ms cooldown')
            return False
    try:
        if limithost:
            if not limithost == req.host:
                return False
        if not req.path.startswith(pathmuststartwith):
            return False
        save()
        if req.type in crawl_types:
            if allowed_to_crawl(req.url()):
                print('Waiting to crawl', req.url() + '...')
                time.sleep(delay)
                resp = req.get()
                print('Crawling ' + req.url())
                db['menus'][req.url()] = {'last_crawled': 0}
                dead = False
                for selector in resp.menu():
                    if selector.type not in ignore_types:
                        surl = selector.request().url()
                        record = True
                        if limithost:
                            if onlyrecordhost:
                                if not selector.request().host == limithost:
                                    record = False
                        if not req.path.startswith(pathmuststartwith):
                            record = False
                        if record:
                            print('Recording selector for URL', surl)
                            # record!
                            if surl not in db['selectors']:
                                db['selectors'][surl] = {}
                                db['selectors'][surl]['titles'] = []
                                db['selectors'][surl]['referrers'] = []
                            if selector.text not in db['selectors'][surl]['titles']:
                                db['selectors'][surl]['titles'].append(selector.text)
                            if req.url() not in db['selectors'][surl]['referrers']:
                                db['selectors'][surl]['referrers'].append(req.url())
                            # if it's a crawl type, let's do that uwu
                            if selector.type in crawl_types:
                                tocrawl.append(selector.request().url())
                    if selector.type == '3':
                        dead = True
                if dead:
                    db['menus'].pop(req.url(), None)
                    db['selectors'].pop(req.url(), None)
                else:
                    db['menus'][req.url()] = {'last_crawled': time.time()}
                save()
                for tc in tocrawl:
                    crawl(tc)
                    save()
    except Exception:
        print('WARN: Failed to fetch', req.url())
        traceback.print_exc()
        db['menus'].pop(req.url(), None)
        db['selectors'].pop(req.url(), None)


for key in db['menus'].copy().keys():
    crawl(key)

for selector in db['selectors'].copy().keys():
    req = pituophis.parse_url(selector)
    if req.type == '1':
        crawl(selector)

save()
