// Знекровлена модель: сам поліс нічого не вміє, лише тримає поля навстіж
class Policy {
  id: string = "";
  status: string = "draft";        // "draft" | "active" | "grace" | "cancelled"
  premium: number = 0;             // сума внеску, у копійках? у гривнях? хтозна
  currency: string = "UAH";
  dueDate: Date = new Date();
  payments: number[] = [];         // суми платежів, теж голі числа
}

// Правило живе ЗЗОВНІ, у сервісі — і кожен викликач тримає свій уламок
class PolicyService {
  activate(p: Policy): void {
    if (p.status !== "draft") throw new Error("wrong state");
    p.status = "active";
  }

  enterGracePeriod(p: Policy): void {
    // тут ЗАБУЛИ перевірити, що поліс узагалі активний
    p.status = "grace";
  }

  addPayment(p: Policy, amount: number): void {
    p.payments.push(amount);        // жодної перевірки: додасться й від'ємне
  }
}
