// Опис одного маршруту. Це і є той конфіг, який змінюють при переїзді.
// Жодного рішення не зашито в код — усе тут, і все оборотне правкою полів.
type Target = "legacy" | "service";

interface RouteRule {
  pattern: RegExp;    // які шляхи стосуються цієї можливості
  target: Target;     // куди слати основний потік: старе чи нове
  percent: number;    // 0..100 — яку частку пускати в нове (canary)
  shadow: boolean;    // тіньово звіряти нове зі старим, не показуючи клієнту
  serviceUrl: string; // база нового сервісу
}

// Детермінований хеш ключа в діапазон 0..99. Той самий ключ — той самий
// бакет ЗАВЖДИ, тож клієнт не стрибає між старим і новим від запиту до запиту.
function bucketOf(key: string): number {
  // FNV-1a — простий, швидкий, добре розсіює; криптостійкість тут не потрібна.
  let h = 0x811c9dc5;
  for (let i = 0; i < key.length; i++) {
    h ^= key.charCodeAt(i);
    h = Math.imul(h, 0x01000193);   // множення за модулем 2³² з переносом
  }
  return (h >>> 0) % 100;           // >>> 0 робить число беззнаковим
}

// Чи веде цей запит у НОВИЙ сервіс? Рішення = напрям × відсоток × стабільний бакет.
function goesToService(rule: RouteRule, userKey: string): boolean {
  if (rule.target !== "service") return false;      // напрям ще на старе
  if (rule.percent >= 100) return true;             // усі
  if (rule.percent <= 0) return false;              // ніхто
  return bucketOf(userKey) < rule.percent;          // стабільна частка
}
