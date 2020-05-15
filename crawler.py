import os
import json
import time
import traceback
import pituophis

###########################

settings = {
    'limit_host': 'your.live.host',  # Host to limit to (for indexing single servers, which is highly recommended)
    'only_record_host': True,
    'path_must_start_with': '/',  # What the path/selector must start with
    'db_filename': 'db.json',  # Filename to use for the database
    'delay': 2,  # x second delay between grabbing files; please be courteous to servers you don't own! 
    'crawl_url': 'gopher://your.live.host/1/',  # URL to crawl (after finished updating the index)
    'cooldown': 86400,  # Required cooldown in ms before crawling a URL again
    'ignore_types': ['i', '3']  # Types of items that should be ignored and not recorded
}

###########################

crawl_types = ['1']

robotstxt = {}
db = {'menus': {}, 'items': {}}

if os.path.isfile(settings['db_filename']):
    with open(settings['db_filename'], 'r') as fp:
        db = json.load(fp)


def save():
    db_out = json.dumps(db, indent=4)
    with open(settings['db_filename'], 'w') as outfile:
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
            line = line.replace('Disallow: ', '').replace(
                'Disallow:', '').strip('/')
            if line in req.path:
                allowed = False
    if allowed:
        if ('Disallow: ' + req.path) in robots:
            allowed = False
        else:
            if 'Disallow: *' in robots:
                allowed = False
    return allowed


def crawl(url, cooldown=86400):
    tocrawl = []
    req = pituophis.parse_url(url)
    if req.url() in db['menus']:
        if not (time.time() >= (db['menus'][req.url()]['last_crawled'] + cooldown)):
            print('Not crawling', url, 'due to', str(cooldown) + 'ms cooldown')
            return False
    try:
        if settings['limit_host']:
            if not settings['limit_host'] == req.host:
                return False
        if not req.path.startswith(settings['path_must_start_with']):
            return False
        save()
        if req.type in crawl_types:
            if allowed_to_crawl(req.url()):
                print('Waiting to crawl', req.url() + '...')
                time.sleep(settings['delay'])
                resp = req.get()
                print('Crawling ' + req.url())
                db['menus'][req.url()] = {'last_crawled': 0}
                dead = False
                for item in resp.menu():
                    if item.type not in settings['ignore_types']:
                        surl = item.request().url()
                        record = True
                        if settings['limit_host']:
                            if settings['only_record_host']:
                                if not item.request().host == settings['limit_host']:
                                    record = False
                        if not req.path.startswith(settings['path_must_start_with']):
                            record = False
                        if '../' in surl:
                            record = False
                        if record:
                            print('Recording item for URL', surl)
                            # record!
                            if surl not in db['items']:
                                db['items'][surl] = {}
                                db['items'][surl]['titles'] = []
                                db['items'][surl]['referrers'] = []
                            if item.text not in db['items'][surl]['titles']:
                                db['items'][surl]['titles'].append(item.text)
                            if req.url() not in db['items'][surl]['referrers']:
                                db['items'][surl]['referrers'].append(
                                    req.url())
                            # if it's a crawl type, let's do that uwu
                            if item.type in crawl_types:
                                tocrawl.append(item.request().url())
                    if item.type == '3':
                        dead = True
                if dead:
                    db['menus'].pop(req.url(), None)
                    db['items'].pop(req.url(), None)
                else:
                    db['menus'][req.url()] = {'last_crawled': time.time()}
                save()
                for tc in tocrawl:
                    crawl(tc, settings['cooldown'])
                    save()
    except Exception:
        print('WARN: Failed to fetch', req.url())
        traceback.print_exc()
        db['menus'].pop(req.url(), None)
        db['items'].pop(req.url(), None)


for key in db['menus'].copy().keys():
    crawl(key, settings['cooldown'])

for item in db['items'].copy().keys():
    req = pituophis.parse_url(item)
    if req.type == '1':
        crawl(item, settings['cooldown'])

crawl(settings['crawl_url'], settings['cooldown'])
save()
