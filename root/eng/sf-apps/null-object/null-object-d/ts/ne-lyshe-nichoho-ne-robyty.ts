interface Customer {
  name(): string;
  discountRate(): number;
}

class RegularCustomer implements Customer {
  constructor(private _name: string, private rate: number) {}
  name(): string { return this._name; }
  discountRate(): number { return this.rate; }
}

class NullCustomer implements Customer {
  name(): string { return "Гість"; }        // нейтральне ім'я
  discountRate(): number { return 0; }      // жодної знижки — розумний типовий стан
}

function findCustomer(id: string): Customer {
  return db.lookup(id) ?? new NullCustomer();  // ніколи не повертаємо null
}
