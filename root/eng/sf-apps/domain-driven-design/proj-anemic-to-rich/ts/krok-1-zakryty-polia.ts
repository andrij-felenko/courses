class Policy {
  // поля закриті: ззовні до них уже не дотягтися напряму
  private _status = "draft";
  private _premium = 0;
  private _payments: number[] = [];

  constructor(
    private readonly _id: string,
    private readonly _currency: string,
    private readonly _dueDate: Date,
  ) {}

  // назовні — лише читання того, що справді потрібне іншим шарам
  get id(): string { return this._id; }
  get status(): string { return this._status; }
  get premium(): number { return this._premium; }
  // ЖОДНОГО set status / set premium: змінити стан ззовні вже не можна
}
