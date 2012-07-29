


def serve(args):
  from tornado import ioloop, web, template, websocket
  from handlers import MainHandler, RTHandler


  settings = dict(debug=True)
  handler_list = [
    ( '/', MainHandler ),
    ( '/rt', RTHandler ),
    ( '/web/(.*)', web.StaticFileHandler, {"path": "./web"}),
  ]
  application = web.Application(handler_list, **settings)
  application.listen(int(args.port))
  ioloop.IOLoop.instance().start()

