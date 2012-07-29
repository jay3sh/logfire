#!/usr/bin/env python

from argparse import ArgumentParser

from listen import listen
from serve import serve
from tail import tail

def main():
  parser = ArgumentParser(prog='logfire', usage='%(prog)s [options]')

  parser.add_argument('--listen',
    help="Listen for log messages published on Redis channel 'logfire'",
    nargs='?', default=False, const=True)
  parser.add_argument('--serve',
    help="Run HTTP server to analyze logs from browser",
    nargs='?', default=False, const=True)
  parser.add_argument('--tail',
    help="Tail logs",
    nargs='?', default=False, const=True)

  parser.add_argument('-p','--port', help="Port for --serve",
    type=int, default=7095)

  args = parser.parse_args()

  if args.listen:
    listen(args)
  elif args.serve:
    serve(args)
  elif args.tail:
    tail(args)
  else:
    parser.print_help()
  
if __name__ == '__main__':
  main()
