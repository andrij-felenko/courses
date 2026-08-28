// Брама 1 — на краю хмари (шлюз): автентифікація + груба авторизація
function edgeGate(req: Request): Subject {
  const subject = verifyAccessToken(req.token);       // підпис локально → суб'єкт, або кине 401
  if (!subject) throw new Http(401);                  // «не знаю тебе»
  if (!policy.mayClass(subject, "device.command"))    // об'єкто-НЕЗАЛЕЖне: роль узагалі командує?
    throw new Http(403);                              // гість — стоп ТУТ, сервіс не потурбовано
  return subject;                                     // несемо доведеного суб'єкта далі
}

// Брама 2 — у сервісі пристроїв: тонка ОБ'ЄКТНА авторизація
async function unlockDoor(subject: Subject, doorId: string) {
  const door = await devices.load(doorId);            // об'єкт У РУКАХ: у ньому homeId
  if (!authz.can(subject, "unlock", door))            // «цей замок — у ТВОЄМУ домі?»
    throw new Http(403);                              // чужий замок — 403, IDOR закрито
  await door.unlock();                                // обидві брами пройдено → сигнал на хаб
}
