# MicroPython на Microdot: віддати файл name порціями через генератор.
import os
from microdot import Response

TYPES = {".html": "text/html", ".css": "text/css",
         ".js": "application/javascript"}

def send_file_from_fs(name):
    full = "/spiffs/" + name
    try:
        f = open(full, "rb")
    except OSError:                             # нема файлу — чесний 404
        return "not found", 404

    ext = "." + name.rsplit(".", 1)[-1]         # тип за розширенням
    ctype = TYPES.get(ext, "text/plain")

    def chunks():                               # ПОРЦІЯМИ: не тримаємо файл у пам'яті
        try:
            while True:
                data = f.read(512)              # кожна порція — окремим шматком
                if not data:
                    break                       # файл скінчився
                yield data
        finally:
            f.close()

    return Response(chunks(), headers={"Content-Type": ctype})
