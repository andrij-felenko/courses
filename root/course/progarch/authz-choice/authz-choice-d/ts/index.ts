// Гібридний авторизатор: політика — з центру, ОЦІНКА — локальна, дані — за місцем
class HybridAuthorizer {
  constructor(
    private policy: Policy,          // роздано з ЦЕНТРУ (підписаний бандл), оновлюється фоном
    private rels: RelationshipCache, // кеш наскрізних зв'язків над центральним сховищем
  ) {}

  can(user: User, action: string, resource: Resource): boolean {
    // наскрізний факт — з кеша над центром (мережа лише на промах, і то рідко)
    const isMember = this.rels.isMemberOf(user.id, resource.homeId);
    // локальний факт — тут-таки, поруч
    const role = user.roleInHome[resource.homeId];

    // ВЕРДИКТ обчислюється ЛОКАЛЬНО, без стрибка — за центральним правилом
    return this.policy.evaluate({ action, role, isMember, now: Date.now() });
  }
}

// обробник як був — гейт лишився викликом функції, начинку не видно
if (!authz.can(user, "unlock", door)) return res.status(403).end();
await door.unlock();
