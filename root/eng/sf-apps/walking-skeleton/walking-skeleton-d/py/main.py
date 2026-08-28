import threading, queue
from http.server import BaseHTTPRequestHandler, HTTPServer

# Найтонша нитка: браузер → API → черга → воркер → сховище → читання назад.
# Справжні тут — HTTP-стик і межа «API ↔ воркер» (черга між потоками).
# Черга і словник — заглушки майбутніх брокера й бази; їхня заміна — вже м'ясо.
q: "queue.Queue[int]" = queue.Queue()
store: dict[str, int] = {}

def worker():                        # окрема частина: читає з черги, пише у сховище
    while True:
        store["temp"] = q.get()      # стик воркер → сховище

threading.Thread(target=worker, daemon=True).start()

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.rfile.read(int(self.headers["Content-Length"])))
        q.put(n)                     # стик API → черга
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(str(store.get("temp", "—")).encode())  # нитка пройшла?

HTTPServer(("", 8080), H).serve_forever()
