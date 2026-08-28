import jwt from "jsonwebtoken";

class StatelessJwtSeam implements SessionSeam {
  constructor(
    private priv: string,                    // приватний ключ — лише в емітента
    private pub: string,                     // публічний — у кожного, хто перевіряє
    private clock: () => number = () => Math.floor(Date.now() / 1000),
  ) {}

  login(p: Principal): string {
    const now = this.clock();
    return jwt.sign(
      { sub: p.sub, home: p.home, scopes: p.scopes, iat: now, exp: now + 24 * 3600 },
      this.priv,
      { algorithm: "RS256" },   // підпис приватним; expiresIn НЕ передаємо — exp уже в тілі
    );
  }

  async validate(token: string): Promise<Principal | null> {
    try {
      const c = jwt.verify(token, this.pub, {
        algorithms: ["RS256"],
        clockTimestamp: this.clock(), // порівняння exp — проти НАШОГО годинника
      }) as jwt.JwtPayload;
      return { sub: c.sub as string, home: c.home, scopes: c.scopes };
    } catch {
      return null; // прострочений або підроблений — і БІЛЬШЕ дивитися нема куди
    }
  }

  async revoke(_handle: string): Promise<void> {
    // НІКУДИ писати. Сервер не тримає сесій — отже, нема місця сказати «ця вже ні».
    // Єдиний спосіб — завести денилист… але це вже похід у стор на гарячому шляху,
    // тобто вже НЕ stateless. Тож тут — чесний no-op, і в ньому вся рана.
  }
}
