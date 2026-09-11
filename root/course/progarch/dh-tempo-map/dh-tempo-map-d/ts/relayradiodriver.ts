// 1. Апаратний драйвер: низька частота змін (роки)
export class RelayRadioDriver {
  private readonly startByte = 0xAA;

  public sendSwitchCommand(channel: number, state: boolean): void {
    const commandByte = state ? 0x01 : 0x00;
    const checksum = (this.startByte ^ commandByte ^ channel) & 0xFF;
    const frame = new Uint8Array([this.startByte, commandByte, channel, checksum]);
    this.transmitUart(frame);
  }

  private transmitUart(frame: Uint8Array): void {
    // Фізичний обмін байтами через апаратну шину хабу
  }
}

// 2. Доменні правила та безпека обладнання: середня частота змін (місяці)
export class RelaySafetyGuard {
  private readonly minIntervalMs = 500;
  private lastSwitchTime = 0;

  constructor(private readonly driver: RelayRadioDriver) {}

  public executeSwitch(channel: number, state: boolean): void {
    const now = Date.now();
    if (now - this.lastSwitchTime < this.minIntervalMs) {
      throw new Error("Захист реле від брязкоту: команда відхилена");
    }

    this.driver.sendSwitchCommand(channel, state);
    this.lastSwitchTime = now;
  }
}

// 3. Інтерфейсне оформлення: надвисока частота змін (дні)
export class LightNotificationPresenter {
  public formatState(channelName: string, state: boolean, isEco: boolean): string {
    const ecoSuffix = isEco ? " (екорежим)" : "";
    return state
      ? `Освітлення «${channelName}» активовано${ecoSuffix}`
      : `Освітлення «${channelName}» вимкнено`;
  }
}
