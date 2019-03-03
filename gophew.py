import os
import json
import pituophis

if os.path.isfile('db.json'):
    with open('db.json', 'r') as fp:
        db = json.load(fp)

def alt(request):
    if request.path.startswith('/search'):
        typestring = request.path.replace('/search', '').replace('/', '')
        types = list(typestring)
        menu = []
        menu.append(pituophis.Selector(itype='1', text='Back to Gophew!', path='/', host=request.host, port=request.port))
        menu.append(pituophis.Selector(itype='7', text='Try another search', path='/search', host=request.host, port=request.port))
        if not request.path == '/search':
            menu.append(pituophis.Selector(itype='7', text='Try another search with the same criteria', path=request.path, host=request.host, port=request.port))
        menu.append(pituophis.Selector(text='Results for ' + "'" + request.query + "' (out of " + str(len(db['selectors'])) + ')'))
        if len(types):
            menu.append(pituophis.Selector(text='Filtering types: ' + (', '.join(types))))
        selectors = db['selectors']
        for selector in selectors:
            sampling = selector
            for title in db['selectors'][selector]['titles']:
                sampling += title
            if request.query.lower() in sampling.lower():
                req = pituophis.parse_url(selector)
                yes = False
                if len(types) == 0:
                    yes = True
                else:
                    if req.type in types:
                        yes = True
                if yes:
                    try:
                        menu.append(pituophis.Selector(text=''))
                        menu.append(pituophis.Selector(itype=req.type, text=selectors[selector]['titles'][0], path=req.path, host=req.host, port=req.port))
                        menu.append(pituophis.Selector(text='URL: ' + req.url()))
                        if len(selectors[selector]['titles']) > 1:
                            menu.append(pituophis.Selector(text='Alternate titles:'))
                            for title in selectors[selector]['titles'][1:]:
                                menu.append(pituophis.Selector(text='  ' + title))
                            menu.append(pituophis.Selector(text='Referred by:'))
                            for referrer in selectors[selector]['referrers']:
                                menu.append(pituophis.Selector(text='  ' + referrer))
                    except:
                        print()
        return menu
    else:
        return 'What?'


pituophis.serve("127.0.0.1", 1337, pub_dir='pub/', alt_handler=alt, tls=False)  # typical Gopher port is 70
