// topology.ts — ЄДИНЕ джерело правди про фінальну топологію DH.
// З нього живуть і сторож (валить збірку), і картинка (з тих самих даних).
export type Style = "sync" | "async";     // синхронно (запит-відповідь) | асинхронно (подія)
type Place = "client" | "door" | "cloud" | "edge" | "external";

interface Deployment {
  place: Place;
  db: string | null;      // база, якою розгортання ВОЛОДІЄ (лише своя); хто без бази — null
  owns: string[];         // внутрішні модулі (для приписування зовнішніх швів білінгу/сповіщень)
}
interface Seam {
  from: string; to: string;
  style: Style;
  topic?: string;         // для async-шва — топік, яким він реалізований
  why: string;            // чому саме цей стиль (те, що на картинці стоїть у колонці «чому»)
}

// ── ЩО котиться в прод самостійно ──
export const DEPLOYMENTS: Record<string, Deployment> = {
  app:       { place: "client",   db: null, owns: [] },
  dashboard: { place: "client",   db: null, owns: [] },
  gateway:   { place: "door",     db: null, owns: [] },                 // TLS, токен, ліміт, маршрут
  core:      { place: "cloud",    db: "core_db",                        // ← ТРИ хмарні розгортання
               owns: ["control","twin","automations","notifications","billing","identity"] },
  telemetry: { place: "cloud",    db: "telemetry_db", owns: ["telemetry"] },
  video:     { place: "cloud",    db: "video_db",     owns: ["video"] },
  hub:       { place: "edge",     db: null, owns: ["hub"] },            // на полиці у власника
  payments:  { place: "external", db: null, owns: [] },                // чужий, за ACL
  push:      { place: "external", db: null, owns: [] },
};

// ── КОЖЕН дозволений шов і його СТИЛЬ (це те, чого мапа моноліта не знала) ──
export const SEAMS: Seam[] = [
  { from:"app",       to:"gateway",   style:"sync",  why:"людина натиснула й дивиться на екран" },
  { from:"dashboard", to:"gateway",   style:"sync",  why:"людина чекає відповіді" },
  { from:"gateway",   to:"core",      style:"sync",  why:"BFF складає екран із ядра" },
  { from:"gateway",   to:"telemetry", style:"sync",  why:"BFF читає останній вимір — терпить таймаут" },
  { from:"gateway",   to:"video",     style:"sync",  why:"клієнт відкриває живий потік камери" },
  { from:"core", to:"telemetry", style:"async", topic:"DeviceEvent", why:"ядро публікує факт і йде — не чекає запису" },
  { from:"core", to:"video",     style:"async", topic:"DeviceEvent", why:"відео чує про камери з того ж потоку" },
  { from:"core", to:"hub",       style:"async", topic:"HubCommand",  why:"команда вниз; у домі буває поганий Wi-Fi" },
  { from:"hub",  to:"core",      style:"async", topic:"HubEvent",    why:"стан дому — подією вгору, ретрай + ідемпотентність" },
  { from:"core", to:"payments",  style:"sync",  why:"білінгу треба тверде «так/ні» від чужого, за ACL" },
  { from:"core", to:"push",      style:"async", topic:"Notify",      why:"сповіщення: вистрелив-забув, доставку не блокуємо" },
];
