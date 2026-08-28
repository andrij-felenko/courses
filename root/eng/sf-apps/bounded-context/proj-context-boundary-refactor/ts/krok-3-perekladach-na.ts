// Перекладач ЖИВЕ НА МЕЖІ — в окремому модулі, не в Sales і не в Billing.
// Це антикорупційний шар бухгалтерії: приймає чужу модель, віддає свою.
import { Sales } from "./sales";
import { Billing } from "./billing";

export function leadToPayer(
  lead: Sales.Lead,
  taxId: string,        // ІПН прийшов НЕ з ліда — його дає сам платник
  iban: string,
): Billing.Payer {
  // беремо лише те, що справді перетинає кордон: id та ім'я.
  // stage, probability, ownerId ЛИШАЮТЬСЯ за дверима — бухгалтерії вони чужі.
  return new Billing.Payer(
    lead.id,
    lead.name,
    taxId,
    0,          // стартовий кредитний ліміт — правило БУХГАЛТЕРІЇ, не ліда
    iban,
  );
}
