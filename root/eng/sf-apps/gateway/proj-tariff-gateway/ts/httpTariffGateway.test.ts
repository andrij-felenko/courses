// test/httpTariffGateway.test.ts — точкові проби САМОГО шлюзу.
import { HttpТарифШлюз } from "../http/httpTariffGateway";
import { ТарифНедоступний, ДоступПрострочено, Напрямок } from "../domain/tariff";

// маленька підміна транспорту: шлюз дістане цей статус, у мережу не піде
function шлюзІзВідповіддю(статус: number, тіло: any = {}) {
  const g = new HttpТарифШлюз("http://x", "tok");
  (g as any).httpGet = async () => ({ статус, тіло: async () => тіло });
  // (у бойовому коді транспорт передають у конструктор — тут спрощено)
  return g;
}

test("406 → ТарифНедоступний", async () => {
  const g = шлюзІзВідповіддю(406);
  await expect(g.тарифДля(new Напрямок("SEG_A"))).rejects.toThrow(ТарифНедоступний);
});

test("419 → ДоступПрострочено", async () => {
  const g = шлюзІзВідповіддю(419);
  await expect(g.тарифДля(new Напрямок("SEG_A"))).rejects.toThrow(ДоступПрострочено);
});

test("200 + rate_bps=500 → Тариф(5)", async () => {
  const g = шлюзІзВідповіддю(200, { rate_bps: 500 });
  const t = await g.тарифДля(new Напрямок("SEG_A"));
  expect(t.одиниць).toBe(5);   // 500 / 100 — переклад форми відпрацював
});
