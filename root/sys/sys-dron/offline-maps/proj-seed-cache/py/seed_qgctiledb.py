#!/usr/bin/env python3
# seed_qgctiledb.py — складання набору офлайн-карт для QGroundControl
# без графічного інтерфейсу станції. Тільки стандартна бібліотека.
import argparse, hashlib, http.client, math, queue, sqlite3, sys, threading, time
import urllib.parse

SCHEMA_VERSION = 1
MAX_LAT = 85.05112877980659          # межа Меркатора: далі tan(φ) вибухає
BATCH   = 200                        # рядків на одну транзакцію

DDL = [
    "CREATE TABLE IF NOT EXISTS Tiles ("
    " tileID INTEGER PRIMARY KEY NOT NULL, hash TEXT NOT NULL UNIQUE,"
    " format TEXT NOT NULL, tile BLOB NULL, size INTEGER, type INTEGER,"
    " date INTEGER DEFAULT 0)",
    "CREATE TABLE IF NOT EXISTS TileSets ("
    " setID INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL UNIQUE, typeStr TEXT,"
    " topleftLat REAL DEFAULT 0.0, topleftLon REAL DEFAULT 0.0,"
    " bottomRightLat REAL DEFAULT 0.0, bottomRightLon REAL DEFAULT 0.0,"
    " minZoom INTEGER DEFAULT 3, maxZoom INTEGER DEFAULT 3, type INTEGER DEFAULT -1,"
    " numTiles INTEGER DEFAULT 0, defaultSet INTEGER DEFAULT 0, date INTEGER DEFAULT 0)",
    "CREATE TABLE IF NOT EXISTS SetTiles ("
    " setID INTEGER NOT NULL REFERENCES TileSets(setID) ON DELETE CASCADE,"
    " tileID INTEGER NOT NULL REFERENCES Tiles(tileID) ON DELETE CASCADE)",
    "CREATE TABLE IF NOT EXISTS TilesDownload ("
    " setID INTEGER NOT NULL REFERENCES TileSets(setID) ON DELETE CASCADE,"
    " hash TEXT NOT NULL, type INTEGER, x INTEGER, y INTEGER, z INTEGER,"
    " state INTEGER DEFAULT 0)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_settiles_unique ON SetTiles(tileID, setID)",
    "CREATE INDEX IF NOT EXISTS idx_settiles_setid  ON SetTiles(setID)",
    "CREATE INDEX IF NOT EXISTS idx_settiles_tileid ON SetTiles(tileID)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_tilesdownload_setid_hash"
    " ON TilesDownload(setID, hash)",
    "CREATE INDEX IF NOT EXISTS idx_tilesdownload_setid_state"
    " ON TilesDownload(setID, state)",
    "CREATE INDEX IF NOT EXISTS idx_tiles_date ON Tiles(date)",
]


# ─── географія ──────────────────────────────────────────────────────────────
def tile_x(lon, z):
    return int(math.floor((lon + 180.0) / 360.0 * (1 << z)))


def tile_y(lat, z):
    lat = max(-MAX_LAT, min(MAX_LAT, lat))
    phi = math.radians(lat)
    return int(math.floor((1.0 - math.log(math.tan(phi) + 1.0 / math.cos(phi))
                           / math.pi) / 2.0 * (1 << z)))


def cells(west, south, east, north, zmin, zmax):
    """Клітинки прямокутника на всіх рівнях. Північ дає МЕНШИЙ y."""
    for z in range(zmin, zmax + 1):
        n = 1 << z
        x0, x1 = tile_x(west, z), tile_x(east, z)
        y0, y1 = tile_y(north, z), tile_y(south, z)
        for x in range(max(0, x0), min(n - 1, x1) + 1):
            for y in range(max(0, y0), min(n - 1, y1) + 1):
                yield z, x, y


def tile_hash(map_id, x, y, z):
    return "%010d%08d%08d%03d" % (map_id, x, y, z)


