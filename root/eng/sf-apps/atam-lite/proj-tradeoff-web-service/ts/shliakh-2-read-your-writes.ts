// Шлях 2: read-your-writes. Після запису «пришпилюємо» читання цього
// користувача до основної на вікно W — доки репліка гарантовано наздожене.
class ProfileStore {
  private readonly windowMs = 1000;   // W = 1 с: стеля лага з запасом

  constructor(
    private primary: Pool,
    private replicas: Pool[],
    private recent: RecentWrites,      // спільний на ВСІ вузли (напр. Redis із TTL)
  ) {}

  async save(userId: string, patch: ProfilePatch): Promise<void> {
    await this.primary.query(
      "UPDATE profiles SET data = $2, updated_at = now() WHERE id = $1",
      [userId, patch],
    );
    await this.recent.mark(userId, this.windowMs);   // «гарячий» на W мілісекунд
  }

  async get(userId: string): Promise<Profile> {
    const hot = await this.recent.isHot(userId);
    const src = hot
      ? this.primary                                   // свіжо писав → з основної
      : this.replicas[(Math.random() * this.replicas.length) | 0];
    const { rows } = await src.query(
      "SELECT data FROM profiles WHERE id = $1",
      [userId],
    );
    return rows[0].data;   // гаряче читання ЗАВЖДИ бачить власний запис
  }
}
