// Контекст БУХГАЛТЕРІЇ: юзер — це платник за рахунками
namespace Billing {
  export class Payer {
    constructor(
      readonly id: string,
      readonly name: string,
      readonly taxId: string,           // не null: без ІПН платника немає
      readonly creditLimit: number,     // не null
      readonly iban: string,            // не null
    ) {
      if (!/^\d{8,10}$/.test(taxId))
        throw new Error("ІПН має бути 8–10 цифр");
    }
    // Жодного stage, probability — бухгалтерії байдуже до воронки.
  }
}
