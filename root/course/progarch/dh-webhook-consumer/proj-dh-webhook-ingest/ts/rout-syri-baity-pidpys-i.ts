import express from "express";
import { Pool } from "pg";
import { createHmac, timingSafeEqual } from "node:crypto";

const pool = new Pool();
const SECRET = process.env.ACME_WEBHOOK_SECRET!;

function verify(raw: Buffer, header: string): boolean {
  const parts = Object.fromEntries(header.split(",").map(kv => kv.split("=", 2)));
  const t = Number(parts.t);
  if (!t || Math.abs(Date.now() / 1000 - t) > 300) return false;   // застарілий → повтор, геть
  const signed = Buffer.concat([Buffer.from(`${t}.`), raw]);        // t + СИРІ байти
  const expected = createHmac("sha256", SECRET).update(signed).digest("hex");
  const a = Buffer.from(expected), b = Buffer.from(parts.v1 ?? "");
  return a.length === b.length && timingSafeEqual(a, b);            // звірка за СТАЛИЙ час
}

// Ядро роуту — чиста функція над (сирі байти, заголовок). Легко кликати з тесту.
export async function handleWebhook(raw: Buffer, sigHeader: string): Promise<number> {
  if (!verify(raw, sigHeader)) return 400;                 // хто ти? не той підпис — двері зачинені
  const event = JSON.parse(raw.toString());

  const cx = await pool.connect();
  try {
    await cx.query("BEGIN");                               // inbox і черга — В ОДНІЙ транзакції
    const ins = await cx.query(
      "INSERT INTO inbox(event_id) VALUES ($1) ON CONFLICT DO NOTHING", [event.id]);
    if (ins.rowCount === 1)                                // id новий → у чергу
      await cx.query("INSERT INTO jobs(event_id, payload) VALUES ($1, $2)",
        [event.id, event]);
    await cx.query("COMMIT");                              // позначка й задача народжуються разом
  } catch (e) {
    await cx.query("ROLLBACK");                            // нічого не позначено баченим
    return 500;                                            // провайдер повторить — це безпечно
  } finally {
    cx.release();
  }
  return 200;                                              // ACK за десятки мс
}

const app = express();
// HTTP-обгортка тонка — увесь сенс у handleWebhook, тому його й тестуємо.
app.post("/hooks/acme-lock", express.raw({ type: "*/*" }), async (req, res) =>
  res.sendStatus(await handleWebhook(req.body, req.header("X-Acme-Signature") ?? "")));
