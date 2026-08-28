// 1) Ліниве поле: лінь живе в самому Order — порожній слот плюс геттер.
class OrderLazyField {
  readonly id: number;
  readonly total: number;
  private customerId: number;
  private _customer: Row | null = null;                    // ще не тягли
  constructor(private db: Db, row: Row) {
    this.id = row.id;
    this.total = row.total;
    this.customerId = row.customerId;
  }
  get customer(): Row {
    return (this._customer ??= this.db.findCustomer(this.customerId));
  }
}

// 2) Віртуальний проксі: окремий об'єкт із тим самим інтерфейсом.
interface Customer { readonly name: string; readonly city: string; }

class CustomerProxy implements Customer {
  private real: Row | null = null;
  constructor(private db: Db, private id: number) {}
  private load(): Row { return (this.real ??= this.db.findCustomer(this.id)); }  // справжнього — раз
  get name(): string { return this.load().name; }          // кожен метод делегує
  get city(): string { return this.load().city; }
}

// 3) Привид: сам покупець з одним id і порожніми полями.
class CustomerGhost implements Customer {
  private loaded = false;
  private _name = "";
  private _city = "";
  constructor(private db: Db, readonly id: number) {}       // тотожність правильна від початку
  private fill(): void {
    if (this.loaded) return;
    const row = this.db.findCustomer(this.id);              // один запит — і ВСІ поля разом
    this._name = row.name;
    this._city = row.city;
    this.loaded = true;
  }
  get name(): string { this.fill(); return this._name; }
  get city(): string { this.fill(); return this._city; }
}
