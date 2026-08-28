// Домен більше НЕ знає про CRM. Говорить лише своєю мовою через порт.
class OrderService {
  constructor(private source: OrderSource) {}   // залежить від СВОГО інтерфейсу

  processBatch(): void {
    let order: Order | null;
    while ((order = this.source.next()) !== null) {
      order.reserve();       // чисте доменне правило, жодного split чи числа 7
    }
  }
}
