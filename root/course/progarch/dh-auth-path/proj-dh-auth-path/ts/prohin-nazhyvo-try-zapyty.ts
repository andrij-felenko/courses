// Членство й ролі (те, що всередині сервісу знає про доми)
const ACTIONS_BY_ROLE = {
  owner:    new Set(["unlock", "lock", "view", "configure"]),
  resident: new Set(["unlock", "lock", "view"]),
  guest:    new Set(["view"]),
} as const;
const membership: Record<string, Record<string, keyof typeof ACTIONS_BY_ROLE>> = {
  bohdan: { "home-7": "resident" },     // Богдан — мешканець дому 7
  guest7: { "home-7": "guest" },        // Гість — лише глядач у домі 7
};
const locks: Record<string, { homeId: string }> = {
  "42": { homeId: "home-7" },           // Богданів замок
  "99": { homeId: "home-3" },           // Мартин замок
};

// «Підпис» клієнтського токена = чи є він у таблиці виданих
const TOKENS: Record<string, Subject> = {
  "tok-bohdan": { id: "bohdan", scopes: ["device:command", "device:view"] },
  "tok-guest":  { id: "guest7", scopes: ["device:view"] },
};
const verifyAccessToken = (auth?: string): Subject | null =>
  (auth && TOKENS[auth.replace(/^Bearer /, "")]) || null;

function can(sub: Subject, action: string, lock: { homeId: string }): boolean {
  const role = membership[sub.id]?.[lock.homeId];   // ключ пошуку — дім САМОГО замка
  if (!role) return false;                          // не член цього дому → ні (IDOR закрито)
  return ACTIONS_BY_ROLE[role].has(action);         // відмова за замовчуванням
}

// ── Ярус 2: сервіс пристроїв (Брама 2) ──
function devicesService(path: string, att: { sub: string; aud: string }): string {
  if (att.aud !== "devices") return "Брама2 ✗ 401 (чуже засвідчення)";
  const subject: Subject = { id: att.sub, scopes: [] };   // хто — із ЗАСВІДЧЕННЯ
  const id = path.split("/")[2];                          // /devices/42/unlock → "42"
  const lock = locks[id];
  if (!lock) return "Брама2 · 404 (нема замка)";
  if (!can(subject, "unlock", lock))
    return `Брама1 ✓ (скоуп є) → засвідчення → Брама2 ✗ 403 (замок #${id} у ${lock.homeId}, не твоєму) — IDOR спіймано`;
  return `Брама1 ✓ → засвідчення → Брама2 ✓ (замок #${id} у домі 7) → 200, замок відчинено`;
}

// ── Ярус 1: шлюз (Брама 1) → карбує засвідчення → кличе сервіс ──
function gateway(path: string, auth: string): string {
  const subject = verifyAccessToken(auth);
  if (!subject) return "Брама1 ✗ 401 (токен не впізнано)";
  if (!subject.scopes.includes("device:command"))
    return "Брама1 ✗ 403 (нема скоупу device:command) — сервіс не потурбовано";
  const attestation = { sub: subject.id, aud: "devices" };   // «підписане» шлюзом
  return devicesService(path, attestation);                  // переслали ЗАСВІДЧЕННЯ, не токен
}

for (const [who, path, auth] of [
  ["Богдан", "/devices/42/unlock", "Bearer tok-bohdan"],
  ["Гість ", "/devices/42/unlock", "Bearer tok-guest"],
  ["Богдан", "/devices/99/unlock", "Bearer tok-bohdan"],
] as const) {
  console.log(`${who} ${path.padEnd(20)} → ${gateway(path, auth)}`);
}
