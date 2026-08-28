// ── 2. Сутності-корені малих агрегатів ──
class Lock {                                   // СУТНІСТЬ + корінь свого агрегата
  private state: LockState = "Unknown";        // завжди визначений (інваріант 2)

  constructor(
    readonly id: DeviceId,
    readonly homeId: HomeId,                    // ← власника вимагає конструктор:
    readonly location: Location,                //    інваріант 1 «не буває нічий»
  ) {}

  // Локальний НАМІР (кнопка в застосунку). Заклинений — командою не чіпаємо.
  lock(): void {
    if (this.state === "Jammed")
      throw new DomainError(`замок ${this.id} заклинило — командою не замкнути, спершу ремонт`);
    this.state = "Locked";
  }
  unlock(): void {
    if (this.state === "Jammed")
      throw new DomainError(`замок ${this.id} заклинило — командою не відчинити`);
    this.state = "Unlocked";
  }

  // ПРАВДА з поля: фізика доповіла — приймаємо як є (навіть Jammed).
  reportFromDevice(s: LockState): void { this.state = s; }

  isLocked(): boolean { return this.state === "Locked"; }
  get current(): LockState { return this.state; }
}

class Home {                                   // окремий МАЛИЙ агрегат
  private mode: HomeMode = "Home";
  private readonly roomIds: RoomId[] = [];
  private readonly memberIds: UserId[] = [];
  private readonly lockIds: DeviceId[] = [];   // ← лише id, НЕ живі об'єкти замків

  constructor(readonly id: HomeId, readonly ownerId: UserId) {}  // дім не буває без власника

  setMode(m: HomeMode): void { this.mode = m; } // міняє СВІЙ стан — і тільки
  get currentMode(): HomeMode { return this.mode; }

  addRoom(r: RoomId): void { this.roomIds.push(r); }
  admit(u: UserId): void { this.memberIds.push(u); }
  attachLock(d: DeviceId): void { this.lockIds.push(d); }
  get locks(): readonly DeviceId[] { return this.lockIds; }
}
