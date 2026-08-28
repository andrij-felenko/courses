// cookie_engine.ts
import crypto from "node:crypto";

export type SameSiteMode = "Strict" | "Lax" | "None";

export interface CookieOptions {
  maxAge?: number;           // час життя у секундах
  expires?: Date;            // абсолютна дата згасання
  domain?: string;           // домен видимості
  path?: string;             // шлях видимості
  secure?: boolean;          // обов'язковий TLS
  httpOnly?: boolean;        // захист від XSS
  sameSite?: SameSiteMode;   // міжсайтова ізоляція
  partitioned?: boolean;     // CHIPS-ізоляція
}

export class CookieError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CookieError";
  }
}

/**
 * Стійкий парсер вхідного заголовка Cookie (RFC 6265)
 */
export function parseCookies(header: string | undefined | null): Map<string, string> {
  const result = new Map<string, string>();
  if (!header || typeof header !== "string") {
    return result;
  }

  const pairs = header.split(";");
  for (const pair of pairs) {
    const trimmed = pair.trim();
    if (!trimmed) continue;

    const eqIdx = trimmed.indexOf("=");
    if (eqIdx === -1) {
      // Cookie без знака '=' вважається ключем із порожнім значенням
      const key = decodeSafely(trimmed);
      if (key && !result.has(key)) result.set(key, "");
      continue;
    }

    const rawKey = trimmed.slice(0, eqIdx).trim();
    let rawVal = trimmed.slice(eqIdx + 1).trim();

    // Зняття подвійних лапок за стандартом Netscape / RFC 6265
    if (rawVal.startsWith('"') && rawVal.endsWith('"') && rawVal.length >= 2) {
      rawVal = rawVal.slice(1, -1);
    }

    const key = decodeSafely(rawKey);
    const val = decodeSafely(rawVal);

    if (key && !result.has(key)) {
      result.set(key, val);
    }
  }

  return result;
}

/**
 * Серіалізатор Set-Cookie з повною перевіркою префіксів (RFC 6265bis)
 */
export function serializeSetCookie(
  name: string,
  value: string,
  options: CookieOptions = {}
): string {
  // 1. Валідація коректності імені
  const fieldContentRegExp = /^[\u0021-\u003A\u003C\u007E]+$/;
  if (!name || !fieldContentRegExp.test(name)) {
    throw new CookieError(`Неприпустимі символи в імені cookie: "${name}"`);
  }

  // 2. Валідація захисних префіксів RFC 6265bis
  if (name.startsWith("__Secure-")) {
    if (!options.secure) {
      throw new CookieError(`Префікс __Secure- вимагає прапорця secure: true`);
    }
  }

  if (name.startsWith("__Host-")) {
    if (!options.secure) {
      throw new CookieError(`Префікс __Host- вимагає прапорця secure: true`);
    }
    if (options.domain) {
      throw new CookieError(`Префікс __Host- забороняє вказувати domain`);
    }
    if (options.path !== "/") {
      throw new CookieError(`Префікс __Host- вимагає path: "/"`);
    }
  }

  // 3. Кодування значення для уникнення роздільників і некоректного UTF-8
  const encodedValue = encodeURIComponent(value);
  const parts: string[] = [`${name}=${encodedValue}`];

  // 4. Формування директив
  if (options.maxAge !== undefined) {
    if (Number.isNaN(options.maxAge)) {
      throw new CookieError("maxAge повинен бути валідним числом");
    }
    parts.push(`Max-Age=${Math.floor(options.maxAge)}`);
  }

  if (options.domain) {
    parts.push(`Domain=${options.domain}`);
  }

  if (options.path) {
    parts.push(`Path=${options.path}`);
  }

  if (options.expires) {
    parts.push(`Expires=${options.expires.toUTCString()}`);
  }

  if (options.httpOnly) {
    parts.push("HttpOnly");
  }

  if (options.secure) {
    parts.push("Secure");
  }

  if (options.sameSite) {
    const mode = options.sameSite;
    if (mode === "None" && !options.secure) {
      throw new CookieError(`SameSite=None обов'язково вимагає прапорця secure: true`);
    }
    parts.push(`SameSite=${mode}`);
  }

  if (options.partitioned) {
    parts.push("Partitioned");
  }

  return parts.join("; ");
}

/**
 * Валідація підписаного значення в константному часі (Constant-Time Verification)
 */
export function verifySignedCookie(signedValue: string, secret: string): string | null {
  const lastDot = signedValue.lastIndexOf(".");
  if (lastDot === -1) return null;

  const value = signedValue.slice(0, lastDot);
  const signature = signedValue.slice(lastDot + 1);

  const expectedSig = crypto
    .createHmac("sha256", secret)
    .update(value)
    .digest("base64url");

  const sigBuf = Buffer.from(signature);
  const expBuf = Buffer.from(expectedSig);

  if (sigBuf.length !== expBuf.length) return null;
  return crypto.timingSafeEqual(sigBuf, expBuf) ? value : null;
}

/**
 * Безпечне декодування: не падає на пошкоджених відсоткових послідовностях
 */
function decodeSafely(str: string): string {
  try {
    return decodeURIComponent(str);
  } catch {
    return str; // повертаємо вихідний рядок, якщо послідовність пошкоджена
  }
}
