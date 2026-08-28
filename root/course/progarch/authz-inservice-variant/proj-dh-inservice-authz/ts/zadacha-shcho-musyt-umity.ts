// ❌ Тонкий баг: роль перевірено, об'єкт — ні.
async function unlockDoor(req: Request, res: Response) {
  const user = req.user;
  const door = await devices.load(req.params.id);     // у door є homeId
  const role = await memberships.anyRoleOf(user.id);  // «Оксана — мешканка? так, дому 12»
  if (role === "resident" || role === "owner") {      // роль підходить…
    await door.unlock();                              // …а це замок ЧУЖОГО дому!
    return res.json({ ok: true });
  }
  res.status(403).end();
}
