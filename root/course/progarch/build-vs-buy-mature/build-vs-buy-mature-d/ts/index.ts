// 1. ПОРТ (Інтерфейс) у бізнес-шарі
export interface UserIdentity {
  userId: string;
  email: string;
  isAuthenticated: boolean;
}

export interface IAuthPort {
  authenticate(token: string): Promise<UserIdentity>;
}

// 2. АДАПТЕР A: SaaS Auth0
export class Auth0Adapter implements IAuthPort {
  async authenticate(token: string): Promise<UserIdentity> {
    if (!token) throw new Error("Auth0: Empty token");
    return { userId: "auth0|12345", email: "user@example.com", isAuthenticated: true };
  }
}

// 3. АДАПТЕР B: Self-Hosted Keycloak (Репатріація)
export class KeycloakAdapter implements IAuthPort {
  async authenticate(token: string): Promise<UserIdentity> {
    if (!token) throw new Error("Keycloak: Empty token");
    return { userId: "kc-8899", email: "user@example.com", isAuthenticated: true };
  }
}
