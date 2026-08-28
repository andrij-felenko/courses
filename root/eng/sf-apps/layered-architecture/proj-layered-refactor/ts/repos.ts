// domain/repos.ts — обіцянки, які домен вимагає від світу (ще не реалізація)
import { Order } from "./order";

export interface ProductRepo {
  // повернути [ціна, залишок] або null, якщо товару немає
  find(sku: string): [price: number, stock: number] | null;
}

export interface OrderRepo {
  add(order: Order): number;              // зберегти, повернути id
  reduceStock(sku: string, qty: number): void;
}
