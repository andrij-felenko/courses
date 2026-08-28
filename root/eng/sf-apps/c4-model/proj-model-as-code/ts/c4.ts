// c4.ts — модель як дані. Тут немає рендерингу: лише вузли й ребра графа.

type Kind = "person" | "system" | "container" | "component";
type Level = "context" | "container";

interface Element {
  id: string;            // СТАБІЛЬНИЙ ключ — на нього посилається все інше
  kind: Kind;
  name: string;          // показове ім'я; його можна міняти будь-коли
  parent?: string;       // власник: контейнер → система, компонент → контейнер
  technology?: string;   // "React", "PostgreSQL" — лише де є сенс
  external?: boolean;    // поза межею нашої системи
}

interface Relation {
  from: string;          // id елемента-джерела
  to: string;            // id елемента-цілі
  label: string;         // "надсилає запити"
  technology?: string;   // "HTTPS/JSON"
}

interface Model {
  root: string;          // id нашої системи — scope за замовчуванням
  elements: Element[];
  relations: Relation[];
}

// --- та сама система, що на діаграмах теми, як звичайні дані ---
const shop: Model = {
  root: "shop",
  elements: [
    { id: "customer", kind: "person", name: "Покупець", external: true },
    { id: "shop",     kind: "system", name: "Інтернет-магазин" },
    { id: "payments", kind: "system", name: "Платіжний шлюз", external: true },
    { id: "email",    kind: "system", name: "Пошта", external: true },

    { id: "web",   kind: "container", name: "Веб-застосунок", parent: "shop", technology: "React" },
    { id: "api",   kind: "container", name: "API-сервіс",     parent: "shop", technology: "Java/Spring" },
    { id: "db",    kind: "container", name: "База даних",      parent: "shop", technology: "PostgreSQL" },
    { id: "queue", kind: "container", name: "Черга задач",     parent: "shop", technology: "RabbitMQ" },
  ],
  relations: [
    { from: "customer", to: "web",      label: "переглядає й купує", technology: "HTTPS" },
    { from: "web",      to: "api",      label: "надсилає запити",    technology: "HTTPS/JSON" },
    { from: "api",      to: "db",       label: "читає й пише",       technology: "SQL" },
    { from: "api",      to: "queue",    label: "кладе задачі",       technology: "AMQP" },
    { from: "api",      to: "payments", label: "проводить оплату",   technology: "API" },
    { from: "queue",    to: "email",    label: "шле листи",          technology: "SMTP" },
  ],
};
