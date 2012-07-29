
import json
from pymongo import Connection

LEVELS = [ 'DEBUG', 'INFO', 'NOTICE', 'WARNING', 'ERROR' ]

def get_db():
  conn = Connection('localhost', 27017)
  db = conn['LOGFIRE']
  return db.LOGS

def json_(**kwds):
  return json.dumps(kwds)


rt_subscribers = {}
stop_signal = {}
