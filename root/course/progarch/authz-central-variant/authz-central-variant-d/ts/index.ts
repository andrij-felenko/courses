// Сервіс пристроїв: обробник «відчинити замок». Гейт (PEP) лишився тут,
// але рішення (PDP) — уже не тут: його питають у центрального сервіса.
async function unlockDoor(req: Request, res: Response) {
  const door = await devices.load(req.params.id);   // об'єкт іще під рукою

  const verdict = await authz.check({               // ← стрибок у центр
    subject: req.user.id,                            // хто: Богдан
    action: "unlock",                                // що: відчинити
    resource: `door:${door.id}`,                     // над чим: замок #42
    context: { homeId: door.homeId },                // факти для рішення — з собою
  });

  if (!verdict.allow) return res.status(403).json({ error: "forbidden" });
  await door.unlock();
  res.json({ ok: true });
}
