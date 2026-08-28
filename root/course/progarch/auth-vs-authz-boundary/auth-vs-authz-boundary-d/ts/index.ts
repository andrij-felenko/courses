app.get("/homes/:id/thermostat", (req, res) => {
  // Питання 1 — автентифікація: хто на іншому кінці?
  const subject = authenticate(req);               // токен → суб'єкт, або нічого
  if (!subject) return res.status(401).end();      // «не знаю тебе» → 401

  // Питання 2 — авторизація: чи можна САМЕ ЦЬОМУ суб'єктові саме ЦЕ?
  const home = homes.get(req.params.id);           // ← об'єкт, якого двері ще не бачили
  if (!canRead(subject, home)) return res.status(403).end();  // «знаю — але ні» → 403

  return res.json(readThermostat(home));           // обидві межі пройдено
});
