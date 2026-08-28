// Один User на всю систему — і продажам, і бухгалтерії
class User {
  id: string;
  name: string;
  email: string;

  // маркер, «звідки» цей юзер — уже симптом
  source: "sales" | "billing";

  // поля продажів (для бухгалтерського юзера — null)
  stage: "new" | "qualified" | "won" | "lost" | null;
  probability: number | null;   // 0..1, шанс закрити угоду
  ownerId: string | null;        // менеджер, що веде

  // поля бухгалтерії (для продажного юзера — null)
  taxId: string | null;          // ІПН / ЄДРПОУ
  creditLimit: number | null;
  iban: string | null;

  // ...ще три десятки полів, половина завжди null

  isValid(): boolean {
    if (this.source === "sales") {
      // продажний юзер валідний, якщо має стадію й менеджера
      return this.stage !== null && this.ownerId !== null;
    } else {
      // бухгалтерський — якщо має ІПН
      return this.taxId !== null;
    }
  }
}
