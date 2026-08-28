// ── Межа хмари, бік сервісу: приймаємо ЗАСВІДЧЕННЯ, не клієнтський токен ──
function attestedSubject(req: Request): Subject {
  const token = req.header("x-dh-attestation");
  if (!token) throw new Http(401);                       // напряму, без шлюзу, без засвідчення → стоп (fail-closed)
  try {
    const c = jwt.verify(token, GATEWAY_INTERNAL_PUBLIC_KEY, {
      algorithms: ["RS256"],
      issuer: "edge-gateway",     // підписав саме шлюз
      audience: "devices",        // і саме НАМ, а не іншому сервісу
    }) as jwt.JwtPayload;
    return { id: c.sub as string, scopes: (c.scopes as string[]) ?? [] };
  } catch {
    throw new Http(401);          // підроблене / протухле / чуже aud → «не знаю тебе»
  }
}
