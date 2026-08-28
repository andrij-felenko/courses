// АНТИПАТЕРН: правило вписане прямо в обробник — і так у кожному з тридцяти
async function unlockDoor(req: Request, res: Response) {
  const user = req.user;
  const door = await devices.load(req.params.id);
  if (door.homeId !== user.homeId ||                        // те саме «член дому + роль»
      (user.role !== "owner" && user.role !== "resident"))  // копіями по всіх маршрутах
    return res.status(403).end();
  await door.unlock();
  res.json({ ok: true });
}
