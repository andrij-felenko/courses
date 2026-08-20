# 📋 Специфікація інтерфейсу обчислення прапорців OpenFeature

**OpenFeature** — це відкритий вендор-нейтральний інженерний стандарт під егідою Cloud Native Computing Foundation (CNCF), що визначає єдиний уніфікований інтерфейс для динамічного обчислення прапорців функцій у коді застосунків.

Стандарт розв'язує фундаментальну проблему жорсткого зв'язування з інструментом (*vendor lock-in*): бізнес-код взаємодіє виключно з абстрактним клієнтським API, тоді як конкретні інструменти керування прапорцями (LaunchDarkly, Unleash, Flagsmith, локальні JSON-файли чи внутрішні розподілені рушії) підключаються на рівні провайдера (*Feature Provider*).

## 1. Архітектурні рівні та розділення обов'язків

Специфікація стандарту будується на чотирьох чітко розмежованих шарах взаємодії, кожен із яких відповідає за ізольовану зону відповідальності:

1. **Шар застосунку (Application Layer):** містить бізнес-логіку програми. Інженер викликає високорівневі суворо типізовані методи (`getBooleanValue`, `getStringDetails`), передаючи ключ прапорця, значення за замовчуванням та контекст виконання. Застосунок не знає, де і як зберігаються правила.
2. **Шар клієнта (Client Layer):** абстракція OpenFeature Client, яка керує злиттям контекстів, запускає послідовність зареєстрованих хуків (Hooks) і делегує безпосереднє обчислення активному провайдеру. Клієнт може бути прив'язаний до окремого домену чи модуля системи (наприклад, окремий клієнт для платежів і окремий для рекомендацій).
3. **Шар провайдера (Provider Layer):** драйвер-адаптер конкретної системи прапорців, що реалізує безпосередню логіку зіставлення правил у пам'яті або взаємодію з локальним кешем. Провайдер транслює абстрактні виклики OpenFeature у специфічні структури даних свого бекенду.
4. **Конвеєр хуків (Evaluation Hooks Pipeline):** проміжне програмне забезпечення (*middleware*) для перехоплення етапів обчислення з метою збору метрик, аудиту, розподіленого трейсингу та логування.

## 2. Модель контексту обчислення (EvaluationContext)

`EvaluationContext` — це структурований контейнер контекстної інформації, на основі якої провайдер приймає рішення щодо правил таргетингу, сегментації користувачів та детермінованого хеш-бакетування.

### Структура та поля контексту
Контекст складається з обов'язкового ідентифікатора сутності та довільного набору типізованих атрибутів:

| Поле | Тип | Обов'язковість | Опис та семантичне призначення |
|---|---|---|---|
| `targetingKey` | `string` | Рекомендовано | Унікальний ідентифікатор суб'єкта таргетингу (User ID, Account ID, Session ID, Device ID), що використовується для детермінованого хешування та консистентного розподілу когорт. |
| `attributes` | `Map<string, Value>` | Опціонально | Словник довільних пар ключ-значення, де значенням може бути рядок, число, булевий прапорець, список або вкладена структура даних. |

### Стандартні зарезервовані атрибути
Для забезпечення сумісності між різними провайдерами та аналітичними платформами специфікація OpenFeature закріплює загальноприйняті семантичні ключі:
* `targetingKey` — головний ключ суб'єкта (користувач або сутність);
* `ip` — IP-адреса клієнта (використовується правилами геолокації та обмеження швидкості);
* `email` — адреса електронної пошти користувача (для таргетингу корпоративних доменів, наприклад `@company.com`);
* `country` — дволітерний код країни ISO 3166-1 alpha-2 (наприклад, `UA`, `PL`, `US`);
* `appVersion` — версія клієнтського або мобільного застосунку у форматі SemVer (для порівняння версій `appVersion >= "3.2.0"`);
* `connectionType` — тип підключення (`wifi`, `cellular_5g`, `ethernet`).

### Правила ієрархічного злиття контекстів (Context Merging)
Контекст обчислення формується на трьох ієрархічних рівнях:
1. **Глобальний контекст (API Level):** статичні атрибути всього вузла застосунку (`environment="production"`, `region="eu-central-1"`, `datacenter="dc-01"`);
2. **Контекст клієнта (Client Level):** атрибути конкретної підсистеми або сервісу (`component="billing-service"`, `tier="enterprise"`);
3. **Контекст виклику (Invocation Level):** динамічні атрибути поточного запиту чи операції (`userId="usr_8492"`, `cartTotal=450.0`, `role="admin"`).

