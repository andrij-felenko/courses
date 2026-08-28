// Грубозернистий інтерфейс: один виклик — один перехід через межу.
// Повертає не об'єкти з поведінкою, а пласкі пакунки даних.
interface DeviceDTO {                // самі поля, жодного методу
  type: string; room: string; state: string;
  brightness: number; lastSeen: number;
}
interface Dashboard {
  snapshot(): Promise<DeviceDTO[]>;   // усі 30 пристроїв за один похід
}

const all = await dashboard.snapshot();     // 1 перехід через межу
for (const d of all) render(d.type, d.room, d.state, d.brightness, d.lastSeen);
