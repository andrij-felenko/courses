// ДО: один клас, поле source, розвилка у валідації, півполя null
class User {
  source: "sales" | "billing";
  stage: ... | null;   taxId: ... | null;   /* +40 полів */
  isValid(): boolean {
    if (this.source === "sales") return this.stage !== null && this.ownerId !== null;
    return this.taxId !== null;
  }
}

// ПІСЛЯ: два чисті світи + перекладач на межі
namespace Sales   { export class Lead  { /* stage, probability, ownerId — усі обов'язкові */ } }
namespace Billing { export class Payer { /* taxId, creditLimit, iban — усі обов'язкові */ } }
function leadToPayer(lead: Sales.Lead, taxId: string, iban: string): Billing.Payer { /* межа */ }
// source більше немає. isValid() більше немає. null-полів немає.