При виникненні конфліктів однакових ключів атрибутів діє строге правило пріоритету: **рівень виклику перекриває рівень клієнта, а рівень клієнта перекриває глобальний рівень** (`Invocation > Client > Global`).

## 3. Модель результату обчислення (EvaluationDetails)

Методи детального обчислення повертають структуру `EvaluationDetails<T>`, що містить не лише обчислене значення прапорця, але й повні діагностичні метадані про те, яким шляхом конвеєра це значення було сформовано.

### Поля структури EvaluationDetails
```typescript
interface EvaluationDetails<T> {
  flagKey: string;              // Унікальний ключ прапорця
  value: T;                     // Обчислене значення (або defaultValue у разі збою)
  variant?: string;             // Назва варіанта (наприклад, "control", "treatment_a", "v2")
  reason?: ResolutionReason;    // Формальна причина ухвалення рішення
  errorCode?: ErrorCode;        // Код помилки (якщо reason == "ERROR")
  errorMessage?: string;        // Текстовий людинозрозумілий опис помилки
  flagMetadata?: FlagMetadata;  // Додаткові статичні метадані прапорця
}
```

### Стандартні причини резолюції (ResolutionReason)

| Код причини | Опис семантики |
|---|---|
| `STATIC` | Значення жорстко зафіксоване в статичній конфігурації провайдера (наприклад, у локальному файлі конфігурації). |
| `DEFAULT` | Жодне правило таргетингу не спрацювало або прапорець вимкнений; повернуто безпечне значення за замовчуванням `defaultValue`. |
| `TARGETING_MATCH` | Спрацювало правило таргетингу за атрибутами (країна, роль, email або вкладені умови). |
| `SPLIT` | Користувач потрапив у динамічний відсоток розкатки або A/B-варіант за детермінованим хеш-бакетом. |
| `CACHED` | Значення взято з локального кешу пам'яті без звернення до сховища. |
| `DISABLED` | Прапорець явно переведено в стан Disabled у системі керування. |
| `UNKNOWN` | Провайдер не зміг визначити точну причину ухвалення рішення. |
| `ERROR` | Під час обчислення сталася помилка (деталі див. у полі `errorCode`). |

### Стандартні коди помилок (ErrorCode)

| Код помилки | Опис причини збою та гарантії відкату |
|---|---|
| `PROVIDER_NOT_READY` | Провайдер ще не завершив асинхронну ініціалізацію або завантаження початкових правил; повертається `defaultValue`. |
| `FLAG_NOT_FOUND` | Прапорець із вказаним ключем відсутній у наборі конфігурації; повертається `defaultValue`. |
| `PARSE_ERROR` | Виникла помилка парсингу правил або невалідний формат JSON; повертається `defaultValue`. |
| `TYPE_MISMATCH` | Очікуваний тип (наприклад, `boolean`) не збігається з типом значення в системі (наприклад, повернуто `string`); повертається `defaultValue`. |
| `TARGETING_KEY_MISSING` | Правила вимагають наявності `targetingKey` для розрахунку бакета, але його не було передано в контексті; повертається `defaultValue`. |
| `INVALID_CONTEXT` | Контекст містить невалідні, пошкоджені або циклічні структури атрибутів; повертається `defaultValue`. |
| `GENERAL` | Непередбачена внутрішня помилка підсистеми провайдера; повертається `defaultValue`. |

## 4. Контракт клієнтського інтерфейсу (Client API)

Клієнт надає суворо типізовані методи для чотирьох фундаментальних типів даних: `Boolean`, `String`, `Number` (ціле/дробове) та `Object` (довільна ієрархічна структура даних).

Кожен тип представлений у двох функціональних формах:
1. **Швидке обчислення значення (`get...Value`):** оптимізовано для гарячого шляху, повертає безпосередньо типізоване значення `T`.
2. **Детальне обчислення (`get...Details`):** повертає повну структуру `EvaluationDetails<T>` для аудиту, аналітики чи логування рішень.

### Сигнатури методів клієнта

