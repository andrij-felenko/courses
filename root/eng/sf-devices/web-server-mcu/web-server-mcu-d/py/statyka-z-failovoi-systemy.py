# Віддати файл name зі статичної теки, порціями через генератор.
import os
from flask import Response, abort

TYPES = {".html": "text/html", ".css": "text/css",
         ".js": "application/javascript"}

def send_file_from_fs(name):
    full = os.path.join("/spiffs", name)
    if not os.path.isfile(full):                # нема файлу — чесний 404
        abort(404)

    ext = os.path.splitext(name)[1]             # тип за розширенням
    ctype = TYPES.get(ext, "text/plain")

    def chunks():                               # ПОРЦІЯМИ: не тримаємо файл у пам'яті
        with open(full, "rb") as f:
            while True:
                data = f.read(512)              # кожна порція — окремим шматком
                if not data:
                    break                       # файл скінчився
                yield data

    return Response(chunks(), mimetype=ctype)
