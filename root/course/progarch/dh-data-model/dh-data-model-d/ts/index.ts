class Lock {                                   // СУТНІСТЬ + корінь свого агрегата
  private state: LockState = "Unknown";        // завжди визначений — інваріант 2 тримає тип

  constructor(
    readonly id: DeviceId,
    readonly homeId: HomeId,                    // ← власника вимагають при народженні:
    readonly roomId: RoomId,                    //    інваріант 1 «не буває нічий»
  ) {}

  // Єдині двері всередину. Стан міняють лише через них — сирого поля ззовні не видно.
  lock(): void {
    if (this.state === "Jammed")
      throw new DomainError("заклинений замок не замкнути — спершу ремонт");
    this.state = "Locked";
  }
  unlock(): void {
    if (this.state === "Jammed")
      throw new DomainError("заклинений замок не відчинити командою");
    this.state = "Unlocked";
  }

  reportFromDevice(s: LockState): void { this.state = s; }  // фізика доповіла — приймаємо як є
  isLocked(): boolean { return this.state === "Locked"; }
}
