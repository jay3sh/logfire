
import json
from pymongo import Connection

LEVELS = [ 'DEBUG', 'INFO', 'NOTICE', 'WARNING', 'ERROR' ]

db = None

def get_db(mongohost=None):
  global db
  if db: return db
  if mongohost:
    hostname, port = mongohost.split(':')
    port = int(port)
  else:
    hostname = 'localhost'
    port = 27017
  conn = Connection(hostname, port)
  db = conn['LOGFIRE'].LOGS
  return db

def json_(**kwds):
  return json.dumps(kwds)


rt_subscribers = {}
stop_signal = {}
