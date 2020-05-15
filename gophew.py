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
        menu.append(pituophis.Item(itype='1', text='Back to Gophew!', path='/', host=request.host, port=request.port))
        menu.append(pituophis.Item(itype='7', text='Try another search', path='/search', host=request.host, port=request.port))
        if not request.path == '/search':
            menu.append(pituophis.Item(itype='7', text='Try another search with the same criteria', path=request.path, host=request.host, port=request.port))
        menu.append(pituophis.Item(text='Results for ' + "'" + request.query + "' (out of " + str(len(db['items'])) + ')'))
        if len(types):
            menu.append(pituophis.Item(text='Filtering types: ' + (', '.join(types))))
        Items = db['items']
        for Item in Items:
            sampling = Item
            for title in db['items'][Item]['titles']:
                sampling += title
            if request.query.lower() in sampling.lower():
                req = pituophis.parse_url(Item)
                yes = False
                if len(types) == 0:
                    yes = True
                else:
                    if req.type in types:
                        yes = True
                if yes:
                    try:
                        menu.append(pituophis.Item(text=''))
                        menu.append(pituophis.Item(itype=req.type, text=Items[Item]['titles'][0], path=req.path, host=req.host, port=req.port))
                        menu.append(pituophis.Item(text='URL: ' + req.url()))
                        if len(Items[Item]['titles']) > 1:
                            menu.append(pituophis.Item(text='Alternate titles:'))
                            for title in Items[Item]['titles'][1:]:
                                menu.append(pituophis.Item(text='  ' + title))
                            menu.append(pituophis.Item(text='Referred by:'))
                            for referrer in Items[Item]['referrers']:
                                menu.append(pituophis.Item(text='  ' + referrer))
                    except:
                        print()
        return menu
    else:
        return 'What?'


pituophis.serve("127.0.0.1", 70, pub_dir='pub/', alt_handler=alt)  # typical Gopher port is 70
