app.get("/api/homes/:homeId/devices/:deviceId", requireSession, async (req, res) => {
  const home = await homes.byId(req.params.homeId);
  if (!home || !home.belongsTo(req.session.userId))
    return res.status(404).end();
  const device = await devices.byId(req.params.deviceId);
  // Мало, що дім наш: пристрій має належати САМЕ цьому дому. Інакше
  // /homes/<мій>/devices/<чужий> пройде — власність перевірено не на тому об'єкті.
  if (!device || device.homeId !== home.id)
    return res.status(404).end();
  res.json(device);
});
