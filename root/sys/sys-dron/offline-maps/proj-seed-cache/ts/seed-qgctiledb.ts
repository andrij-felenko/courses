// seed-qgctiledb.ts — те саме на Node 22.13+ / 24: node:sqlite без прапорця,
// fetch вбудований, залежностей немає.
import { DatabaseSync } from 'node:sqlite';
import { createHash } from 'node:crypto';
import { writeFileSync } from 'node:fs';
import { parseArgs } from 'node:util';

const SCHEMA_VERSION = 1;
const MAX_LAT = 85.05112877980659;   // межа Меркатора: далі tan(φ) вибухає
const BATCH = 200;                   // рядків на одну транзакцію

const DDL = [
  'CREATE TABLE IF NOT EXISTS Tiles (' +
  ' tileID INTEGER PRIMARY KEY NOT NULL, hash TEXT NOT NULL UNIQUE,' +
  ' format TEXT NOT NULL, tile BLOB NULL, size INTEGER, type INTEGER,' +
  ' date INTEGER DEFAULT 0)',
  'CREATE TABLE IF NOT EXISTS TileSets (' +
  ' setID INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL UNIQUE, typeStr TEXT,' +
  ' topleftLat REAL DEFAULT 0.0, topleftLon REAL DEFAULT 0.0,' +
  ' bottomRightLat REAL DEFAULT 0.0, bottomRightLon REAL DEFAULT 0.0,' +
  ' minZoom INTEGER DEFAULT 3, maxZoom INTEGER DEFAULT 3, type INTEGER DEFAULT -1,' +
  ' numTiles INTEGER DEFAULT 0, defaultSet INTEGER DEFAULT 0, date INTEGER DEFAULT 0)',
  'CREATE TABLE IF NOT EXISTS SetTiles (' +
  ' setID INTEGER NOT NULL REFERENCES TileSets(setID) ON DELETE CASCADE,' +
  ' tileID INTEGER NOT NULL REFERENCES Tiles(tileID) ON DELETE CASCADE)',
  'CREATE TABLE IF NOT EXISTS TilesDownload (' +
  ' setID INTEGER NOT NULL REFERENCES TileSets(setID) ON DELETE CASCADE,' +
  ' hash TEXT NOT NULL, type INTEGER, x INTEGER, y INTEGER, z INTEGER,' +
  ' state INTEGER DEFAULT 0)',
  'CREATE UNIQUE INDEX IF NOT EXISTS idx_settiles_unique ON SetTiles(tileID, setID)',
  'CREATE INDEX IF NOT EXISTS idx_settiles_setid  ON SetTiles(setID)',
  'CREATE INDEX IF NOT EXISTS idx_settiles_tileid ON SetTiles(tileID)',
  'CREATE UNIQUE INDEX IF NOT EXISTS idx_tilesdownload_setid_hash' +
  ' ON TilesDownload(setID, hash)',
  'CREATE INDEX IF NOT EXISTS idx_tilesdownload_setid_state' +
  ' ON TilesDownload(setID, state)',
  'CREATE INDEX IF NOT EXISTS idx_tiles_date ON Tiles(date)',
];

type Cell = { z: number; x: number; y: number; hash: string };

// ─── географія ──────────────────────────────────────────────────────────────
const tileX = (lon: number, z: number) => Math.floor(((lon + 180) / 360) * 2 ** z);

const tileY = (lat: number, z: number): number => {
  const phi = (Math.max(-MAX_LAT, Math.min(MAX_LAT, lat)) * Math.PI) / 180;
  return Math.floor(((1 - Math.log(Math.tan(phi) + 1 / Math.cos(phi)) / Math.PI) / 2)
                    * 2 ** z);
};

const pad = (v: number, w: number) => String(v).padStart(w, '0');
const tileHash = (mapId: number, x: number, y: number, z: number) =>
  pad(mapId, 10) + pad(x, 8) + pad(y, 8) + pad(z, 3);