def quadkey(x, y, z):
    """Адресація Bing: рівень за рівнем, по два біти на цифру."""
    out = []
    for i in range(z, 0, -1):
        mask, digit = 1 << (i - 1), 0
        if x & mask:
            digit += 1
        if y & mask:
            digit += 2
        out.append(str(digit))
    return "".join(out)


def image_format(body):
    """Розпізнавання за сигнатурою — так само, як це робить станція."""
    if body[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if body[:3] == b"\xff\xd8\xff":
        return "jpg"
    return None


# ─── мережа ─────────────────────────────────────────────────────────────────
class Pace:
    """Спільна на всі нитки стеля «не більше rps запитів за секунду»."""

    def __init__(self, rps):
        self._gap = 1.0 / rps
        self._lock = threading.Lock()
        self._next = time.monotonic()

    def wait(self):
        with self._lock:                       # нитки справжні — потрібен замок
            now = time.monotonic()
            self._next = max(self._next, now) + self._gap
            delay = self._next - self._gap - now
        if delay > 0:
            time.sleep(delay)


class Fetcher:
    """Одне тривке з'єднання на робітника: рукостискання — раз на прогін."""

    def __init__(self, host, headers, pace, timeout=15.0):
        self.host, self.headers, self.pace, self.timeout = host, headers, pace, timeout
        self.conn = None

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except OSError:
                pass
            self.conn = None

    def get(self, path, attempts=4):
        for attempt in range(attempts):
            self.pace.wait()
            try:
                if self.conn is None:
                    self.conn = http.client.HTTPSConnection(self.host, timeout=self.timeout)
                self.conn.request("GET", path, headers=self.headers)
                resp = self.conn.getresponse()
                body = resp.read()             # тіло читаємо ЗАВЖДИ, інакше
                if resp.status == 200:         # з'єднання не перевикористати
                    return body
                if resp.status in (408, 429, 500, 502, 503, 504):
                    hold = resp.getheader("Retry-After")
                    time.sleep(float(hold) if hold and hold.isdigit() else 2.0 ** attempt)
                    continue
                return None                    # 401 / 403 / 404 — остаточні
            except (http.client.HTTPException, OSError):
                self.close()
                time.sleep(2.0 ** attempt)
        return None


# ─── база ───────────────────────────────────────────────────────────────────
def open_db(path):
    db = sqlite3.connect(path, isolation_level=None)   # транзакціями керуємо самі
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = DELETE")         # один файл на виході
    db.execute("PRAGMA synchronous  = NORMAL")
    for stmt in DDL:
        db.execute(stmt)
    return db


def ensure_set(db, a, west, south, east, north, zmin, zmax):
    row = db.execute("SELECT setID FROM TileSets WHERE name = ?", (a.name,)).fetchone()
    if row:
        return row[0]
    cur = db.execute(
        "INSERT INTO TileSets(name, typeStr, topleftLat, topleftLon, bottomRightLat,"
        " bottomRightLon, minZoom, maxZoom, type, numTiles, defaultSet, date)"
        " VALUES(?,?,?,?,?,?,?,?,?,0,0,?)",
        (a.name, a.map_name, north, west, south, east,      # topleft = ПнЗх кут
         zmin, zmax, a.map_id, int(time.time())))
    return cur.lastrowid


# ─── прогін ─────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Складання .qgctiledb для QGroundControl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", required=True, help="ім'я набору, як його побачить оператор")
    ap.add_argument("--bbox", required=True, help="west,south,east,north у градусах")
    ap.add_argument("--zoom", required=True, help="zmin-zmax")
    ap.add_argument("--url", required=True,
                    help="шаблон із {z} {x} {y} або {q} (quadkey)")
    ap.add_argument("--map-name", required=True, help='typeStr, напр. "Bing Satellite"')
    ap.add_argument("--map-id", type=int, required=True, help="той самий код, що в hash")
    ap.add_argument("--rps", type=float, default=4.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--user-agent", default="qgc-tile-seeder/1.0")
    ap.add_argument("--referer")
    ap.add_argument("--drop", action="append", default=[], help="sha1 тіла-заглушки")
    a = ap.parse_args()

    if a.map_id < 1:
        sys.exit("код провайдера мусить бути додатним: -1 дає непридатний ключ")

    west, south, east, north = (float(v) for v in a.bbox.split(","))
    zmin, zmax = (int(v) for v in a.zoom.split("-"))
    url = urllib.parse.urlsplit(a.url)
    headers = {"User-Agent": a.user_agent, "Accept": "*/*", "Connection": "keep-alive"}
    if a.referer:
        headers["Referer"] = a.referer

    db = open_db(a.out)
    set_id = ensure_set(db, a, west, south, east, north, zmin, zmax)
    have = {h for (h,) in db.execute("SELECT hash FROM Tiles")}   # для продовження

    work, planned = queue.Queue(), 0
    for z, x, y in cells(west, south, east, north, zmin, zmax):
        planned += 1
        h = tile_hash(a.map_id, x, y, z)
        if h not in have:
            work.put((z, x, y, h))
    results = queue.Queue(maxsize=256)      # стеля пам'яті: ~256 тайлів у польоті
    pace = Pace(a.rps)

    def worker():
        f = Fetcher(url.netloc, headers, pace)
        while True:
            try:
                z, x, y, h = work.get_nowait()
            except queue.Empty:
                break
            fields = {"z": z, "x": x, "y": y, "q": quadkey(x, y, z)}
            path = url.path.format(**fields)
            if url.query:
                path += "?" + url.query.format(**fields)
            results.put((h, f.get(path)))
        f.close()
        results.put(None)

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(a.workers)]
    for t in threads:
        t.start()

    digests, saved, skipped, alive = {}, 0, 0, len(threads)
    now = int(time.time())
    db.execute("BEGIN")
    while alive:
        item = results.get()
        if item is None:
            alive -= 1
            continue
        h, body = item
        fmt = image_format(body) if body else None
        if fmt is None:
            skipped += 1
            continue
        digests.setdefault(hashlib.sha1(body).hexdigest(), []).append(h)
        db.execute("INSERT OR IGNORE INTO Tiles(hash, format, tile, size, type, date)"
                   " VALUES(?,?,?,?,?,?)", (h, fmt, body, len(body), a.map_id, now))
        saved += 1
        if saved % BATCH == 0:
            db.execute("COMMIT")
            db.execute("BEGIN")
            print("\r%d / %d" % (saved, planned), end="", file=sys.stderr)
    db.execute("COMMIT")
    print("\nзбережено %d, не картинок %d" % (saved, skipped), file=sys.stderr)

    # відсів заглушок: спершу звіт зі зразками, викидаємо лише назване явно
    for digest, hashes in sorted(digests.items(), key=lambda kv: -len(kv[1]))[:5]:
        if len(hashes) < 2:
            continue
        fmt, blob = db.execute("SELECT format, tile FROM Tiles WHERE hash = ?",
                               (hashes[0],)).fetchone()
        with open("sample-%s.%s" % (digest[:8], fmt), "wb") as fh:
            fh.write(blob)
        print("%s  однакових тіл: %d  → sample-%s.%s"
              % (digest, len(hashes), digest[:8], fmt), file=sys.stderr)
    if a.drop:
        marked = [(h,) for d in a.drop for h in digests.get(d, [])]
        db.executemany("DELETE FROM Tiles WHERE hash = ?", marked)
        print("викинуто заглушок: %d" % len(marked), file=sys.stderr)

    db.execute("BEGIN")
    db.execute("INSERT OR IGNORE INTO SetTiles(tileID, setID) SELECT tileID, ? FROM Tiles",
               (set_id,))
    total = db.execute("SELECT COUNT(*) FROM SetTiles WHERE setID = ?",
                       (set_id,)).fetchone()[0]
    db.execute("UPDATE TileSets SET numTiles = ? WHERE setID = ?", (total, set_id))
    db.execute("COMMIT")
    db.execute("PRAGMA user_version = %d" % SCHEMA_VERSION)
    db.close()
    print("у наборі «%s»: %d клітинок" % (a.name, total), file=sys.stderr)


if __name__ == "__main__":
    main()
