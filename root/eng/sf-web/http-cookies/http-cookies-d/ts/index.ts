import { IncomingMessage, ServerResponse } from "node:http";

interface SessionUser {
  userId: string;
  role: string;
}

// Проста імітація сховища сесій
const sessionStore = new Map<string, SessionUser>();

/**
 * Парсинг вхідного заголовка Cookie
 */
function getCookie(req: IncomingMessage, name: string): string | null {
  const header = req.headers.cookie;
  if (!header) return null;

  const matches = header.split(";");
  for (const item of matches) {
    const [k, v] = item.trim().split("=");
    if (k === name && v) {
      return decodeURIComponent(v);
    }
  }
  return null;
}

/**
 * Безпечна установка сесійного cookie з префіксом __Host-
 */
function setSessionCookie(res: ServerResponse, sid: string): void {
  // Використовуємо суворий префікс __Host- для захисту від піддоменів
  const cookieValue = [
    `__Host-sid=${encodeURIComponent(sid)}`,
    "Path=/",
    "Max-Age=86400",          // 24 години
    "HttpOnly",               // захист від XSS
    "Secure",                 // передача тільки через HTTPS
    "SameSite=Lax"            // захист від CSRF
  ].join("; ");

  res.setHeader("Set-Cookie", cookieValue);
}

/**
 * Видалення сесійного cookie
 */
function clearSessionCookie(res: ServerResponse): void {
  res.setHeader("Set-Cookie", "__Host-sid=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax");
}

export function handleLogin(res: ServerResponse, userId: string, sid: string): void {
  sessionStore.set(sid, { userId, role: "member" });
  setSessionCookie(res, sid);
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ status: "logged_in" }));
}
