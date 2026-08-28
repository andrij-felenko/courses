interface Approver {
  setNext(next: Approver): Approver;
  handle(amount: number): void;
}

// Спільна основа: тримає наступного й уміє передавати далі
abstract class BaseApprover implements Approver {
  private next?: Approver;

  setNext(next: Approver): Approver {
    this.next = next;
    return next;                      // повертаємо наступного — зручно зчіплювати
  }

  handle(amount: number): void {
    if (this.next) this.next.handle(amount);
    else console.log(`Нема кому погодити ${amount}`);
  }
}

class TeamLead extends BaseApprover {
  handle(amount: number): void {
    if (amount <= 1_000) console.log(`Керівник групи погодив ${amount}`);
    else super.handle(amount);        // не моє — передаю далі
  }
}

class Manager extends BaseApprover {
  handle(amount: number): void {
    if (amount <= 10_000) console.log(`Начальник відділу погодив ${amount}`);
    else super.handle(amount);
  }
}

class Director extends BaseApprover {
  handle(amount: number): void {
    if (amount <= 100_000) console.log(`Директор погодив ${amount}`);
    else super.handle(amount);
  }
}
