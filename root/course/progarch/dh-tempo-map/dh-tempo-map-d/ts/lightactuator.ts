// Антипатерн: темпове склеювання трьох життєвих циклів в одному модулі
export class LightActuator {
  private pinState: boolean = false;
  private lastToggleTime: number = 0;
  private readonly minIntervalMs: number = 500;

  // Годинник 1: апаратний протокол (живе роками)
  private buildUartFrame(commandByte: number, channel: number): Uint8Array {
    const frame = new Uint8Array(4);
    frame[0] = 0xAA; // Стартовий байт синхронізації
    frame[1] = commandByte;
    frame[2] = channel;
    frame[3] = (frame[0] ^ frame[1] ^ frame[2]) & 0xFF; // Контрольна сума XOR
    return frame;
  }

  // Годинник 2: доменні правила безпеки (живуть місяцями)
  public toggle(channel: number, desiredState: boolean): void {
    const now = Date.now();
    if (now - this.lastToggleTime < this.minIntervalMs) {
      throw new Error("Захист реле від брязкоту: занадто часті виклики");
    }

    const commandByte = desiredState ? 0x01 : 0x00;
    const payload = this.buildUartFrame(commandByte, channel);
    this.sendToSerialBus(payload);

    this.pinState = desiredState;
    this.lastToggleTime = now;
  }

  // Годинник 3: оформлення інтерфейсу (живе днями)
  public formatStatusMessage(channelName: string, isEco: boolean): string {
    const suffix = isEco ? " (екорежим)" : "";
    return this.pinState
      ? `Освітлення «${channelName}» активовано${suffix}`
      : `Освітлення «${channelName}» вимкнено`;
  }

  private sendToSerialBus(bytes: Uint8Array): void {
    // Низькорівневий запис безпосередньо в апаратний UART-дескриптор
  }
}
