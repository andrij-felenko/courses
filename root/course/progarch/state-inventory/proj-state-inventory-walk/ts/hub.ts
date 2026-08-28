// hub.ts — підрослий хаб Digital Homes (фрагмент): пристрої, розклад, БД, кеш
import Database from "better-sqlite3";
import { readFileSync } from "node:fs";

const TIMEOUT_S = 90;                       // мовчить довше — вважаємо офлайн
const db = new Database("hub.db");          // ← джерело правди про пристрої: на диску

class Device {                              // сесія пристрою — живе в ПАМʼЯТІ процесу
  lastSeen = 0;
  online = false;                           // ← похідне від lastSeen, а ЗБЕРІГАЄМО окремо
  temp: number | null = null;
  constructor(public id: number, public name: string, public relay: number) {}
}

const devices = new Map<number, Device>();  // ← список у памʼяті: ДУБЛЬ таблиці devices
const statusCache = new Map<number, any>(); // ← кеш статусів для застосунку: похідне
const schedule = JSON.parse(readFileSync("schedule.json", "utf8"));  // ← розклад: з ФАЙЛУ
let heatedSince: number | null = null;      // ← лічильник «2 год»: ТІЛЬКИ в памʼяті

function reloadDevices(): void {            // тягнемо список із БД у памʼятний кеш
  devices.clear();
  for (const r of db.prepare("SELECT id, name, relay FROM devices").all() as any[])
    devices.set(r.id, new Device(r.id, r.name, r.relay));
}

function poll(): void {                     // опитувач: раз на виток питає кожен пристрій
  for (const d of devices.values()) {
    const t = ping(d);                      // локальна змінна — живе один виток
    if (t !== null) { d.temp = t; d.lastSeen = Date.now(); d.online = true; }  // писар online №1
    statusCache.set(d.id, { temp: d.temp, online: d.online, ts: Date.now() });
  }
}

function onPush(msg: { id: number; temp: number }): void {   // пристрій штовхнув пакет
  const d = devices.get(msg.id);
  if (d) {
    d.lastSeen = Date.now(); d.online = true;                 // писар online №2
    statusCache.get(msg.id).temp = msg.temp;                  // писар у кеш повз опитувач
  }
}

function apiStatus(deviceId: number) {      // застосунок питає статус — читає кеш
  return statusCache.get(deviceId);
}
