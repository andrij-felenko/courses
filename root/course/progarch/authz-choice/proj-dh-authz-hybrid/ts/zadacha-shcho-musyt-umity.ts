// ❌ Три тихі помилки в одному охайному на вигляд класі.
class NaiveHybrid {
  constructor(private policy: Policy, private rels: RelationshipCache) {}

  can(user: User, action: Action, resource: Resource): boolean {   // (1) синхронний — ламає шов А
    let isMember: boolean;
    try {
      isMember = this.rels.isMemberOfSync(user.id, resource.homeId);
    } catch {
      isMember = true;                                             // (2) збій центру → «пустити»
    }
    const role = user.roleInHome[resource.homeId];
    return this.policy.evaluate({ action, role, isMember, now: Date.now() });
  }
}
