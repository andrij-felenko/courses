// Знекровлена модель: сам поліс нічого не вміє, лише зберігає поля
class Policy {
  status: string = "active";
  balance: number = 0;
  dueDate: Date;
}

// Правило живе ЗЗОВНІ, у сервісі — і будь-хто може забути його викликати
class PolicyService {
  enterGracePeriod(p: Policy): void {
    // хто гарантує, що всі перевірки тут, а не в трьох інших сервісах?
    if (p.status !== "active") throw new Error("wrong state");
    p.status = "grace";
  }
}
