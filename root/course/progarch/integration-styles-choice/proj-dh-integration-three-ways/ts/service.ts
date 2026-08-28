// devices/service.ts — усередині контексту пристроїв, за його власною стіною
class DevicesService implements DeviceCatalog {
  constructor(private db: Pool) {}                    // ← ЙОГО база, тільки його

  async activeCount({ homeId }: { homeId: number }): Promise<{ count: number }> {
    const { rows } = await this.db.query(
      `SELECT count(*)::int AS n
         FROM devices
        WHERE home_id = $1 AND active = true`,          // той самий SQL — але це ЙОГО SQL
      [homeId],
    );
    return { count: rows[0].n };
  }
}
