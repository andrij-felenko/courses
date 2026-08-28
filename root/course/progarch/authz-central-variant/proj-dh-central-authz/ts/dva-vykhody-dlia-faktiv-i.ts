// Вихід 2: центр тримає ГРАФ КОРТЕЖІВ і бере факти З ГРАФА, а не з чужого слова.
//   door:42  #home                home:7        (пише сервіс пристроїв)
//   home:7   #member(resident)    user:bohdan   (пише сервіс домогосподарств)
interface TupleStore {
  homeOf(object: string): Promise<string | undefined>;             // door:42 → home:7
  roleOf(home: string, subject: string): Promise<Role | undefined>; // home:7, user:bohdan → resident
}

const ACTIONS_BY_ROLE: Record<Role, ReadonlySet<Action>> = {
  owner:    new Set(["unlock", "lock", "view", "configure"]),
  resident: new Set(["unlock", "lock", "view"]),
  guest:    new Set(["view"]),
};

class GraphPdp implements PdpClient {
  constructor(private readonly tuples: TupleStore) {}

  async check(req: DecisionRequest): Promise<DecisionResponse> {
    const home = await this.tuples.homeOf(req.resource);            // 1) чий це дім — З ГРАФА, не з context
    if (!home) return { allow: false, reason: `no home for ${req.resource}` };

    const role = await this.tuples.roleOf(home, `user:${req.subject}`); // 2) роль суб'єкта В ЦЬОМУ домі
    if (!role) return { allow: false, reason: `${req.subject} not in ${home}`, home };

    const ok = ACTIONS_BY_ROLE[role]?.has(req.action) ?? false;    // 3) відмова за замовчуванням
    return { allow: ok, reason: ok ? "ok" : `${role} may not ${req.action}`, home };
  }
}
