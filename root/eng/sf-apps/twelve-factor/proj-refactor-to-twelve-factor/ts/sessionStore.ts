// sessionStore.ts — сесії залогінених у спільному Redis.
import { createClient } from "redis";
import { config } from "./config";

const r = createClient({ url: config.REDIS_URL });
await r.connect();

const SESSION_TTL = 3600;

export async function rememberLogin(sid: string, userId: number): Promise<void> {
  // Було: MemoryStore — сесії в купі цього процесу.
  await r.setEx(`session:${sid}`, SESSION_TTL, String(userId));  // ← у СПІЛЬНОМУ кеші
}

export async function whoami(sid: string): Promise<number | null> {
  const value = await r.get(`session:${sid}`);
  return value ? Number(value) : null;   // null → протухла або чужа
}