```typescript
interface Client {
  // Булеві прапорці (увімкнено / вимкнено)
  getBooleanValue(flagKey: string, defaultValue: boolean, context?: EvaluationContext): Promise<boolean>;
  getBooleanDetails(flagKey: string, defaultValue: boolean, context?: EvaluationContext): Promise<EvaluationDetails<boolean>>;

  // Рядкові прапорці (вибір варіанта, ключа API або текстового повідомлення)
  getStringValue(flagKey: string, defaultValue: string, context?: EvaluationContext): Promise<string>;
  getStringDetails(flagKey: string, defaultValue: string, context?: EvaluationContext): Promise<EvaluationDetails<string>>;

  // Числові прапорці (таймаути, ліміти черг, порогові значення)
  getNumberValue(flagKey: string, defaultValue: number, context?: EvaluationContext): Promise<number>;
  getNumberDetails(flagKey: string, defaultValue: number, context?: EvaluationContext): Promise<EvaluationDetails<number>>;

  // Структуровані об'єктні прапорці (конфігураційні JSON-схеми, словники)
  getObjectValue<T extends object>(flagKey: string, defaultValue: T, context?: EvaluationContext): Promise<T>;
  getObjectDetails<T extends object>(flagKey: string, defaultValue: T, context?: EvaluationContext): Promise<EvaluationDetails<T>>;

  // Управління хуками на рівні екземпляра клієнта
  addHooks(...hooks: Hook[]): void;
}
```

## 5. Контракт провайдера (Feature Provider API)

Розробник власного рушія або інтегратор зовнішньої платформи прапорців зобов'язаний реалізувати інтерфейс `FeatureProvider`.

### Життєвий цикл та методи резолюції

```typescript
interface FeatureProvider {
  readonly metadata: { name: string };
  readonly hooks?: Hook[];

  // Події життєвого циклу провайдера
  initialize?(context?: EvaluationContext): Promise<void>;
  shutdown?(): Promise<void>;
  onContextChange?(oldContext: EvaluationContext, newContext: EvaluationContext): Promise<void>;

  // Обов'язкові внутрішні методи резолюції типів
  resolveBooleanEvaluation(flagKey: string, defaultValue: boolean, context: EvaluationContext): Promise<ResolutionDetails<boolean>>;
  resolveStringEvaluation(flagKey: string, defaultValue: string, context: EvaluationContext): Promise<ResolutionDetails<string>>;
  resolveNumberEvaluation(flagKey: string, defaultValue: number, context: EvaluationContext): Promise<ResolutionDetails<number>>;
  resolveObjectEvaluation<T extends object>(flagKey: string, defaultValue: T, context: EvaluationContext): Promise<ResolutionDetails<T>>;
}
```

### Події стану провайдера (Provider Events)
Провайдер емітує стандартні події життєвого циклу через механізм підписки, інформуючи клієнтів про зміни в інфраструктурі:
* `PROVIDER_READY` — провайдер успішно підключився до сховища правил, ініціалізував внутрішній кеш і готовий обробляти виклики;
* `PROVIDER_CONFIGURATION_CHANGED` — конфігурація правил оновилася на льоту (додано нові прапорці, змінено відсоток розкатки без перезапуску застосунку);
* `PROVIDER_ERROR` — виник критичний збій мережевого з'єднання або пошкодження правил;
* `PROVIDER_STALE` — дані в локальному кеші застаріли через тривалу втрату зв'язку з площиною керування.

## 6. Конвеєр хуків (Evaluation Hooks Pipeline)

Хуки дозволяють вбудовувати наскрізну логіку (аудит, трасування, моніторинг помилок, метрики в Prometheus або OpenTelemetry) на кожному етапі життєвого циклу перевірки прапорця.

### Послідовність виконання хуків
Під час кожного звернення до клієнта конвеєр виконує чотири стадії в строго фіксованому порядку:

```
[ Старт обчислення ]
        │
        ▼
   1. before() ──────────► [ Валідація / збагачення EvaluationContext ]
        │
        ▼
[ Резолюція у провайдері ]
   ├── Успіх ────────────► 2. after()   ──► [ Запис метрик успішного обчислення ]
   └── Помилка ──────────► 3. error()   ──► [ Фіксація збою в логах / Sentry ]
        │
        ▼
   4. finally() ─────────► [ Закриття трейс-спанів / очищення ресурсів ]
```

