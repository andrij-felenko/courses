// acl/orderTranslator.ts — ЄДИНЕ місце, де мови CRM і складу зустрічаються.
import { CrmOrderDto } from "../crm/dto";
import { Order, Product, Article, Color, Size, ClientId } from "../domain/order";
import { UnsupportedByModel } from "../domain/errors";

const KNOWN_STATUS = new Set([1, 2, 3]); // статуси, що мають відповідник у нас

export function translateOrder(dto: CrmOrderDto): Order {
  // --- чуже без пари: відбій на порозі ---
  if (dto.qty < 0)
    throw new UnsupportedByModel("повернення (від'ємна кількість) з CRM");
  if (dto.qty === 0)
    throw new UnsupportedByModel("нульова кількість");
  if (!KNOWN_STATUS.has(dto.status_code))
    throw new UnsupportedByModel(`статус ${dto.status_code} без відповідника`);

  // --- переклад: народжуємо наші поняття ---
  const product = parseSku(dto.sku);
  const client  = parseClient(dto.client_ref);
  return new Order(client, product, dto.qty);
}

function parseSku(sku: string): Product {
  const parts = sku.split("/");
  if (parts.length !== 3)
    throw new UnsupportedByModel(`SKU не розкладається на 3 частини: "${sku}"`);
  const [article, color, size] = parts;
  return new Product(new Article(article), Color.parse(color), Size.parse(size));
}

function parseClient(ref: string): ClientId {
  if (!ref.startsWith("CL:"))
    throw new UnsupportedByModel(`client_ref без префікса "CL:": "${ref}"`);
  return new ClientId(ref.slice(3));
}
