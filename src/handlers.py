
import json
import thread
from threading import Thread
from tornado import web, template, websocket
from common import get_db, LEVELS, json_,\
  rt_subscribers, stop_signal, poller_specs
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

  '''
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
  '''

def tailThread(spec=None, handler=None):
  from time import sleep
  myid = str(thread.get_ident())

  cursor = db.find(spec,tailable=True)
  while cursor.alive:
    if stop_signal.has_key(myid) and stop_signal[myid]:
      del stop_signal[myid]
      break
    try:
      doc=cursor.next()
      handler.write_message(json_(
        comp=doc['comp'],
        lvl=doc['lvl'],
        msg=doc['msg'],
        tstamp=str(doc['tstamp'])))
    except StopIteration:
      sleep(1)

class RTHandler(websocket.WebSocketHandler):

  def makeSpec(self, components, levels):
    spec = dict()
    if components:
      comp = map(str, components.split(','))
      spec['comp'] = {'$in':comp}
    if levels:
      lvl = map(lambda x: LEVELS.index(x), levels.split(','))
      spec['lvl'] = {'$in':lvl}
    return spec

  def open(self):
    self.poller_id = None

  def on_message(self, message):
    msg = json.loads(message)
    if msg['cmd'] == 'refresh':

      # Stop current poller thread
      if self.poller_id:
        stop_signal[self.poller_id] = True 
        self.poller.join()

      spec = self.makeSpec(msg['comp'],msg['lvl'])
      self.poller = Thread(target=tailThread,
        kwargs=dict(spec=spec,handler=self))
      self.poller.daemon = True
      self.poller.start()
      self.poller_id = str(self.poller.ident)
      stop_signal[self.poller_id] = False

  def on_close(self):
    del rt_subscribers[self.poller_id]
    stop_signal[self.poller_id] = True
