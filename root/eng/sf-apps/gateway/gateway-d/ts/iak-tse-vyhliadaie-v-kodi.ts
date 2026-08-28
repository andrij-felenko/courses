// РЕАЛІЗАЦІЯ шлюзу: єдине місце, де програма знає мову чужого сервісу.
class HttpТарифШлюз implements ТарифШлюз {
  constructor(private базовийUrl: string, private токен: string) {}

  async тарифДля(напрямок: Напрямок): Promise<Тариф> {
    // 1. переклад НАШОЇ мови → у мову чужого API
    const url = `${this.базовийUrl}/rate?seg=${напрямок.код}&v=3`;
    const відповідь = await fetch(url, {
      headers: { Authorization: `Bearer ${this.токен}` },
    });

    // 2. чужі коди помилок → НАШІ доменні помилки
    if (відповідь.status === 406) throw new ТарифНедоступний(напрямок);
    if (відповідь.status === 419) throw new ДоступПрострочено();
    if (!відповідь.ok) throw new ШлюзНедоступний(відповідь.status);

    // 3. чужа форма даних → НАШ доменний об'єкт (rate_bps — їхня назва, не наша)
    const дані = await відповідь.json();
    return new Тариф(дані.rate_bps / 100);   // переклад завершено — далі рідне
  }
}
