// Дрібнозернистий інтерфейс: багато маленьких методів.
// Локально — ідеально. По мережі кожен рядок — окремий перехід через межу.
interface Device {
  type(): string;
  room(): string;
  state(): string;
  brightness(): number;
  lastSeen(): number;
}

for (const d of devices)            // 30 пристроїв
  render(d.type(), d.room(), d.state(), d.brightness(), d.lastSeen());
  //     └─ 5 викликів на пристрій × 30 = 150 звернень
