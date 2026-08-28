// Сутність: рівність — за ТОТОЖНІСТЮ (id), стан вільно змінюється в часі.
class Order {
  private status: "новий" | "оплачений" | "скасований" = "новий";

  constructor(readonly id: string) {}    // id незмінний — це нитка тотожності

  pay(): void  { this.status = "оплачений"; }   // стан МІНЯЄТЬСЯ — і це нормально
  cancel(): void { this.status = "скасований"; }

  equals(other: Order): boolean {
    return this.id === other.id;         // тільки id, атрибути не дивимось
  }
}

const o1 = new Order("ord-42");
o1.pay();                                // стан змінився
const same = new Order("ord-42");        // той самий id — та сама сутність
o1.equals(same);                         // true — попри те, що стани різні
