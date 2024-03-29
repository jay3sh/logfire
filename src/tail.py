
from common import get_db
from time import sleep

def tail(args):

  db = get_db(args.mongohost)
  spec = dict()
  if args.comp:
    spec['comp'] = args.comp

  total = db.find(spec).count()
  cursor = db.find(spec,tailable=True).skip(max(0,total-10))
  while cursor.alive:
    try:
      doc=cursor.next()
      print '' if args.comp else doc['comp'],doc['lvl'],doc['msg']
    except StopIteration:
      sleep(1)
