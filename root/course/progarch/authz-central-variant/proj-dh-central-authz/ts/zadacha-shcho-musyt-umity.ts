// ❌ Тонкий баг: центр питаємо чесно — але факт для рішення беремо з РУК КЛІЄНТА.
async function unlockDoor(req: Request, res: Response) {
  const verdict = await pdp.check({
    subject:  req.user.id,                  // хто — з автентифікованої сесії (це чесно)
    action:   "unlock",
    resource: `door:${req.params.id}`,      // над чим — door:42
    context:  { homeId: req.body.homeId },  // ← homeId ПРИЙШОВ ІЗ ТІЛА ЗАПИТУ
  });
  if (!verdict.allow) return res.status(403).end();
  await devices.unlock(req.params.id);
  res.json({ ok: true });
}
