// sync-route.ts — await наскрізь; відповідь = РЕАЛЬНИЙ кінцевий стан
app.post("/homes/:id/lock", async (req, res) => {
  try {
    const r = await withTimeout(hub.send(req.params.id, { cmd: "lock" }), 5_000);
    // Дійшли до замка й почули його — вертаємо стан, який він назвав.
    res.status(200).json({ state: r.state });               // 200 «зроблено»
  } catch (e) {
    if (e instanceof HubTimeout) {
      // Таймаут — це «я не знаю», а не «не вийшло»: замок МІГ клацнути.
      res.status(504).json({ state: "unknown", reason: "хаб мовчить" });
    } else if (e instanceof HubOffline) {
      // Хаба нема на зв'язку — покласти команду нема куди. Вона програна ТУТ.
      res.status(502).json({ state: "unknown", reason: "хаб офлайн" });
    } else {
      res.status(500).json({ state: "unknown" });
    }
  }
});
