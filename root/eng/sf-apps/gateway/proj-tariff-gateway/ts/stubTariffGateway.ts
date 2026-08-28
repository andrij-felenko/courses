// test/stubTariffGateway.ts — підробка: той самий інтерфейс, без мережі.
import { ТарифШлюз } from "../domain/tariffGateway";
import { Напрямок, Тариф } from "../domain/tariff";

export class StubТарифШлюз implements ТарифШлюз {
  constructor(private фіксований: Тариф) {}
  async тарифДля(_: Напрямок): Promise<Тариф> {
    return this.фіксований;   // жодного HTTP — просто віддали, що просили
  }
}

// Тест НАШОГО правила — без сервера, без мережі, за мілісекунди
test("дорогий тариф → самовивіз", async () => {
  const домен = new ДоставкаСервіс(new StubТарифШлюз(new Тариф(500)));  // дорого
  const рішення = await домен.порадитиСпосіб(new Напрямок("SEG_A"));
  expect(рішення).toBe("самовивіз");
});

test("дешевий тариф → доставка", async () => {
  const домен = new ДоставкаСервіс(new StubТарифШлюз(new Тариф(50)));   // дешево
  expect(await домен.порадитиСпосіб(new Напрямок("SEG_A"))).toBe("доставка");
});
