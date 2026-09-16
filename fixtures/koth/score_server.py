import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length))
        accepted = payload.get("flag") == "OMNI{fixture}"
        self.send_response(200 if accepted else 400)
        self.end_headers()
        self.wfile.write(json.dumps({"accepted": accepted}).encode())


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 19090), Handler).serve_forever()
