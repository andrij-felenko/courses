class HybridAuthorizer implements Authorizer {
  constructor(
    private policies: PolicySource,   // РОЗДАНА з центру, оновлюється ФОНОМ (не на запиті)
    private rels: RelationshipCache,  // кеш наскрізного членства над центром зв'язків
    private now: () => number = Date.now,
  ) {}

  async can(user: User, action: Action, resource: Resource): Promise<boolean> {
    let policy: Policy;
    try { policy = this.policies.policy(); }  // читання вказівника — БЕЗ I/O
    catch { return false; }                   // правила ще нема (старт/збій) → deny

    const isMember = await this.rels.isMemberOf(user.id, resource.homeId); // кеш; fail-closed
    const role = user.roleInHome[resource.homeId];                          // локальний факт

    // ВЕРДИКТ — у процесі, за центральним правилом. Жодного стрибка на рішення.
    return policy.evaluate({ action, role, isMember, now: this.now() });
  }
}
