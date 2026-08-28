class SqliteDeviceRepository implements DeviceRepository {   // той самий порт із v2
  constructor(private db: Database) {}

  saveHome(home: Home): void {
    // увесь агрегат — в ОДНІЙ транзакції: дім і пристрої або разом, або ніяк
    this.db.transaction(() => {                 // commit на виході, rollback на винятку
      this.db.run(
        "INSERT INTO home(id, owner_id, plan, device_cap, threshold) VALUES(?,?,?,?,?) " +
        "ON CONFLICT(id) DO UPDATE SET plan=excluded.plan, threshold=excluded.threshold",
        home.id, home.ownerId, home.plan, home.deviceCap, home.threshold);
      for (const d of home.devices)
        this.db.run(
          "INSERT INTO device(id, home_id, kind, room, state, paired_at) VALUES(?,?,?,?,?,?) " +
          "ON CONFLICT(id) DO UPDATE SET room=excluded.room, state=excluded.state",
          d.id, home.id, d.kind, d.room, d.state, d.pairedAt);
    })();
  }
}
