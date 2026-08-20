# 📋 Специфікація схеми метаданих та протоколу рендерингу

Специфікація визначає структуру метаданих, типізовані контракти вузлів інтерфейсу, граматику безпечних логічних виразів, протокол адресації стану, дельта-патчі та мережеві контракти узгодження версій для клієнтського рантайму Metadata-Driven UI.

## 1. Конверт схеми екрана (Screen Envelope)

Кожна відповідь сервера, що передає екран, модальне вікно або секцію інтерфейсу, упаковується в уніфікований канонічний JSON-конверт. Конверт містить не лише візуальне дерево, а й початковий стан, декларативні обмеження та метадані життєвого циклу:

```json
{
  "$schema": "https://specs.architecture.internal/sdui/v2/screen.json",
  "screen_id": "checkout_payment_step",
  "schema_version": 2,
  "min_client_version": "3.4.0",
  "meta": {
    "title": "Оформлення замовлення",
    "analytics_page_name": "checkout_step_payment",
    "cache_ttl_seconds": 3600,
    "keyboard_avoidance_mode": "scroll_to_active"
  },
  "initial_state": {
    "payment_method": "card",
    "card_number": "",
    "save_card": true,
    "currency": "UAH",
    "billing_address": {
      "country": "UA",
      "city": "Київ"
    }
  },
  "root": {
    "id": "root_container",
    "type": "Stack",
    "props": {
      "direction": "vertical",
      "spacing": 16,
      "padding": 20
    },
    "children": []
  }
}
```

### Поля конверта

| Поле | Тип | Обов'язкове | Призначення |
| :--- | :--- | :--- | :--- |
| `screen_id` | `string` | Так | Унікальний стабільний ідентифікатор екрана в системі маршрутизації клієнта. |
| `schema_version` | `integer` | Так | Семантична версія структури схеми для диспетчеризації сумісності. |
| `min_client_version` | `string` | Так | Мінімальна версія бінарного клієнта (SemVer), необхідна для рендерингу екрана. |
| `meta` | `object` | Ні | Метадані екрана: заголовок навігації, аналітичні теги, політика поведінки клавіатури, TTL кешу. |
| `initial_state` | `object` | Так | Початковий словник стану форми та контекстних змінних, що завантажуються в реактивний стор. |
| `root` | `Node` | Так | Кореневий вузол дерева компонентів (деревоподібна структура AST). |

---

## 2. Базова модель вузла (Node Contract)

Кожен елемент у дереві `root` підпорядковується єдиному контракту вузла абстрактного синтаксичного дерева:

```typescript
interface Node {
  id: string;                      // Унікальний ідентифікатор вузла в межах екрана
  type: string;                    // Назва компонента для пошуку в Component Registry
  props?: Record<string, any>;     // Статичні властивості та конфігурація віджета
  bind?: {                         // Декларативне зв'язування з клієнтським станом
    value?: string;                // JSON Pointer до поля в сховищі стану (наприклад, "/user/email")
    [propName: string]: string | undefined;
  };
  visibility?: Expression;         // Логічний AST-вираз; результат false виключає вузол з рендер-дерева
  enabled?: Expression;            // Логічний AST-вираз; результат false блокує взаємодію (disabled-стан)
  validation?: ValidationRule[];   // Список декларативних правил перевірки коректності значення
  actions?: Record<string, Action>;// Обробники подій ("on_click", "on_change", "on_blur", "on_mount")
  children?: Node[];               // Вкладені дочірні вузли для контейнерних елементів
  fallback?: Node;                 // Запасний вузол для застарілих клієнтів, якщо type не зареєстровано
}
```

### Життєвий цикл рендерингу вузла
1. **Обчислення видимості (`visibility`):** якщо вираз повертає `false`, вузол не створює нативного віджета й не займає місце в геометрії екрана.
2. **Перевірка активності (`enabled`):** якщо вираз повертає `false`, нативний віджет рендериться в заблокованому режимі та ігнорує події натискання.
3. **Прив'язка даних (`bind`):** значення поля вичитується з глобального чи локального стану за вказаним JSON Pointer.
4. **Реєстрація обробників:** події користувача прив'язуються до диспетчера дій із збереженням контексту вузла.

---

## 3. Специфікація стандартних компонентів

### Контейнери розкладки (Layout Containers)

#### `Stack`
Організує дочірні елементи у лінійну послідовність по вертикалі або горизонталі з підтримкою гнучкого вирівнювання:
* `direction` (`"vertical"` | `"horizontal"`) — головна вісь розміщення віджетів.
* `spacing` (`number`) — відступ між сусідніми елементами в пікселях.
* `align_items` (`"start"` | `"center"` | `"end"` | `"stretch"`) — вирівнювання по поперечній осі.
* `justify_content` (`"start"` | `"center"` | `"end"` | `"space_between"` | `"space_around"`) — розподіл по головній осі.
* `padding` (`number` | `[top, right, bottom, left]`) — внутрішні відступи контейнера від межі.
* `scrollable` (`boolean`) — автоматичне увімкнення скролінгу, якщо контент перевищує розмір вікна.

