


def serve(args):
  from tornado import ioloop, web, template, websocket

  from common import get_db
  get_db(args.mongohost)

  from handlers import MainHandler, RTHandler, GoogleAuthHandler

  if args.authgmaillist and not args.cookiesecret:
    print '--cookiesecret required with --authgmaillist'
    return

  settings = dict(
    debug = True,
    cookie_secret = args.cookiesecret,
    authgmaillist = args.authgmaillist.split(',') if args.authgmaillist else []
  )
  handler_list = [
    ( '/', MainHandler ),
    ( '/login', GoogleAuthHandler ),
    ( '/rt', RTHandler ),
    ( '/web/(.*)', web.StaticFileHandler, {"path": "./web"}),
  ]
  application = web.Application(handler_list, **settings)
  application.listen(int(args.port))
  ioloop.IOLoop.instance().start()

