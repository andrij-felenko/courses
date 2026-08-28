// Сьогодні — рішення в процесі:
const authz: Authorizer = new InServiceAuthorizer(localMemberships);

// Завтра, коли переростемо в центр, — той самий тип, інша реалізація:
class CentralAuthorizer implements Authorizer {
  constructor(private readonly pdp: PdpClient) {}
  async can(user: User, action: Action, resource: Resource): Promise<boolean> {
    try {
      return await this.pdp.check(user.id, action, resource);  // запит до центрального PDP
    } catch {
      return false;                                            // збій PDP → deny (fail-closed)
    }
  }
}
const authz: Authorizer = new CentralAuthorizer(pdpClient);    // жоден обробник не змінився
