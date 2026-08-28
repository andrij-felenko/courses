// Дозволи за роллю — ЄДИНА таблиця правила. Усе, чого тут НЕ виписано, — заборонено.
const ACTIONS_BY_ROLE: Record<Role, ReadonlySet<Action>> = {
  owner:    new Set(["unlock", "lock", "view", "configure"]),
  resident: new Set(["unlock", "lock", "view"]),
  guest:    new Set(["view"]),
};

class InServiceAuthorizer implements Authorizer {
  constructor(private readonly memberships: Memberships) {}

  async can(user: User, action: Action, resource: Resource): Promise<boolean> {
    // Ключ пошуку — дім САМОГО об'єкта. Тут і закривається IDOR.
    const role = await this.memberships.roleIn(user.id, resource.homeId);
    if (role === undefined) return false;               // не член ЦЬОГО дому → ні
    return ACTIONS_BY_ROLE[role]?.has(action) ?? false; // відмова за замовчуванням
  }
}
