// Контракт шва — незмінний по обидва боки розрізу.
interface DeviceStateReader {
  read(deviceId: string): Promise<DeviceState>;
}

// ДО: твін — сусідній модуль в одному процесі. Виклик у пам'яті.
class InProcessTwin implements DeviceStateReader {
  constructor(private twin: TwinModule) {}
  async read(id: string) {
    return this.twin.snapshot(id);               // наносекунди, без мережі
  }
}

// ПІСЛЯ: твін — окремий сервіс. Той самий контракт, інший транспорт.
class RemoteTwin implements DeviceStateReader {
  constructor(private http: HttpClient, private base: string) {}
  async read(id: string) {
    const res = await this.http.get(
      `${this.base}/devices/${id}/state`,
      { timeoutMs: 200 },                         // мережа зависає — потрібен дедлайн
    );
    return DeviceState.parse(res.body);           // чужі дані — валідуємо на межі
  }
}

// Автоматизаціям видали інтерфейс — вони не знають, який бік шва живий.
const engine = new AutomationEngine(reader);      // reader: DeviceStateReader
