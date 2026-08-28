import { createHmac, timingSafeEqual } from "node:crypto";

// Перевіряємо ДО розбору тіла. rawBody — точні отримані байти, не переупакований JSON.
function verify(rawBody: Buffer, header: string, secret: string): boolean {
  const parts = Object.fromEntries(header.split(",").map(kv => kv.split("=", 2)));
  const t = Number(parts.t);
  if (!t || Math.abs(Date.now() / 1000 - t) > 300) return false; // застарілий підпис → повтор, геть
  const signed = Buffer.concat([Buffer.from(`${t}.`), rawBody]);
  const expected = createHmac("sha256", secret).update(signed).digest("hex");
  const a = Buffer.from(expected);
  const b = Buffer.from(parts.v1 ?? "");
  return a.length === b.length && timingSafeEqual(a, b);         // звірка за СТАЛИЙ час
}
