// Порт: що домен ВИМАГАЄ від зовнішнього світу. Мова складу, жодного CRM.
interface OrderSource {
  next(): Order | null;   // дай наступне замовлення як НАШ об'єкт
}

// ACL: єдине місце, де живе знання про чужий формат
class CrmOrderAcl implements OrderSource {
  constructor(private crm: CrmClient) {}

  next(): Order | null {
    const dto = this.crm.fetchNext();
    if (dto === null) return null;
    return this.translate(dto);            // переклад чужого на наше — тут і лише тут
  }

  private translate(dto: CrmOrderDto): Order {
    if (dto.qty < 0)
      throw new UnsupportedByModel("повернень наш склад не приймає з CRM");
    if (![1, 2, 3].includes(dto.status_code))
      throw new UnsupportedByModel(`статус ${dto.status_code} не має відповідника`);

    const product = this.parseSku(dto.sku);      // "ART-00417/RED/XL" → Product
    const client  = new ClientId(dto.client_ref.replace(/^CL:/, ""));
    return new Order(client, product, dto.qty);  // чистий об'єкт нашої моделі
  }

  private parseSku(sku: string): Product {
    const [article, color, size] = sku.split("/");
    return new Product(new Article(article), Color.parse(color), Size.parse(size));
  }
}
