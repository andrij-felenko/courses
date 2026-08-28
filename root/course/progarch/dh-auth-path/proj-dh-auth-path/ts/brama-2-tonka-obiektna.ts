// ── Брама 2: тонка ОБ'ЄКТНА авторизація ──
async function unlockDoor(req: Request, res: Response) {
  const subject = attestedSubject(req);                 // хто — із ЗАСВІДЧЕННЯ, не з токена
  const door = await devices.load(req.params.id);       // об'єкт У РУКАХ: у ньому homeId
  if (!door) return res.status(404).end();
  if (!(await authz.can(subject, "unlock", door)))      // «цей замок — у ТВОЄМУ домі?» ключ = door.homeId
    return res.status(403).end();                       // чужий дім → 403, IDOR закрито
  await door.unlock();                                  // обидві брами пройдено → сигнал на хаб
  res.json({ ok: true });
}
