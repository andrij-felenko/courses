// Сервіс пристроїв: обробник команди «відчинити замок»
async function unlockDoor(req: Request, res: Response) {
  const user = req.user;                            // хто прийшов (уже автентифікований)
  const door = await devices.load(req.params.id);  // об'єкт У РУКАХ: у ньому homeId

  if (!authz.can(user, "unlock", door)) {          // рішення — тут, у процесі
    return res.status(403).json({ error: "forbidden" });
  }
  await door.unlock();
  res.json({ ok: true });
}