#### `Grid`
Двовимірна сіткова розкладка для складних табличних форм або галерей:
* `columns` (`number` | `string`) — кількість рівних колонок або патерн часток (`"1fr 2fr 1fr"`).
* `row_gap` (`number`) — вертикальний відступ між рядками сітки.
* `column_gap` (`number`) — горизонтальний відступ між колонками.

#### `Card`
Структурний блок для групування логічно пов'язаних полів:
* `elevation` (`number`) — висота підняття над площиною для розрахунку тіні.
* `corner_radius` (`number`) — радіус заокруглення кутів картки.
* `background_color` (`string`) — шістнадцятковий код кольору тла (`"#ffffff"`, `"#f8fafc"`).
* `border` (`{ width: number; color: string }`) — параметри контуру.

---

### Атомні компоненти вводу (Input Components)

#### `TextInput`
* `label` (`string`) — підпис над полем вводу.
* `placeholder` (`string`) — сірий текст-підказка за відсутності значення.
* `input_type` (`"text"` | `"email"` | `"phone"` | `"number"` | `"password"`) — тип системної клавіатури.
* `mask` (`string`) — шаблон маскування введення (наприклад, `"+380 (__) ___-__-__"` або `"____-____-____-____"`).
* `max_length` (`number`) — жорстке обмеження на максимальну довжину рядка.
* `clear_button_mode` (`"never"` | `"while_editing"` | `"always"`) — відображення кнопки очищення вмісту.

#### `Select` та `RadioGroup`
* `label` (`string`) — заголовок списку вибору.
* `options` (`Array<{ value: string | number; label: string; description?: string; disabled?: boolean }>`) — доступні варіанти.
* `presentation` (`"dropdown"` | `"bottom_sheet"` | `"modal"`) — модальний спосіб показу списку на мобільному пристрої.

#### `Toggle` та `Checkbox`
* `label` (`string`) — супровідний напис біля перемикача.
* `description` (`string`) — дрібний пояснювальний текст під міткою.

#### `Button`
* `text` (`string`) — текст на кнопці.
* `variant` (`"primary"` | `"secondary"` | `"outline"` | `"destructive"`) — візуальна тема.
* `loading_text` (`string`) — напис, що замінює `text`, коли активна асинхронна мережева дія.
* `icon` (`string`) — назва системної векторної іконки з дизайн-системи.

---

## 4. Граматика безпечних виразів (Safe Expression AST)

Для динамічного обчислення видимості полів, умовного блокування кнопок та розрахунку підсумкових сум використовується строго типізоване Тюрінг-неповне дерево операцій. Виконання довільного рядкового коду заборонено на рівні синтаксичного аналізатора.

```typescript
type Expression =
  | boolean
  | number
  | string
  | { var: string }                        // Звернення до змінної стану за JSON Pointer: { "var": "/cart/total" }
  | { op: "==" | "!=" | ">" | ">=" | "<" | "<=", left: Expression, right: Expression }
  | { op: "and" | "or", args: Expression[] }
  | { op: "not", arg: Expression }
  | { op: "in", item: Expression, list: Expression[] }
  | { op: "regex", value: Expression, pattern: string }
  | { op: "+" | "-" | "*" | "/", left: Expression, right: Expression }
  | { op: "ternary", condition: Expression, true_val: Expression, false_val: Expression };
```

### Семантика обчислення операторів:
* **`var`:** вичитує значення з контексту стану форми. Якщо шлях не існує, повертає `null` без виклику винятків.
* **`==` / `!=`:** суворе порівняння значень з попереднім узгодженням числових і рядкових типів.
* **`and` / `or`:** ліниве (short-circuit) обчислення списку аргументів.
* **`regex`:** перевірка рядка на відповідність регулярному виразу з обмеженням на час виконання (захист від ReDoS-атак).
* **`ternary`:** умовний оператор «якщо-то-інакше» для динамічного вибору властивостей.

### Приклад комплексного правила:
Поле підтвердження податкового номера відображається лише якщо обрано юридичну особу ТА сума перевищує 50 000 грн:

```json
{
  "visibility": {
    "op": "and",
    "args": [
      { "op": "==", "left": { "var": "/customer/type" }, "right": "business" },
      { "op": ">=", "left": { "var": "/order/amount_cents" }, "right": 5000000 }
    ]
  }
}
```

---

## 5. Декларативні правила валідації (Validation Rules)

Кожен компонент вводу може містити масив правил, які клієнтський рушій перевіряє локально в реальному часі:

```typescript
interface ValidationRule {
  rule: "required" | "min_length" | "max_length" | "pattern" | "range" | "custom_expr" | "remote";
  params?: any;
  message: string;             // Локалізований текст помилки для відображення під полем
  when?: Expression;           // Умова, за якої правило є активним (динамічна валідація)
  debounce_ms?: number;        // Інтервал затримки для мережевої валідації (для rule: "remote")
}
```

