import type { Request, Response } from "express";

// Багата модель замовлення — те, що реально є в системі.
interface Money { value: number; currency: string; }   // {value, currency}
interface Order { id: number; amount: Money; }

declare function loadOrders(req: Request): Order[];      // спільне джерело даних

// Звуження до бідного формату v1: валюту відкидаємо, лишаємо ціле value.
declare function toV1(orders: Order[]): unknown;

// Телеметрія цього шляху (той самий DeprecationMeter, окремий модуль).
const ordersV1Meter = new DeprecationMeter();

// ── НОВИЙ ШЛЯХ: повна реалізація, джерело правди ────────────────────────────
// GET /api/v2/orders  — формат v2: amount = {value, currency}
export function handleOrdersV2(req: Request, res: Response): void {
  const orders = loadOrders(req);   // єдина логіка вибірки
  res.status(200).json(orders);     // багатий формат
}

// ── СТАРИЙ ШЛЯХ: тонка обгортка над новим ───────────────────────────────────
// GET /api/v1/orders — формат v1: amount = ціле (копійки), без валюти.
// Делегує в спільну логіку, ЗВУЖУЄ результат, чіпляє попередження й лічить себе.
export function handleOrdersV1(req: Request, res: Response): void {
  // 1. Спільна логіка — та сама, що в v2. Жодного дубля вибірки даних.
  const orders = loadOrders(req);

  // 2. ЗВУЖЕННЯ: багатий Order → бідний формат v1.
  //    Звузити повне до неповного — завжди можна; тут просто губимо currency.
  const body = toV1(orders);

  // 3. Попередження — відповідь валідна, але чесно каже «переходь».
  markDeprecated(res,
    1735689600,                    // deprecated_since: 2025-01-01
    1798761600,                    // sunset_at:        2027-01-01
    "/api/v2/orders",
    "https://api.example.com/deprecations/orders-v1");

  res.status(200).json(body);

  // 4. Телеметрія: хтось іще ходить старим шляхом — рахуємо й записуємо, хто.
  ordersV1Meter.record(identifyCaller(req));
}
