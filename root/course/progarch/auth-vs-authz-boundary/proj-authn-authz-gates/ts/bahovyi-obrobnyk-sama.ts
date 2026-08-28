// ── Домен ────────────────────────────────────────────────
type Subject = { id: string };
type Role    = "guest" | "family" | "founder";
type Action  = "read"  | "write"  | "manage";
type Home    = { id: string; ownerId: string };

// Express.Request доповнюємо полем subject (його ставить автентифікація)
declare global {
  namespace Express { interface Request { subject?: Subject } }
}

// Автентифікація — на краю, раз на запит: токен → суб'єкт
function authenticate(req: Request, res: Response, next: NextFunction) {
  const subject = verifyToken(req.header("authorization"));
  if (!subject) {                                    // немає / хибний / протух
    res.set("WWW-Authenticate", "Bearer").status(401).end();
    return;
  }
  req.subject = subject;
  next();
}

// ⛔ БАГ: перевірено лише «хто», не «що саме йому можна»
app.get("/homes/:id/thermostat", authenticate, (req, res) => {
  const home = homes.get(req.params.id);             // :id — рядок від клієнта
  if (!home) return res.status(404).end();
  res.json(readThermostat(home));                    // ← другої брами немає
});
