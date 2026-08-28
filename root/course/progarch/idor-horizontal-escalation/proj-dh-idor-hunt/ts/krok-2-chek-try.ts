app.get("/api/homes/:homeId/devices", requireSession, async (req, res) => {
  const home = await homes.byId(req.params.homeId);   // id — з запиту, тобто від КЛІЄНТА
  // Три несучі властивості чека:
  //  1) НА СЕРВЕРІ  — тут, а не в застосунку (саме клієнт і підставляє чужий id);
  //  2) НА КОЖНОМУ доступі — у цьому обробнику, не «десь раніше по дорозі»;
  //  3) ЗА ОСОБОЮ запитувача — ключ = req.session.userId, НЕ id, надісланий клієнтом.
  if (!home || !home.belongsTo(req.session.userId))
    return res.status(404).end();                      // 404, не 403 — про це нижче
  res.json(await devices.ofHome(home.id));
});
