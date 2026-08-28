// Шлях 1: читання завжди з пулу реплік. Швидко й дешево —
// але репліка може ще НЕ мати щойно записаного (застаріле читання).
class ProfileStore {
  constructor(
    private primary: Pool,      // єдина основна — приймає записи
    private replicas: Pool[],   // пул реплік — розносять читання
  ) {}

  async save(userId: string, patch: ProfilePatch): Promise<void> {
    await this.primary.query(
      "UPDATE profiles SET data = $2, updated_at = now() WHERE id = $1",
      [userId, patch],
    );
  }

  async get(userId: string): Promise<Profile> {
    // випадкова репліка — розносимо читання рівномірно
    const r = this.replicas[(Math.random() * this.replicas.length) | 0];
    const { rows } = await r.query(
      "SELECT data FROM profiles WHERE id = $1",
      [userId],
    );
    return rows[0].data;   // може бути версія ДО save(), якщо репліка відстала
  }
}
