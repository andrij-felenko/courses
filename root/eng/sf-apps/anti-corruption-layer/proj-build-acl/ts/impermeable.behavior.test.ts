// tests/impermeable.behavior.test.ts
import { translateOrder } from "../src/acl/orderTranslator";
import { UnsupportedByModel } from "../src/domain/errors";
import { Order } from "../src/domain/order";

const good = {
  sku: "ART-00417/RED/XL", qty: 5, status_code: 2, client_ref: "CL:88213",
};

test("валідне замовлення перекладається в чистий Order", () => {
  const order = translateOrder(good);
  expect(order).toBeInstanceOf(Order);
  expect(order.quantity).toBe(5);
  expect(order.product.article.code).toBe("ART-00417");
  expect(order.client.value).toBe("88213");     // "CL:" зрізано
});

// Кожне чуже поняття без пари МУСИТЬ відбитися UnsupportedByModel.
test.each([
  ["повернення",        { ...good, qty: -3 }],
  ["нульова кількість", { ...good, qty: 0 }],
  ["невідомий статус",  { ...good, status_code: 7 }],
  ["кривий SKU",        { ...good, sku: "ART-00417-RED" }],
  ["client без CL:",    { ...good, client_ref: "88213" }],
])("відбиває: %s", (_name, dto) => {
  expect(() => translateOrder(dto)).toThrow(UnsupportedByModel);
});
