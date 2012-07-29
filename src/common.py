
from pymongo import Connection,DESCENDING

LEVELS = dict(
  DEBUG   = 0,
  INFO    = 1,
  NOTICE  = 2,
  WARNING = 3,
  ERROR   = 4,
)

def get_db():
  conn = Connection('localhost', 27017)
  db = conn['LOGFIRE']
  return db.LOGS
