const IDLE_MS = 1000 * 60 * 60 * 24 * 7;      // 7 діб без активності — просрочка
const ABSOLUTE_MS = 1000 * 60 * 60 * 24 * 14; // 14 діб від входу — жорстка стеля

async function authenticate(token: string, db: Db): Promise<Session | null> {
  const s = await db.getSession(sha256(token));
  if (!s) return null;
  const now = Date.now();
  if (now - s.lastSeen > IDLE_MS || now - s.createdAt > ABSOLUTE_MS) {
    await db.deleteSession(sha256(token));  // мертву — прибрати
    return null;
  }
  await db.touchSession(sha256(token), now); // ковзне вікно бездіяльності
  return s;
}

// РОТАЦІЯ під час входу — проти фіксації сесії:
async function loginAndStart(user: User, oldToken: string | null, db: Db): Promise<string> {
  if (oldToken) await db.deleteSession(sha256(oldToken)); // старий ідентифікатор — мертвий
  return createSession(user.id, db);                      // свіжий, невідомий нападнику
}
