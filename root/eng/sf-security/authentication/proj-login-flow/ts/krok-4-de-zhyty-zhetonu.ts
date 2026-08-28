import { createHash, randomBytes } from "node:crypto";

const sha256 = (s: string) => createHash("sha256").update(s).digest("hex");

interface Session { userId: string; createdAt: number; lastSeen: number; }

async function createSession(userId: string, db: Db): Promise<string> {
  const token = randomBytes(16).toString("base64url");
  const now = Date.now();
  // у базі — лише ВІДБИТОК жетона; сам жетон їде тільки в cookie до клієнта
  await db.putSession(sha256(token), { userId, createdAt: now, lastSeen: now });
  return token;
}

async function resolveSession(token: string, db: Db): Promise<Session | null> {
  return db.getSession(sha256(token));   // шукаємо за відбитком
}
