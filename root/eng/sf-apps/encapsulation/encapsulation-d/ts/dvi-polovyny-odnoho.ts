class Account {
  #balance = 0;                 // приховане: ззовні не видно й не змінити

  deposit(sum: number): void {
    if (sum <= 0) throw new Error("сума має бути додатною");
    this.#balance += sum;
  }
  withdraw(sum: number): void {
    if (sum <= 0) throw new Error("сума має бути додатною");
    if (sum > this.#balance) throw new Error("недостатньо коштів");  // інваріант під захистом
    this.#balance -= sum;
  }
  get amount(): number { return this.#balance; }   // лише читання
}
