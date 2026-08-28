// Значення конфігу — або просте (рядок/число/булеве), або ПОСИЛАННЯ на секрет.
type Ref  = { readonly secret: string };            // { secret: "dh/db/password" }
type Leaf = string | number | boolean | Ref;

// Секрет упізнаємо ЗА ФОРМОЮ: обʼєкт із полем `secret`, а не за списком імен.
const isRef = (v: Leaf): v is Ref =>
  typeof v === "object" && v !== null && typeof (v as Ref).secret === "string";

// Той самий поділ, що в статті: горішні — конфіг, долішні — секрети.
const manifest: Record<string, Leaf> = {
  mqttUrl:    "mqtts://broker.dh.internal:8883",   // конфіг
  pollSec:    30,                                  // конфіг
  logLevel:   "info",                              // конфіг
  dbHost:     "prod-db.internal",                  // конфіг
  dbPassword: { secret: "dh/db/password" },        // СЕКРЕТ — лише адреса у сховищі
  cloudToken: { secret: "dh/cloud/hub-token" },    // СЕКРЕТ — лише адреса у сховищі
};
