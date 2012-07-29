
import redis
import re
from common import get_db
from datetime import datetime

MSGPATTERN = re.compile('^(\w+)\|(\d)\|([\s\S]*)$')
CHANNEL = 'logfire'

def listen(args):

  global MSGPATTERN

  rserver = redis.Redis('localhost')
  rserver.subscribe(CHANNEL)

  db = get_db(args.mongohost)

  for packet in rserver.listen():
    try:
      if packet['type'] != 'message': continue
      match = MSGPATTERN.match(packet['data'])
      component = match.group(1)
      level = int(match.group(2))
      message = match.group(3)
      db.insert(dict(
        tstamp=datetime.now(),comp=component,lvl=level,msg=message))
    except Exception, e:
      print e, packet
