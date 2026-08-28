enum PolicyStatus { Draft, Active, Grace, Cancelled }

class DomainError extends Error {}   // окремий тип — щоб ловити саме порушення правила

class Policy {
  private _status = PolicyStatus.Draft;
  private _premium = 0;
  private _payments: number[] = [];

  constructor(
    private readonly _id: string,
    private readonly _currency: string,
    private readonly _dueDate: Date,
  ) {}

  // КОМАНДА: правило переходу тепер ТУТ, разом зі своїм вартовим
  activate(): void {
    if (this._status !== PolicyStatus.Draft)
      throw new DomainError("активувати можна лише чернетку");
    this._status = PolicyStatus.Active;
  }

  enterGracePeriod(): void {
    if (this._status !== PolicyStatus.Active)      // ← перевірка, якої бракувало
      throw new DomainError("у пільговий період входять лише з активного");
    this._status = PolicyStatus.Grace;
  }

  get status(): PolicyStatus { return this._status; }
}
