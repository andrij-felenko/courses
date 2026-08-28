function canRead(subject: Subject, home: Home): boolean {
  return home.ownerId === subject.id;                // поки що — тільки власник
}

app.get("/homes/:id/thermostat", authenticate, (req, res) => {
  const home = homes.get(req.params.id);
  if (!home) return res.status(404).end();
  if (!canRead(req.subject!, home))                  // ← друга брама, ПІСЛЯ завантаження
    return res.status(403).end();
  res.json(readThermostat(home));
});
