
from common import get_db
from time import sleep

def tail(args):
  db = get_db()

  spec = dict()
  if args.comp:
    spec['comp'] = args.comp

  cursor = db.find(spec,tailable=True)
  while cursor.alive:
    try:
      doc=cursor.next()
      print '' if args.comp else doc['comp'],doc['lvl'],doc['msg']
    except StopIteration:
      sleep(1)
