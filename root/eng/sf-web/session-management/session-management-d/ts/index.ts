import { randomBytes } from "node:crypto";

// Сервер тримає правду в себе; клієнт отримає лише номер
const sessions = new Map<string, { userId: string; createdAt: number }>();

function login(res: Response, userId: string) {
  const sid = randomBytes(16).toString("hex");        // 128 біт із CSPRNG
  sessions.set(sid, { userId, createdAt: Date.now() });
  res.setHeader("Set-Cookie",
    `sid=${sid}; HttpOnly; Secure; SameSite=Lax; Path=/`);
}

function whoAmI(req: Request): string | null {
  const sid = parseCookie(req.headers.cookie).sid;
  const session = sid ? sessions.get(sid) : undefined;
  return session ? session.userId : null;             // немає запису → анонім
}

function logout(sid: string) {
  sessions.delete(sid);        // знищуємо ПРАВДУ на сервері, не лише cookie
}
