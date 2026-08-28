class HybridSeam implements SessionSeam {
  constructor(
    private priv: string,
    private pub: string,
    private store: Store,             // тримає лише РЕФРЕШІ, а не гарячий шлях
    private accessTtlSec = 120,       // короткий повідок: 2 хвилини
    private clock: () => number = () => Math.floor(Date.now() / 1000),
  ) {}

  // холодний шлях: логін дає короткий access + непрозорий refreshId (у сторі)
  async login(p: Principal): Promise<{ access: string; refreshId: string }> {
    const refreshId = randomBytes(32).toString("base64url");
    await this.store.set(`refresh:${refreshId}`, JSON.stringify(p), 30 * 24 * 3600);
    return { access: this.issueAccess(p), refreshId };
  }

  private issueAccess(p: Principal): string {
    const now = this.clock();
    return jwt.sign(
      { sub: p.sub, home: p.home, scopes: p.scopes, iat: now, exp: now + this.accessTtlSec },
      this.priv, { algorithm: "RS256" },
    );
  }

  // ГАРЯЧИЙ шлях — суто локальний, як у Б: жодного стору
  async validate(access: string): Promise<Principal | null> {
    try {
      const c = jwt.verify(access, this.pub, {
        algorithms: ["RS256"], clockTimestamp: this.clock(),
      }) as jwt.JwtPayload;
      return { sub: c.sub as string, home: c.home, scopes: c.scopes };
    } catch { return null; }
  }

  // ХОЛОДНИЙ шлях, раз на кілька хвилин: обмін refresh на свіжий access — ТУТ можна відмовити
  async refresh(refreshId: string): Promise<string | null> {
    const raw = await this.store.get(`refresh:${refreshId}`);
    if (!raw) return null;                     // відкликали — нового access не дамо
    return this.issueAccess(JSON.parse(raw) as Principal);
  }

  // орган відкликання: викидаємо refresh зі стору (або в денилист)
  async revoke(refreshId: string): Promise<void> {
    await this.store.del(`refresh:${refreshId}`);
  }
}
