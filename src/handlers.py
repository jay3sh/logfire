
import thread
from tornado import web, template, websocket
from common import get_db, LEVELS, json_, rt_subscribers, stop_signal
from pymongo import DESCENDING

index_template = template.Template(
  open('web/html/logfire.html','r').read(), autoescape='')

db = get_db()

components = db.distinct('comp')
levels = map(lambda x: LEVELS[x], db.distinct('lvl'))

class MainHandler(web.RequestHandler):
  def get(self):
    params = dict(
      components = components,
      levels = levels,
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
  from time import sleep
  spec = dict()
  cursor = db.find(spec,tailable=True)
  myid = str(thread.get_ident())
  while cursor.alive:
    if stop_signal.has_key(myid):
      del stop_signal[myid]
      break
    try:
      doc=cursor.next()
      handler = rt_subscribers[myid]
      handler.write_message(json_(
        comp=doc['comp'],lvl=doc['lvl'],
        msg=doc['msg'],tstamp=str(doc['tstamp'])))
    except StopIteration:
      sleep(1)

class RTHandler(websocket.WebSocketHandler):
  def open(self):
    from threading import Thread
    self.poller = Thread(target=tailThread)
    self.poller.daemon = True
    self.poller.start()
    self.poller_id = str(self.poller.ident)
    rt_subscribers[self.poller_id] = self

  def on_message(self, message):
    pass

  def on_close(self):
    del rt_subscribers[self.poller_id]
    stop_signal[self.poller_id] = True
