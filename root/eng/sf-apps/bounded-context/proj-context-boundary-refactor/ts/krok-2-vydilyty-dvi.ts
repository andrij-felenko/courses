// Контекст ПРОДАЖІВ: юзер — це наводка на угоду
namespace Sales {
  export class Lead {
    constructor(
      readonly id: string,
      readonly name: string,
      readonly stage: "new" | "qualified" | "won" | "lost",  // не null!
      readonly probability: number,                           // не null!
      readonly ownerId: string,                               // не null!
    ) {
      if (probability < 0 || probability > 1)
        throw new Error("ймовірність поза [0, 1]");
    }
    // валідність тепер вбудована: ліда без стадії просто не існує.
    // Жодного taxId, iban — цей світ про них не чув.
  }
}
