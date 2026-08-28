import { createHmac, timingSafeEqual } from "node:crypto";

// Node вміє кодек 'base64url' (від v14) — він без службових '='.
const enc = (buf: Buffer): string => buf.toString("base64url");
const dec = (s: string): Buffer => Buffer.from(s, "base64url");

const hs256 = (msg: string, secret: Buffer): Buffer =>
  createHmac("sha256", secret).update(msg).digest();

type Claims = Record<string, unknown>;

// ── ВИДАЧА ────────────────────────────────────────────────────────────────
export function issue(claims: Claims, secret: Buffer, ttl = 900): string {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: "HS256", typ: "JWT" };
  const payload = { ...claims, iat: now, nbf: now, exp: now + ttl };
  const signingInput =
    enc(Buffer.from(JSON.stringify(header))) + "." +
    enc(Buffer.from(JSON.stringify(payload)));
  return `${signingInput}.${enc(hs256(signingInput, secret))}`;
}

// ── ПЕРЕВІРКА ──────────────────────────────────────────────────────────────
export function verify(token: string, secret: Buffer, leeway = 30): Claims {
  const parts = token.split(".");
  if (parts.length !== 3) throw new Error("не три частини");
  const [headerB64, payloadB64, sigB64] = parts;

  // (1) АЛГОРИТМ ПРИБИТО
  const header = JSON.parse(dec(headerB64).toString());
  if (header.alg !== "HS256") throw new Error("несподіваний alg");

  // (2) СТАЛИЙ ЧАС: timingSafeEqual вимагає буфери однакової довжини
  const expected = hs256(`${headerB64}.${payloadB64}`, secret);
  const got = dec(sigB64);
  if (expected.length !== got.length || !timingSafeEqual(expected, got))
    throw new Error("підпис не збігається");

  // (3) ЧАСОВІ ТВЕРДЖЕННЯ
  const payload = JSON.parse(dec(payloadB64).toString()) as Claims;
  const now = Math.floor(Date.now() / 1000);
  const num = (k: string) =>
    typeof payload[k] === "number" ? (payload[k] as number) : undefined;
  const exp = num("exp"), nbf = num("nbf"), iat = num("iat");
  if (exp !== undefined && now > exp + leeway) throw new Error("протермінований");
  if (nbf !== undefined && now + leeway < nbf) throw new Error("ще не набув чинності");
  if (iat !== undefined && now + leeway < iat) throw new Error("виданий у майбутньому");
  return payload;
}
