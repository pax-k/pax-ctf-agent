from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class FixtureHandler(BaseHTTPRequestHandler):
    notes = {"1": "public", "2": "admin-only fixture note"}

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path == "/login" and query.get("user") == ["admin"]:
            self.send_response(302)
            self.send_header("Set-Cookie", "role=admin")
            self.send_header("Location", "/note?id=2")
            self.end_headers()
            return
        if parsed.path == "/note":
            body = self.notes.get(query.get("id", ["1"])[0], "missing").encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OmniCTF local Web fixture")


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 18080), FixtureHandler).serve_forever()
