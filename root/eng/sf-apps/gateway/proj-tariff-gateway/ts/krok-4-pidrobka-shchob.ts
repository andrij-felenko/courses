// domain/доставкаСервіс.ts — НАШЕ правило. Кличе шлюз через ІНТЕРФЕЙС.
import { ТарифШлюз } from "./tariffGateway";
import { Напрямок } from "./tariff";

export class ДоставкаСервіс {
  constructor(private шлюз: ТарифШлюз, private поріг = 300) {}

  async порадитиСпосіб(напрямок: Напрямок): Promise<string> {
    const тариф = await this.шлюз.тарифДля(напрямок);   // не знає, ХТО по той бік
    return тариф.дорожчийЗа(this.поріг) ? "самовивіз" : "доставка";
  }
}
