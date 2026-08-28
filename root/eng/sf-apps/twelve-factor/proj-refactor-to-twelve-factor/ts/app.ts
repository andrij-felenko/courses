// app.ts — застосунок «до». Та сама історія іншою мовою.
import express from "express";
import session from "express-session";
import multer from "multer";
import path from "path";

const app = express();

// ── прив'язка №1: конфіг зашитий у код ──
const SECRET = "super-secret-please-change";
const DATABASE_URL = "postgresql://localhost:5432/photos";
const UPLOAD_DIR = "/var/app/uploads";

// ── прив'язка №2: сесія в пам'яті ЦЬОГО процесу ──
// MemoryStore за замовчуванням тримає всі сесії в купі цього процесу
app.use(session({ secret: SECRET, resave: false, saveUninitialized: false }));

const upload = multer({ dest: UPLOAD_DIR });   // ← файли на локальний диск

app.post("/upload", upload.single("photo"), (req, res) => {
  const userId = (req.session as any).userId;
  const dest = path.join(UPLOAD_DIR, userId, req.file!.originalname);
  // ...перекласти файл у dest на ЦЬОМУ диску...
  res.json({ stored: dest });
});

app.get("/photo/:userId/:name", (req, res) => {
  res.sendFile(path.join(UPLOAD_DIR, req.params.userId, req.params.name));
});

app.listen(8000, "0.0.0.0");   // ← порт зашитий у код
