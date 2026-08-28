// Набір рядків — звичайні таблиці в пам'яті; рядок плаский, як у базі
type Contract = { id: number; productId: number; revenue: number; signedOn: Date };
type Recognition = { contractId: number; amount: number; recognizedOn: Date };
type DataSet = { contracts: Map<number, Contract>; recognitions: Recognition[]; products: Map<number, Product> };

class ContractModule {
  constructor(private readonly data: DataSet) {}   // стан — у наборі рядків, а не в полях модуля

  // тотожності немає: рядок називають ключем у виклику
  calculateRecognitions(contractId: number): void {
    const contract = this.data.contracts.get(contractId);   // дешевий пошук за ключем
    if (!contract) throw new Error("немає такого контракту");

    // про товар питаємо модуль товарів — і знову ключем
    const type = new ProductModule(this.data).typeOf(contract.productId);

    const add = (amount: number, on: Date) =>
      this.data.recognitions.push({ contractId, amount, recognizedOn: on });

    if (type === "spreadsheet") {                 // вибір за ЗНАЧЕННЯМ у рядку, не за типом об'єкта
      const third = round2(contract.revenue / 3);
      add(third, contract.signedOn);
      add(third, plusDays(contract.signedOn, 60));
      add(round2(contract.revenue - 2 * third), plusDays(contract.signedOn, 90));  // залишок
    } else {
      add(contract.revenue, contract.signedOn);
    }
  }

  // питання «скільки визнано на дату» — підсумок по набору, а не обхід об'єктів
  recognizedRevenue(contractId: number, asOf: Date): number {
    return this.data.recognitions
      .filter(r => r.contractId === contractId && r.recognizedOn <= asOf)
      .reduce((sum, r) => sum + r.amount, 0);
  }
}
