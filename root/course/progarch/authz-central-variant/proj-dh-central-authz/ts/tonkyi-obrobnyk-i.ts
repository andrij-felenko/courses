// Обробник тонкий: завантаж об'єкт, спитай ШОВ, застосуй вердикт. Правил тут нема.
async function unlockDoor(req: Request, res: Response) {
  const door = await devices.load(req.params.id);      // door.homeId — з НАШОЇ БД, не з рук клієнта
  if (!(await authz.can(req.user, "unlock", door))) {  // рішення — за швом, у центрі
    return res.status(403).json({ error: "forbidden" });
  }
  await door.unlock();
  res.json({ ok: true });
}

// Реалізація шва: те, що у Варіанті А було локальною функцією, тут — похід у центр.
class CentralAuthorizer implements Authorizer {
  constructor(private readonly pdp: PdpClient) {}

  async can(user: User, action: Action, resource: Resource): Promise<boolean> {
    try {
      const v = await this.pdp.check({
        subject:  user.id,
        action,
        resource: `${resource.kind}:${resource.id}`,
        context:  { homeId: resource.homeId }, // факт із ЗАВАНТАЖЕНОГО об'єкта — за нього відповідаємо МИ
      });
      return v.allow;
    } catch {
      return false;                            // центр мовчить → DENY (fail-closed)
    }
  }
}
