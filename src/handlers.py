
from tornado import web, template, websocket
from common import get_db, LEVELS, json_
from pymongo import DESCENDING

index_template = template.Template(
  open('web/html/logfire.html','r').read(), autoescape='')

db = get_db()

components = db.distinct('comp')
rt_subscribers = []

class MainHandler(web.RequestHandler):
  def get(self):
    params = dict(
      components = components,
      levels = LEVELS.keys(),
    )
    self.write(index_template.generate(**params))

  def post(self):
    components = self.get_argument('components', None)
    levels = self.get_argument('levels', None)
    limit = self.get_argument('limit', 25)
    offset = self.get_argument('offset', 0)
    spec = dict()
    if components:
      comp = map(str, components.split(','))
      spec['comp'] = {'$in':comp}
    if levels:
      lvl = map(lambda x: LEVELS[x], levels.split(','))
      spec['lvl'] = {'$in':lvl}
    rows = [
      dict(
        tstamp = str(r['tstamp']),
        lvl = r['lvl'],
        comp = r['comp'],
        msg = r['msg'],
      ) for r in db 
        .find(spec, skip=int(offset), limit=int(limit))
        .sort('tstamp',direction=DESCENDING)]

    self.write(dict(result='SUCCESS',rows=rows))

  def get_cache_time(self, path, modified, mime_type):
    return 0

def tailThread():
  global rt_subscribers
  from time import sleep
  spec = dict()
  cursor = db.find(spec,tailable=True)
  while cursor.alive:
    try:
      doc=cursor.next()
      for rt_sub in rt_subscribers:
        rt_sub.write_message(json_(
          comp=doc['comp'],lvl=doc['lvl'],
          msg=doc['msg'],tstamp=str(doc['tstamp'])))
    except StopIteration:
      sleep(1)

class RTHandler(websocket.WebSocketHandler):
  def open(self):
    global rt_subscribers
    rt_subscribers.append(self)
    from threading import Thread
    Thread(target=tailThread).start()

  def on_message(self, message):
    pass

  def on_close(self):
    global rt_subscribers
    rt_subscribers.remove(self)
