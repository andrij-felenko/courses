// domain/tariff.ts — НАШ світ. Мова доставки. Про HTTP не чув.
export class Напрямок {
  constructor(readonly код: string) {}   // "SEG_A", "SEG_B" — наш ключ напрямку
}

export class Тариф {
  constructor(readonly одиниць: number) {}   // уже наше число, не rate_bps
  дорожчийЗа(поріг: number): boolean { return this.одиниць > поріг; }
}

// Доменні помилки: НАШІ поняття біди. У них перекладуться чужі коди.
export class ТарифНедоступний extends Error {
  constructor(readonly напрямок: Напрямок) {
    super(`Тарифу для напрямку ${напрямок.код} немає`);
    this.name = "ТарифНедоступний";
  }
}
export class ДоступПрострочено extends Error {
  constructor() { super("Доступ до служби тарифів прострочено"); this.name = "ДоступПрострочено"; }
}
export class ШлюзНедоступний extends Error {   // сервіс зламався або не відповів
  constructor(readonly причина: string) {
    super(`Служба тарифів недоступна: ${причина}`);
    this.name = "ШлюзНедоступний";
  }
}
