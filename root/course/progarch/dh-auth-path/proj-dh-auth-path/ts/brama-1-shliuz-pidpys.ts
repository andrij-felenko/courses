// Спільний словник хмари DH
type Subject = { id: string; scopes: string[] };   // доведена особа + грубі скоупи з токена

// ── Брама 1: шлюз на краю хмари ─────────────────────────────────────────────
function edgeGate(req: Request): string {
  const subject = verifyAccessToken(req.header("authorization"));  // підпис ключем ЕМІТЕНТА, локально
  if (!subject) throw new Http(401);                               // печатка/термін не зійшлись → «не знаю тебе»

  if (!subject.scopes.includes("device:command"))                 // об'єкто-НЕЗАЛЕЖне: роль узагалі командує?
    throw new Http(403);                                          // гість (лише device:view) — стоп ТУТ, сервіс не потурбовано

  return mintAttestation(subject);   // суб'єкт доведено → карбуємо СВІЖЕ засвідчення саме для сервісу пристроїв
}

// Внутрішнє засвідчення: короткий токен «це справді Богдан», підписаний ключем ШЛЮЗУ.
function mintAttestation(subject: Subject): string {
  const now = Math.floor(Date.now() / 1000);
  return jwt.sign(
    { sub: subject.id, scopes: subject.scopes,
      iss: "edge-gateway", aud: "devices",      // від кого й КОМУ — інший сервіс його не прийме
      iat: now, exp: now + 10 },                // живе 10 с — рівно на один стрибок углиб
    GATEWAY_INTERNAL_PRIVATE_KEY,               // НЕ той ключ, що перевіряє клієнтські токени!
    { algorithm: "RS256" },
  );
}

// Переслати в сервіс: кладемо ЗАСВІДЧЕННЯ, прибираємо клієнтський токен.
async function forwardToDevices(req: Request, attestation: string): Promise<Response> {
  const headers = new Headers({ "x-dh-attestation": attestation }); // свіже, підписане шлюзом
  // Authorization (клієнтський токен) НЕ переслали — у сервісі він і не потрібен, і не бажаний.
  return fetch(`http://devices.internal${req.path}`, { method: req.method, headers, body: req.rawBody });
}