/** Адресація Bing: рівень за рівнем, по два біти на цифру. */
function quadkey(x: number, y: number, z: number): string {
  let out = '';
  for (let i = z; i > 0; i--) {
    const mask = 1 << (i - 1);
    out += String((x & mask ? 1 : 0) + (y & mask ? 2 : 0));
  }
  return out;
}

/** Розпізнавання за сигнатурою — так само, як це робить станція. */
function imageFormat(b: Uint8Array): string | null {
  if (b.length > 8 && b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47)
    return 'png';
  if (b.length > 3 && b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return 'jpg';
  return null;
}

function* cells(w: number, s: number, e: number, n: number, zmin: number, zmax: number) {
  for (let z = zmin; z <= zmax; z++) {
    const size = 2 ** z;
    const x0 = Math.max(0, tileX(w, z));
    const x1 = Math.min(size - 1, tileX(e, z));
    const y0 = Math.max(0, tileY(n, z));          // північ дає МЕНШИЙ y
    const y1 = Math.min(size - 1, tileY(s, z));
    for (let x = x0; x <= x1; x++) for (let y = y0; y <= y1; y++) yield { z, x, y };
  }
}

// ─── мережа ─────────────────────────────────────────────────────────────────
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** Спільна стеля «не більше rps запитів за секунду».
 *  Замка немає навмисно: у Node паралельність кооперативна, і між читанням
 *  та записом `next` виконання не переривається. */
class Pace {
  private readonly gap: number;
  private next = 0;
  constructor(rps: number) { this.gap = 1000 / rps; }
  async wait(): Promise<void> {
    const now = Date.now();
    this.next = Math.max(this.next, now) + this.gap;
    const delay = this.next - this.gap - now;
    if (delay > 0) await sleep(delay);
  }
}

async function get(url: string, headers: Record<string, string>, pace: Pace,
                   attempts = 4): Promise<Uint8Array | null> {
  for (let a = 0; a < attempts; a++) {
    await pace.wait();
    try {
      const res = await fetch(url, { headers, signal: AbortSignal.timeout(15_000) });
      const body = new Uint8Array(await res.arrayBuffer());   // тіло читаємо ЗАВЖДИ
      if (res.ok) return body;
      if ([408, 429, 500, 502, 503, 504].includes(res.status)) {
        const hold = Number(res.headers.get('retry-after'));
        await sleep(Number.isFinite(hold) && hold > 0 ? hold * 1000 : 2 ** a * 1000);
        continue;
      }
      return null;                                           // 401 / 403 / 404
    } catch { await sleep(2 ** a * 1000); }
  }
  return null;
}

// ─── прогін ─────────────────────────────────────────────────────────────────
const { values } = parseArgs({
  options: {
    out: { type: 'string' }, name: { type: 'string' }, bbox: { type: 'string' },
    zoom: { type: 'string' }, url: { type: 'string' },
    'map-name': { type: 'string' }, 'map-id': { type: 'string' },
    rps: { type: 'string', default: '4' }, workers: { type: 'string', default: '4' },
    'user-agent': { type: 'string', default: 'qgc-tile-seeder/1.0' },
    referer: { type: 'string' }, drop: { type: 'string', multiple: true, default: [] },
  },
});

const mapId = Number(values['map-id']);
if (!(mapId >= 1)) throw new Error('код провайдера мусить бути додатним');

const [west, south, east, north] = values.bbox!.split(',').map(Number);
const [zmin, zmax] = values.zoom!.split('-').map(Number);
const headers: Record<string, string> = {
  'User-Agent': values['user-agent']!, Accept: '*/*',
  ...(values.referer ? { Referer: values.referer } : {}),
};

const db = new DatabaseSync(values.out!);
db.exec('PRAGMA foreign_keys = ON');
db.exec('PRAGMA journal_mode = DELETE');        // один файл на виході
db.exec('PRAGMA synchronous  = NORMAL');
for (const stmt of DDL) db.exec(stmt);

let setRow = db.prepare('SELECT setID FROM TileSets WHERE name = ?')
               .get(values.name!) as { setID: number } | undefined;
if (!setRow) {
  const res = db.prepare(
    'INSERT INTO TileSets(name, typeStr, topleftLat, topleftLon, bottomRightLat,' +
    ' bottomRightLon, minZoom, maxZoom, type, numTiles, defaultSet, date)' +
    ' VALUES(?,?,?,?,?,?,?,?,?,0,0,?)',
  ).run(values.name!, values['map-name']!, north, west, south, east,  // ПнЗх кут
        zmin, zmax, mapId, Math.floor(Date.now() / 1000));
  setRow = { setID: Number(res.lastInsertRowid) };
}
const setID = setRow.setID;

const have = new Set((db.prepare('SELECT hash FROM Tiles').all() as { hash: string }[])
                       .map((r) => r.hash));
const todo: Cell[] = [];
let planned = 0;
for (const c of cells(west, south, east, north, zmin, zmax)) {
  planned++;
  const hash = tileHash(mapId, c.x, c.y, c.z);
  if (!have.has(hash)) todo.push({ ...c, hash });
}

const insTile = db.prepare(
  'INSERT OR IGNORE INTO Tiles(hash, format, tile, size, type, date) VALUES(?,?,?,?,?,?)');
const pace = new Pace(Number(values.rps));
const digests = new Map<string, string[]>();
const now = Math.floor(Date.now() / 1000);
let cursor = 0, saved = 0, skipped = 0;

db.exec('BEGIN');
await Promise.all(Array.from({ length: Number(values.workers) }, async () => {
  while (cursor < todo.length) {
    const c = todo[cursor++];
    const url = values.url!.replaceAll('{z}', String(c.z)).replaceAll('{x}', String(c.x))
                           .replaceAll('{y}', String(c.y))
                           .replaceAll('{q}', quadkey(c.x, c.y, c.z));
    const body = await get(url, headers, pace);
    const fmt = body ? imageFormat(body) : null;
    if (!body || !fmt) { skipped++; continue; }
    const d = createHash('sha1').update(body).digest('hex');
    const seen = digests.get(d);
    if (seen) seen.push(c.hash); else digests.set(d, [c.hash]);
    insTile.run(c.hash, fmt, body, body.length, mapId, now);   // запис синхронний
    if (++saved % BATCH === 0) {
      db.exec('COMMIT'); db.exec('BEGIN');
      process.stderr.write(`\r${saved} / ${planned}`);
    }
  }
}));
db.exec('COMMIT');
process.stderr.write(`\nзбережено ${saved}, не картинок ${skipped}\n`);

// відсів заглушок: спершу звіт зі зразками, викидаємо лише назване явно
const sample = db.prepare('SELECT format, tile FROM Tiles WHERE hash = ?');
for (const [digest, list] of [...digests].sort((a, b) => b[1].length - a[1].length)
                                         .slice(0, 5)) {
  if (list.length < 2) continue;
  const row = sample.get(list[0]) as { format: string; tile: Uint8Array };
  writeFileSync(`sample-${digest.slice(0, 8)}.${row.format}`, row.tile);
  process.stderr.write(`${digest}  однакових тіл: ${list.length}\n`);
}
const del = db.prepare('DELETE FROM Tiles WHERE hash = ?');
let dropped = 0;
for (const d of values.drop!) for (const h of digests.get(d) ?? []) { del.run(h); dropped++; }
if (dropped) process.stderr.write(`викинуто заглушок: ${dropped}\n`);

db.exec('BEGIN');
db.prepare('INSERT OR IGNORE INTO SetTiles(tileID, setID) SELECT tileID, ? FROM Tiles')
  .run(setID);
const { total } = db.prepare('SELECT COUNT(*) AS total FROM SetTiles WHERE setID = ?')
                    .get(setID) as { total: number };
db.prepare('UPDATE TileSets SET numTiles = ? WHERE setID = ?').run(total, setID);
db.exec('COMMIT');
db.exec(`PRAGMA user_version = ${SCHEMA_VERSION}`);
db.close();
process.stderr.write(`у наборі «${values.name}»: ${total} клітинок\n`);