### Специфікація типів правил:
1. **`required`:** перевіряє, що значення не є `null`, `undefined` або порожнім рядком `""`.
2. **`min_length` / `max_length`:** перевіряє кількість символів у рядку або елементів у масиві. `params: 8`.
3. **`pattern`:** валідація за регулярним виразом. `params: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"`.
4. **`range`:** перевірка числового діапазону. `params: { min: 18, max: 120 }`.
5. **`custom_expr`:** валідація через безпечний AST-вираз (правило вважається порушеним, якщо вираз повертає `false`).
6. **`remote`:** асинхронна перевірка на сервері (наприклад, перевірка унікальності логіна чи валідності промокоду). `params: { url: "/api/v1/check-promo", field_key: "code" }`.

---

## 6. Диспетчеризація дій (Action Dispatcher Contract)

Будь-яка подія користувача транслюється в декларативну інструкцію `Action`, яку виконує клієнтський Action Dispatcher:

```typescript
interface Action {
  type: "NAVIGATE" | "SET_STATE" | "HTTP_MUTATION" | "SUBMIT_FORM" | "OPEN_MODAL" | "SHOW_TOAST" | "SEQUENCE";
  payload: Record<string, any>;
  on_success?: Action;
  on_failure?: Action;
  optimistic_patch?: Record<string, any>; // Оптимістична зміна стану до завершення мережевого виклику
}
```

### Специфікація дій:
* **`SET_STATE`:** атомарний запис значення в клієнтське сховище.
  * `payload`: `{ "path": "/cart/selected_tier", "value": "premium" }`.
* **`NAVIGATE`:** маршрутизація всередині застосунку або відкриття зовнішнього URL.
  * `payload`: `{ "target": "screen", "screen_id": "profile_edit", "params": { "user_id": "${/user/id}" } }`.
* **`HTTP_MUTATION`:** фоновий мережевий виклик без зміни поточного екрана.
  * `payload`: `{ "method": "POST", "url": "/api/v2/cart/items", "body": { "item_id": 42, "quantity": 1 } }`.
* **`SUBMIT_FORM`:** валідація всіх активних вузлів форми. Якщо помилок немає — надсилає зібраний стан на вказану кінцеву точку; якщо є — фокусує перше поле з помилкою.
* **`SEQUENCE`:** послідовне виконання ланцюжка дій один за одним.

---

## 7. Дельта-оновлення дерева через JSON Patch (RFC 6902)

Для екранів із високою частотою оновлення (наприклад, кошик з динамічним перерахунком цін або живий чат підтримки) повне перезавантаження дерева призводить до надлишкового споживання трафіку та повторного створення віджетів. Рушій підтримує часткові оновлення за стандартом RFC 6902 через протокол WebSocket або Server-Sent Events (SSE):

```json
[
  { "op": "replace", "path": "/root/children/2/props/text", "value": "Разом до сплати: 1 450 грн" },
  { "op": "remove", "path": "/root/children/1" },
  { "op": "add", "path": "/root/children/3", "value": { "id": "promo_applied_badge", "type": "Text", "props": { "text": "Знижка 10% врахована" } } }
]
```

Клієнтський диференціатор застосовує операції `add`, `remove`, `replace` безпосередньо до впам'ятного AST і перераховує лише зачеплені піддерева віджетів.

---

## 8. Мережевий протокол та узгодження версій (HTTP Content Negotiation)

Для забезпечення безшовного оновлення серверних схем без зламу застарілих мобільних клієнтів використовується строгий протокол узгодження через HTTP-заголовки.

### Запит клієнта (Client Request):
Клієнт повідомляє свою версію, платформу, підтримувану версію схеми та повний перелік зареєстрованих компонентів:

```http
GET /api/v2/screens/checkout HTTP/1.1
Host: api.platform.internal
Accept: application/vnd.sdui.screen+json
X-Client-Platform: ios
X-Client-App-Version: 3.4.1
X-Client-Schema-Version: 2
X-Client-Capabilities: Stack,Grid,Card,TextInput,Select,Button,DatePicker,BiometricAuth
If-None-Match: "w/9f2a4b881c3e"
```

### Відповіді сервера (Server Responses):
* **`200 OK`:** повертає скомпільовану схему у форматі `application/vnd.sdui.screen+json`. Заголовок `ETag` фіксує хеш схеми, а `Cache-Control: public, max-age=3600` дозволяє клієнту зберегти відповідь у локальній базі даних SQLite / IndexedDB.
* **`304 Not Modified`:** якщо ETag збігся, передача тіла відсутня. Клієнт миттєво рендерить дерево з локального кешу без затримок парсингу.
* **`426 Upgrade Required`:** повертається, якщо для відображення екрана критично необхідна нова функціональність платформи, яка відсутня в клієнта (`min_client_version` більша за `X-Client-App-Version`). Відповідь містить посилання на завантаження оновлення в App Store чи Google Play.
