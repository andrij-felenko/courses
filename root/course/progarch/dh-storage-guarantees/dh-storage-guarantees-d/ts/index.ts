function saveHome(db: Database, home: Home): void {
  const tx = db.transaction((h: Home) => {   // єдина транзакція: усе-або-нічого
    db.prepare("UPDATE homes SET threshold=? WHERE id=?").run(h.threshold, h.id);
    db.prepare("DELETE FROM devices WHERE home_id=?").run(h.id);
    const ins = db.prepare(
      "INSERT INTO devices(home_id, id, kind, room) VALUES(?,?,?,?)");
    for (const d of h.devices) ins.run(h.id, d.id, d.kind, d.room);
  });
  tx(home);   // краш посеред → база відкотить усе: напівоновленого дому не існує
}
