// Фабрика брами: мідлвар, що вантажить дім і пускає лише з правом на дію.
// Обробник дістає вже авторизований дім у res.locals — забути перевірку ніде.
function requireHome(action: Action): RequestHandler {
  return (req, res, next) => {
    const home = homes.get(req.params.id);
    if (!home) return res.status(404).end();
    if (!can(req.subject!, action, home)) return res.status(403).end();
    res.locals.home = home;                          // далі — вже авторизований обʼєкт
    next();
  };
}

app.get("/homes/:id/thermostat", authenticate, requireHome("read"), (req, res) => {
  res.json(readThermostat(res.locals.home));         // право вже перевірено вище
});
app.put("/homes/:id/thermostat", authenticate, requireHome("write"), (req, res) => {
  setThermostat(res.locals.home, req.body.target);
  res.status(204).end();                             // сюди Гриць-гість не дійде
});
