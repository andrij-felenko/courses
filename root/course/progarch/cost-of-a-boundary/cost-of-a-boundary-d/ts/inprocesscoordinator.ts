// Сценарій «Добрий вечір»: контраст локальної атомарності та мережевої межі

// 1. Монолітний виклик у спільній пам'яті (затримка 5 мкс, детермінована атомарність)
interface Device {
  id: string;
  setPower(state: boolean): void;
  setTargetValue(value: number): void;
}

class InProcessCoordinator {
  constructor(private readonly devices: Map<string, Device>) {}

  public executeEveningScenario(): void {
    const light = this.devices.get("light-living-room");
    const blinds = this.devices.get("blinds-main");
    const thermostat = this.devices.get("thermostat-living-room");
    const lock = this.devices.get("lock-front-door");

    if (!light || !blinds || !thermostat || !lock) {
      throw new Error("Апаратна конфігурація кімнати неповна");
    }

    // Виклики відбуваються синхронно в єдиному адресному просторі.
    // Якщо будь-який пристрій генерує виняток, стек негайно розкручується,
    // запобігаючи переходу системи в неконтрольований стан.
    light.setPower(true);
    blinds.setTargetValue(100);
    thermostat.setTargetValue(20);
    lock.setPower(true);
  }
}

// 2. Винесений сервіс через мережеву межу (часткова відмова та втрата інваріантів)
interface DeviceHttpClient {
  postCommand(deviceId: string, command: string, payload: Record<string, unknown>): Promise<void>;
}

class DistributedCoordinator {
  constructor(private readonly client: DeviceHttpClient) {}

  public async executeEveningScenario(): Promise<void> {
    // Крок 1: Вмикаємо світло (успішно, затримка 22 мс)
    await this.client.postCommand("light-living-room", "set-power", { state: true });

    // Крок 2: Опускаємо жалюзі (успішно, затримка 25 мс)
    await this.client.postCommand("blinds-main", "set-position", { value: 100 });

    try {
      // Крок 3: Запит до термостата потрапляє в мережевий затор або втрату пакета.
      // Клієнт блокується на 2000 мс в очікуванні відповіді від сокета.
      await this.client.postCommand("thermostat-living-room", "set-temp", { value: 20 });
    } catch (error) {
      // Часткова відмова: стан термостата невідомий, двері не замкнено,
      // а дім зависає в неузгодженому стані.
      throw new Error(`Збій сценарію: ${(error as Error).message}`);
    }

    // Крок 4: Ця точка ніколи не досягається у разі таймауту на попередньому кроці
    await this.client.postCommand("lock-front-door", "lock", { state: true });
  }
}
