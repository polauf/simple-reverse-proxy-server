from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

class ReverseProxyHandler(BaseHTTPRequestHandler):
  PROTOCOL = 'http'
  protocol_version = 'HTTP/1.0'

  def parse_headers(self):
    "Requests module compatible headers"
    self._header = {}
    for line in self.headers:
      l = line.split(":")
      if len(l) > 1:
        self._header[l[0].strip()] = l[1].strip() 

  def parse_body(self):
    "Read bytes from raw file"
    try:
      nbytes = int(self.headers.get('content-length'))
    except (TypeError, ValueError):
      nbytes = 0
    self.data = None
    if nbytes > 0:
      self.data = self.rfile.read(nbytes)

  def resolve(self):
    "Very (very) simple router"
    for iin, out, cut in routes:
      if self.path.startswith(iin):
        self.output = out
        if cut:
          self.path = self.path[len(iin):]
        return
    self.output = root

  def do_POST(self):
    "'Universal' request folower"
    self.resolve()
    self.parse_headers()
    self.parse_body()
    # get stuff from actual server
    resp = requests.request(
      self.command,
      f"{self.PROTOCOL}://{self.output}{self.path}",
      headers=self._header,
      data=self.data,
      verify=False # only HTTP
      )
    # remake it to HTTPServer response
    self.send_response(resp.status_code)
    for k, v in resp.headers.items():
      self.send_header(k, v)
    self.end_headers()
    self.wfile.write(resp.content)

  # Use principle above for all requests (fast and dirty)
  do_PATCH = do_OPTIONS = do_CONNECT = do_DELETE = do_PUT = do_HEAD = do_GET = do_POST

if __name__ == "__main__":
  import sys
  if len(sys.argv) == 2 and (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
    print("""
Very simple reverse proxy server
--------------------------------

Suitable only for development and testing.

Route rule is in::out::cut_path

example:

reverse_proxy localhost:4000 /::localhost:3000 /api::localhost:6000::true /more_stuff::localhost:9000

Output is 'localhost:4000'.
If its begins with '/api' it should go to :6000 and cut '/api' from request path.
If its begins with '/more_stuff' go to :9000 and don't cut '/more_stuff' from path.
Otherwise go to :3000.
""")
    sys.exit(0)

  if len(sys.argv) < 3:
    print("Need output and one rule as minimum")
    sys.exit(1)

  try:
    host, port = sys.argv[1].split(":")
    port = int(port)

    routes = []
    root = None
    for i, rule in enumerate(sys.argv[2:]):
      rule = rule.split("::")
      if len(rule) == 2:
        rule.append(False)
      elif len(rule) == 3:
        rule[2] = rule[2].lower() == "true"
      else:
        print(f"Wrong rule #{i+1}.")
        sys.exit(1)
      if rule[0] == "/":
        root = rule[1]
      else:
        routes.append(rule)
  except Exception as e:
    print("Something went wrong. Try again.")
    sys.exit(1)

  try:
    print(f"Reverse Proxy running at {host}:{port}.\n")
    print(f"/ -> {root}")
    for r in routes:
      print(f"{r[0]} -> {r[1]}{' cut' if r[2] else ''}")
    print()
    httpd = HTTPServer((host, port), ReverseProxyHandler)
    httpd.serve_forever()
  except KeyboardInterrupt:
    print("Bye.")

