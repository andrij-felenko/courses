// ЄДИНИЙ писар device_card; живиться тією самою шиною, що й усі
class DeviceCardProjector {
  onEvent(e: DeviceEvent): void {
    // 1) голова картки (ім'я, кімната) — раз, коли пристрій уперше побачено:
    //    рядок мусить існувати ДО того, як писати в нього вимір
    if (!db.hasCard(e.deviceId)) {
      const d = control.getDevice(e.deviceId);   // ОДИН виклик на пристрій за життя
      db.insertHead(e.deviceId, e.homeId, d.name, d.room);
    }
    // 2) вимір — просто з події, у вже наявний рядок:
    db.updateReading(e.deviceId, e.value, e.unit, e.at);
  }
}