### Сигнатура інтерфейсу Hook
```typescript
interface Hook {
  // Виконується ДО резолюції: може додати контекстні атрибути
  before?(hookContext: HookContext, hints?: HookHints): Promise<EvaluationContext | void>;

  // Виконується після успішної резолюції
  after?(hookContext: HookContext, details: EvaluationDetails<any>, hints?: HookHints): Promise<void>;

  // Виконується у разі виникнення помилки або викидання винятку
  error?(hookContext: HookContext, error: Error, hints?: HookHints): Promise<void>;

  // Виконується завжди (як блок finally)
  finally?(hookContext: HookContext, hints?: HookHints): Promise<void>;
}
```

## 7. Семантичні конвенції OpenTelemetry для прапорців функцій

Специфікація OpenFeature стандартизована з **OpenTelemetry Semantic Conventions for Feature Flags**. Кожне обчислення прапорця збагачує активний розподілений спан (Trace Span) такими обов'язковими атрибутами:

* `feature_flag.key` — ім'я прапорця (наприклад, `"payment-gateway-v2"`);
* `feature_flag.provider_name` — ім'я активного провайдера (наприклад, `"in-memory-engine"`);
* `feature_flag.variant` — назва обраного варіанта (наприклад, `"treatment_stripe"`);
* `feature_flag.context.id` — значення `targetingKey` із контексту.

Це дозволяє в системах моніторингу (Jaeger, Grafana Tempo) фільтрувати трейси за значенням прапорця і миттєво бачити, чи не спричинила нова версія фічі зростання кількості помилок HTTP 500 у суміжних мікросервісах.

## 8. Метадані прапорця та підтримка статичних схем (FlagMetadata)

Стандарт дозволяє прикріплювати до кожного прапорця статичні декларативні метадані `FlagMetadata`, які провайдер повертає разом із результатом резолюції:

* `description` — стислий інженерний опис функціональності;
* `owner` — команда чи інженер, відповідальний за підтримку та видалення прапорця (наприклад, `"team-checkout"`);
* `expirationDate` — запланована дата виходу з експлуатації та очищення коду у форматі ISO 8601;
* `ticket` — посилання на задачу в трекері завдань (наприклад, `"PROJ-1842"`).

Наявність метаданих дозволяє лінтерам та автоматизованим CI/CD-пайплайнам сканувати кодову базу і надсилати сповіщення в командні чати про прострочені релізні прапорці до того, як вони перетворяться на некерований технічний борг.

## 9. Повний приклад інтеграції та використання

Нижче наведено практичний приклад ініціалізації стандарту OpenFeature, реєстрації власного провайдера та хука метрик і виконання безпечного обчислення в бізнес-сервісі:

```typescript
import { OpenFeature, Hook, HookContext, EvaluationDetails } from "@openfeature/server-sdk";
import { MyInMemoryProvider } from "./my-in-memory-provider";

// 1. Створюємо хук для логування A/B-експозицій
class ExposureLoggingHook implements Hook {
  after(hookContext: HookContext, details: EvaluationDetails<any>) {
    if (details.reason === "SPLIT") {
      console.log(`[Telemetry] User "${hookContext.context.targetingKey}" assigned to variant "${details.variant}" for flag "${details.flagKey}"`);
    }
  }
}

// 2. Реєструємо глобального провайдера та хуки на рівні платформи
await OpenFeature.setProviderAndWait(new MyInMemoryProvider());
OpenFeature.addHooks(new ExposureLoggingHook());

// 3. Отримуємо типізованого клієнта для платіжного сервісу
const client = OpenFeature.getClient("billing-service");

// 4. Обчислюємо прапорець під час обробки транзакції
async function processCheckout(userId: string, country: string, amount: number) {
  const context = {
    targetingKey: userId,
    country: country,
    cartAmount: amount
  };

  // Виклик ніколи не кидає винятків: при збої повертається false
  const useStripeV2 = await client.getBooleanValue("payment-gateway-v2", false, context);

  if (useStripeV2) {
    return executeStripeV2Checkout(amount);
  } else {
    return executeLegacyCheckout(amount);
  }
}
```

Стандартизований інтерфейс OpenFeature гарантує повну незалежність бізнес-логіки від особливостей інфраструктури розповсюдження прапорців, забезпечуючи переносимість, чистоту архітектури та високу надійність кодової бази.
