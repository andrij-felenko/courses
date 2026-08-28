import { DatabaseSync } from "node:sqlite";           // вбудований у Node ≥ 22.5

function openRegistry(path: string): DatabaseSync {   // писар реєстру: тривкість по максимуму
  const db = new DatabaseSync(path);
  db.exec("PRAGMA journal_mode = WAL");               // властивість ФАЙЛУ
  db.exec("PRAGMA synchronous  = FULL");             // властивість ЦЬОГО зʼєднання
  db.exec("PRAGMA foreign_keys = ON");
  db.exec("PRAGMA busy_timeout = 5000");
  return db;
}

function openTelemetry(path: string): DatabaseSync {  // писар телеметрії: тривкість відпущена
  const db = new DatabaseSync(path);
  db.exec("PRAGMA journal_mode = WAL");
  db.exec("PRAGMA synchronous  = NORMAL");
  db.exec("PRAGMA busy_timeout = 5000");
  return db;
}
