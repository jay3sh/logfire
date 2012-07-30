
import json
import thread
from threading import Thread
from tornado import web, auth, template, websocket
from common import get_db, LEVELS, json_, stop_signal
from pymongo import DESCENDING

index_template = template.Template(
  open('web/html/logfire.html','r').read(), autoescape='')

db = get_db()

components = db.distinct('comp')
levels = map(lambda x: LEVELS[x], db.distinct('lvl'))

class MainHandler(web.RequestHandler):
  def get(self):

    authgmaillist = self.application.settings['authgmaillist']

    # Check if Authorization is required
    if len(authgmaillist) > 0:
      usergmail = self.get_secure_cookie('_userid_')
      if not usergmail:
        self.redirect('/login')
        return

      if usergmail not in authgmaillist:
        raise web.HTTPError(403, 'You are not authorized')

    params = dict(
      components = components,
      levels = levels,
    )
    self.write(index_template.generate(**params))

def tailThread(spec=None, handler=None):
  from time import sleep
  myid = str(thread.get_ident())

  total = db.find(spec).count()
  cursor = db.find(spec,tailable=True).skip(max(0,total-10))
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

    if msg['cmd'] == 'onetime':

      limit = self.get_argument('limit', 25)
      offset = self.get_argument('offset', 0)
      spec = self.makeSpec(msg['comp'],msg['lvl'])
      docs = [
        dict(
          tstamp = str(r['tstamp']),
          lvl = r['lvl'],
          comp = r['comp'],
          msg = r['msg'],
        ) for r in db 
          .find(spec, skip=int(offset), limit=int(limit))
          .sort('tstamp',direction=DESCENDING)]

      for doc in reversed(docs):
        self.write_message(json_(
          comp=doc['comp'],
          lvl=doc['lvl'],
          msg=doc['msg'],
          tstamp=str(doc['tstamp'])))

    if msg['cmd'] == 'startRT':

      # Stop current poller thread
      if self.poller_id:
        stop_signal[self.poller_id] = True 
        self.poller.join()

      # Start new poller thread with modified spec
      spec = self.makeSpec(msg['comp'],msg['lvl'])
      self.poller = Thread(target=tailThread,
        kwargs=dict(spec=spec,handler=self))
      self.poller.daemon = True
      self.poller.start()
      self.poller_id = str(self.poller.ident)
      stop_signal[self.poller_id] = False

    elif msg['cmd'] == 'stopRT':

      # Stop current poller thread
      if self.poller_id:
        stop_signal[self.poller_id] = True 
        self.poller.join()


  def on_close(self):
    stop_signal[self.poller_id] = True


class GoogleAuthHandler(
  web.RequestHandler, auth.GoogleMixin):
  @web.asynchronous
  def get(self):
    if self.get_argument("openid.mode", None):
      self.get_authenticated_user(self.async_callback(self._on_auth))
      return
    self.authenticate_redirect()

  def _on_auth(self, user):
    if not user:
      print 'No GMail ID found'
      raise web.HTTPError(500)
 
    self.set_secure_cookie("_userid_", user['email'])
    self.redirect('/')
