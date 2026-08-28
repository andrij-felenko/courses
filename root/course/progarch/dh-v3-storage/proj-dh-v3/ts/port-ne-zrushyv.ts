interface Device { id: string; kind: string; room: string; state: string; pairedAt: string; }
interface Home {
  id: string; ownerId: string; plan: string; deviceCap: number;
  threshold: number; usedSlots: number;   // лічильник READ-ONLY для застосунку
  devices: Device[];
}

interface DeviceRepository {              // ТОЙ САМИЙ порт із v2, тепер зернистістю агрегату
  saveHome(home: Home): void;
  load(homeId: string): Home | null;
  addDevice(homeId: string, d: Device): boolean;   // False, якщо тариф вичерпано
}

class SqliteDeviceRepository implements DeviceRepository {
  constructor(private db: DatabaseSync) {}

  saveHome(home: Home): void {           // увесь агрегат — в ОДНІЙ транзакції
    this.db.exec("BEGIN IMMEDIATE");     // межа агрегату = межа транзакції
    try {
      this.db.prepare(
        "INSERT INTO home(id, owner_id, plan, device_cap, used_slots, threshold) " +
        "VALUES(?,?,?,?,?,?) " +
        "ON CONFLICT(id) DO UPDATE SET " +           // поклади АБО онови…
        "  plan = excluded.plan, threshold = excluded.threshold"   // …а used_slots НЕ чіпай
      ).run(home.id, home.ownerId, home.plan, home.deviceCap, home.devices.length, home.threshold);
      const insDev = this.db.prepare(
        "INSERT INTO device(id, home_id, kind, room, state, paired_at) VALUES(?,?,?,?,?,?) " +
        "ON CONFLICT(id) DO UPDATE SET room = excluded.room, state = excluded.state");
      for (const d of home.devices)                  // ← збій на будь-якому витку відкотить УСЕ
        insDev.run(d.id, home.id, d.kind, d.room, d.state, d.pairedAt);
      this.db.exec("COMMIT");
    } catch (e) { this.db.exec("ROLLBACK"); throw e; }
  }

  load(homeId: string): Home | null {
    const row = this.db.prepare(
      "SELECT owner_id, plan, device_cap, used_slots, threshold FROM home WHERE id=?"
    ).get(homeId) as any;
    if (!row) return null;
    const devices = this.db.prepare(
      "SELECT id, kind, room, state, paired_at FROM device WHERE home_id=?"
    ).all(homeId).map((r: any) => (
      { id: r.id, kind: r.kind, room: r.room, state: r.state, pairedAt: r.paired_at }));
    return { id: homeId, ownerId: row.owner_id, plan: row.plan, deviceCap: row.device_cap,
             threshold: row.threshold, usedSlots: row.used_slots, devices };
  }

  addDevice(homeId: string, d: Device): boolean {     // слот Й пристрій — атомарно
    this.db.exec("BEGIN IMMEDIATE");                   // замок писаря одразу
    try {
      const bumped = this.db.prepare(
        "UPDATE home SET used_slots = used_slots + 1 " +
        "WHERE id = ? AND used_slots < device_cap"     // ← вартовий: не перевищити тариф
      ).run(homeId);
      if (bumped.changes !== 1) { this.db.exec("ROLLBACK"); return false; }   // 0 → тариф вичерпано
      this.db.prepare(
        "INSERT INTO device(id, home_id, kind, room, state, paired_at) VALUES(?,?,?,?,?,?)"
      ).run(d.id, homeId, d.kind, d.room, d.state, d.pairedAt);
      this.db.exec("COMMIT");                           // слот і пристрій видимі РАЗОМ
      return true;
    } catch (e) { this.db.exec("ROLLBACK"); throw e; }
  }
}
