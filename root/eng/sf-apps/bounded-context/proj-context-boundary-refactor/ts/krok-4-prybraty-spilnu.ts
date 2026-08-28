// СТАЛО: у кожного контексту свій опис своєї моделі
namespace Sales {
  export function describe(lead: Lead): string {
    return `Лід ${lead.name}: стадія ${lead.stage}, шанс ${lead.probability}`;
  }
}
namespace Billing {
  export function describe(payer: Payer): string {
    return `Платник ${payer.name}: ІПН ${payer.taxId}, ліміт ${payer.creditLimit}`;
  }
}
