# 📋 Специфікація та схема моделі загроз як коду (Threat Model as Code)

Специфікація визначає машиночитаний декларативний контракт опису моделі загроз (Threat Model as Code, TMaC) на базі форматів JSON Schema та YAML. Цей контракт призначений для переведення моделювання загроз із паперових звітів і статичних діаграм у версіонований артефакт репозиторію вихідного коду, який автоматично валідується лінтерами архітектури, генераторами DFD та шлюзами безпеки в конвеєрах неперервної інтеграції (CI/CD).

## Архітектурне призначення та принципи проектування

Традиційне моделювання загроз у вигляді багатосторінкових PDF-документів страждає на швидке старіння: щойно розробники додають новий ендпоінт, мікросервіс чи чергу повідомлень, статичний документ перестає відповідати реальній інфраструктурі. Концепція Threat Model as Code розв'язує цю проблему через збереження моделі поруч із кодом програми в єдиному репозиторії.

Специфікація базується на таких інженерних принципах:
- **Декларативність:** Архітектор описує структуру компонентів, межі довіри та потоки даних, а лінтер автоматично виводить потенційні загрози за правилами STRIDE.
- **Строга типізація:** Кожен елемент системи належить до одного з чотирьох канонічних типів DFD та має чітко визначений контекст виконання (привілеї, технологічний стек, рівень довіри).
- **Неперервний контроль у CI/CD:** Будь-який pull request, що змінює топологію мережі або додає неавтентифікований потік через межу довіри, автоматично блокує збірку проекту доти, доки для нового потоку не буде задекларовано відповідні контрзаходи.

## Повний опис структури документа

Маніфест моделі загроз є документом верхнього рівня, що містить шість ключових секцій:

1. `version` (рядок, обов'язкове): Версія специфікації схеми (наприклад, `"1.1.0"`).
2. `metadata` (об'єкт, обов'язкове): Загальна інформація про проектовану систему:
   - `system_name` (рядок): Унікальна назва системи або мікросервісного комплексу;
   - `owner` (рядок): Відповідальна інженерна команда або лід безпеки;
   - `review_date` (рядок у форматі ISO 8601 YYYY-MM-DD): Дата останнього архітектурного перегляду;
   - `confidentiality_level` (перелік: `public`, `internal`, `confidential`, `restricted`): Найвищий рівень секретності даних, які обробляються системою.
3. `trust_boundaries` (масив об'єктів): Перелік меж довіри, які розділяють компоненти системи з різними правами доступу та рівнями захищеності:
   - `id` (рядок, патерн `^tb-[a-z0-9-]+$`): Унікальний ідентифікатор межі;
   - `name` (рядок): Назва сегмента (наприклад, «Публічний інтернет» або «Внутрішній кластер»);
   - `trust_level` (ціле число від 0 до 100): Числовий градієнт довіри, де 0 — абсолютно вороже середовище (інтернет), а 100 — апаратний анклав HSM або ядро ОС;
   - `description` (рядок): Пояснення периметра та фізичного розташування.
4. `elements` (масив об'єктів): Архітектурні вузли, що беруть участь в обробці та зберіганні інформації:
   - `id` (рядок, патерн `^(ee|pr|ds)-[a-z0-9-]+$`): Префікс типу (`ee` — External Entity, `pr` — Process, `ds` — Data Store) та унікальне ім'я;
   - `name` (рядок): Зрозуміла назва сервісу чи бази;
   - `type` (перелік: `external_entity`, `process`, `data_store`): Канонічний тип вузла за класифікацією DFD;
   - `boundary_id` (рядок): Посилання на ідентифікатор межі довіри, всередині якої розташовано вузол;
   - `technology` (рядок): Технологічний стек (наприклад, `Go/gRPC`, `PostgreSQL 16`, `React`);
   - `run_as_privilege` (перелік: `root`, `user`, `sandboxed`, `external`): Рівень системних привілеїв, з якими виконується процес.
5. `flows` (масив об'єктів): Спрямовані канали зв'язку та потоки передачі даних між елементами:
   - `id` (рядок, патерн `^df-[a-z0-9-]+$`): Унікальний ідентифікатор потоку даних;
   - `name` (рядок): Опис операції (наприклад, `POST /v1/checkout` або `SQL query`);
   - `source_id` (рядок): Ідентифікатор вузла-відправника з масиву `elements`;
   - `target_id` (рядок): Ідентифікатор вузла-отримувача з масиву `elements`;
   - `protocol` (перелік: `http`, `https`, `grpc`, `mtls`, `tcp`, `ipc`, `amqp`): Мережевий або міжпроцесний протокол передачі;
   - `data_classification` (перелік: `public`, `pii`, `credentials`, `financial`, `telemetry`): Чутливість інформації, що передається потоком;
   - `crosses_boundary` (булеве значення): Прапорець, що сигналізує про перетин потоком кордону між різними межами довіри;
   - `authenticated` (булеве значення): Чи перевіряється справжність джерела на стороні отримувача;
   - `integrity_protected` (булеве значення): Чи захищено дані від модифікації криптографічним кодом або підписом.
6. `threats` (масив об'єктів): Реєстр виявлених загроз та контрзаходів:
   - `id` (рядок, патерн `^th-[a-z0-9-]+$`): Унікальний ідентифікатор загрози;
   - `stride_category` (перелік: `spoofing`, `tampering`, `repudiation`, `info_disclosure`, `dos`, `elevation_of_privilege`): Категорія загрози;
   - `target_id` (рядок): Посилання на ідентифікатор скомпрометованого елемента (`elements`) або потоку (`flows`);
   - `title` (рядок): Коротка суть небезпеки;
   - `description` (рядок): Механізм здійснення атаки;
   - `dread` (об'єкт): Числові оцінки від 1 до 10 за шкалою DREAD (`damage`, `reproducibility`, `exploitability`, `affected_users`, `discoverability`);
   - `status` (перелік: `open`, `mitigated`, `accepted`, `transferred`, `eliminated`): Поточний стан обробки загрози;
   - `mitigation` (об'єкт, обов'язковий якщо статус не `open`): Опис впровадженого архітектурного захисту, стратегія та посилання на задачу в трекері.

## Життєвий цикл обробки загроз (Threat State Machine)

Кожна загроза в реєстрі проходить строгий життєвий цикл станів:

- **`open` (Відкрита):** Загроза ідентифікована під час архітектурного аналізу, але захисні механізми ще не спроектовані або не реалізовані в коді. Якщо оцінка DREAD перевищує встановлений поріг блокування, лінтер не дозволяє випуск релізу.
- **`mitigated` (Зменшена / Захищена):** Впроваджено інженерний контрзахід (наприклад, валідація вхідних даних, шифрування каналу, контроль прав), який знижує ймовірність або наслідки атаки до прийнятного рівня. Потребує заповнення поля `control` та посилання на автоматизований тест або комміт.
- **`eliminated` (Усунена):** Архітектура системи змінена таким чином, що вразливий компонент або небезпечний функціонал повністю видалено (наприклад, відмова від збереження номерів кредитних карток на користь сторонньої токенізації).
- **`transferred` (Передана):** Відповідальність за ризик делеговано зовнішньому сертифікованому провайдеру або страховій компанії (наприклад, обробка платежів через PCI-DSS сумісний шлюз Stripe).
- **`accepted` (Прийнята):** Керівництво проекту свідомо фіксує залишковий ризик без впровадження контрзаходів, якщо вартість захисту перевищує потенційні збитки. Вимагає обов'язкового письмового обґрунтування та підпису офіцера безпеки в полі `rationale`.

## JSON Schema специфікація

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ThreatModelSpec",
  "type": "object",
  "required": ["version", "metadata", "trust_boundaries", "elements", "flows", "threats"],
  "properties": {
    "version": {
      "type": "string",
      "enum": ["1.0.0", "1.1.0"]
    },
    "metadata": {
      "type": "object",
      "required": ["system_name", "owner", "review_date"],
      "properties": {
        "system_name": { "type": "string" },
        "owner": { "type": "string" },
        "review_date": { "type": "string", "format": "date" },
        "confidentiality_level": { "type": "string", "enum": ["public", "internal", "confidential", "restricted"] }
      }
    },
    "trust_boundaries": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/TrustBoundary"
      }
    },
    "elements": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/Element"
      }
    },
    "flows": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/DataFlow"
      }
    },
    "threats": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/Threat"
      }
    }
  },
  "$defs": {
    "TrustBoundary": {
      "type": "object",
      "required": ["id", "name", "trust_level"],
      "properties": {
        "id": { "type": "string", "pattern": "^tb-[a-z0-9-]+$" },
        "name": { "type": "string" },
        "trust_level": { "type": "integer", "minimum": 0, "maximum": 100 },
        "description": { "type": "string" }
      }
    },
    "Element": {
      "type": "object",
      "required": ["id", "name", "type", "boundary_id"],
      "properties": {
        "id": { "type": "string", "pattern": "^(ee|pr|ds)-[a-z0-9-]+$" },
        "name": { "type": "string" },
        "type": { "type": "string", "enum": ["external_entity", "process", "data_store"] },
        "boundary_id": { "type": "string" },
        "technology": { "type": "string" },
        "run_as_privilege": { "type": "string", "enum": ["root", "user", "sandboxed", "external"] }
      }
    },
    "DataFlow": {
      "type": "object",
      "required": ["id", "name", "source_id", "target_id", "protocol", "crosses_boundary"],
      "properties": {
        "id": { "type": "string", "pattern": "^df-[a-z0-9-]+$" },
        "name": { "type": "string" },
        "source_id": { "type": "string" },
        "target_id": { "type": "string" },
        "protocol": { "type": "string", "enum": ["http", "https", "grpc", "mtls", "tcp", "ipc", "amqp"] },
        "data_classification": { "type": "string", "enum": ["public", "pii", "credentials", "financial", "telemetry"] },
        "crosses_boundary": { "type": "boolean" },
        "authenticated": { "type": "boolean" },
        "integrity_protected": { "type": "boolean" }
      }
    },
    "Threat": {
      "type": "object",
      "required": ["id", "stride_category", "target_id", "title", "dread", "status"],
      "properties": {
        "id": { "type": "string", "pattern": "^th-[a-z0-9-]+$" },
        "stride_category": { "type": "string", "enum": ["spoofing", "tampering", "repudiation", "info_disclosure", "dos", "elevation_of_privilege"] },
        "target_id": { "type": "string" },
        "title": { "type": "string" },
        "description": { "type": "string" },
        "dread": {
          "type": "object",
          "required": ["damage", "reproducibility", "exploitability", "affected_users", "discoverability"],
          "properties": {
            "damage": { "type": "number", "minimum": 1, "maximum": 10 },
            "reproducibility": { "type": "number", "minimum": 1, "maximum": 10 },
            "exploitability": { "type": "number", "minimum": 1, "maximum": 10 },
            "affected_users": { "type": "number", "minimum": 1, "maximum": 10 },
            "discoverability": { "type": "number", "minimum": 1, "maximum": 10 }
          }
        },
        "status": { "type": "string", "enum": ["open", "mitigated", "accepted", "transferred", "eliminated"] },
        "mitigation": {
          "type": "object",
          "properties": {
            "strategy": { "type": "string", "enum": ["mitigate", "eliminate", "transfer", "accept"] },
            "control": { "type": "string" },
            "ticket_ref": { "type": "string" }
          }
        }
      }
    }
  }
}
```

## Приклад декларативної моделі (YAML)

```yaml
version: "1.1.0"
metadata:
  system_name: "PaymentCheckoutService"
  owner: "Payments Core Team"
  review_date: "2026-08-20"
  confidentiality_level: "restricted"

trust_boundaries:
  - id: "tb-internet"
    name: "Публічна мережа Інтернет"
    trust_level: 0
    description: "Неконтрольоване середовище, зловмисники мають прямий доступ"

  - id: "tb-dmz"
    name: "Периметр сервісу (DMZ / API Gateway)"
    trust_level: 50
    description: "Зона вхідних термінованих TLS-з'єднань"

  - id: "tb-backend"
    name: "Внутрішній захищений контур (Kubernetes Service Mesh)"
    trust_level: 90
    description: "Ізольована віртуальна мережа, доступ за взаємною mTLS-автентифікацією"

elements:
  - id: "ee-browser"
    name: "Клієнтський веб-браузер"
    type: "external_entity"
    boundary_id: "tb-internet"
    run_as_privilege: "external"

  - id: "pr-gateway"
    name: "Kong API Gateway"
    type: "process"
    boundary_id: "tb-dmz"
    technology: "OpenResty / Lua"
    run_as_privilege: "sandboxed"

  - id: "pr-checkout"
    name: "Checkout Processing Service"
    type: "process"
    boundary_id: "tb-backend"
    technology: "Go / gRPC"
    run_as_privilege: "user"

  - id: "ds-postgres"
    name: "PostgreSQL Orders Database"
    type: "data_store"
    boundary_id: "tb-backend"
    technology: "PostgreSQL 16"
    run_as_privilege: "user"

flows:
  - id: "df-checkout-req"
    name: "POST /v1/checkout"
    source_id: "ee-browser"
    target_id: "pr-gateway"
    protocol: "https"
    data_classification: "financial"
    crosses_boundary: true
    authenticated: true
    integrity_protected: true

  - id: "df-grpc-process"
    name: "gRPC: ProcessPayment"
    source_id: "pr-gateway"
    target_id: "pr-checkout"
    protocol: "mtls"
    data_classification: "financial"
    crosses_boundary: true
    authenticated: true
    integrity_protected: true

  - id: "df-db-save"
    name: "SQL: INSERT INTO orders"
    source_id: "pr-checkout"
    target_id: "ds-postgres"
    protocol: "mtls"
    data_classification: "financial"
    crosses_boundary: false
    authenticated: true
    integrity_protected: true

threats:
  - id: "th-gateway-tampering"
    stride_category: "tampering"
    target_id: "df-checkout-req"
    title: "Підміна суми транзакції клієнтом під час оплати"
    description: "Користувач надсилає змінений JSON із модифікованим полем amount."
    dread:
      damage: 9.0
      reproducibility: 9.0
      exploitability: 8.0
      affected_users: 10.0
      discoverability: 8.0
    status: "mitigated"
    mitigation:
      strategy: "mitigate"
      control: "Серверний перерахунок цін на стороні Checkout Service, ціна з клієнта ігнорується."
      ticket_ref: "SEC-1042"

  - id: "th-db-sqli"
    stride_category: "elevation_of_privilege"
    target_id: "ds-postgres"
    title: "SQL-ін'єкція через несанітизований коментар до замовлення"
    description: "Виконання довільних SQL-команд через конкатенацію рядків у запиті."
    dread:
      damage: 10.0
      reproducibility: 8.0
      exploitability: 6.0
      affected_users: 10.0
      discoverability: 5.0
    status: "mitigated"
    mitigation:
      strategy: "mitigate"
      control: "Використання виключно параметризованих prepared statements у Go pgx драйвері."
      ticket_ref: "SEC-1043"
```

## Інваріанти валідатора моделі загроз та коди помилок

Автоматизований інструмент статичного аналізу моделі (Threat Linter) запускається на кожному етапі створення pull request та проводить перевірку графа топології на дотримання наступних інваріантів:

| Код інваріанта | Перевірка валідатора | Очікувана поведінка та наслідки порушення |
| :--- | :--- | :--- |
| `ERR_CROSS_BOUNDARY_NO_AUTH` | `flow.crosses_boundary == true` | Якщо потік перетинає межу довіри, але `flow.authenticated == false`, валідатор генерує фатальну помилку: будь-який вхід з менш довіреної зони зобов'язаний проходити криптографічну автентифікацію. |
| `ERR_CROSS_BOUNDARY_NO_TLS` | `flow.crosses_boundary == true` | Протокол передачі даних повинен належати до шифрованого набору (`https`, `grpc`, `mtls`). Використання незахищеного `http` чи `tcp` між різними межами блокує збірку. |
| `ERR_UNMITIGATED_HIGH_THREAT` | `threat.dread_score ≥ 7.0` | Якщо загроза з рейтингом ризику 7.0 і вище має статус `open`, лінтер завершує роботу з кодом помилки `2` (блокер випуску релізу). |
| `ERR_DANGLING_ELEMENT_REF` | `flow.source_id` / `flow.target_id` | Усі посилання на ідентифікатори вузлів у потоках і загрозах повинні строго відповідати наявним записам у секції `elements`. Наявність битих посилань свідчить про розсинхронізацію моделі. |
| `ERR_STRIDE_ELEMENT_MISMATCH` | `threat.stride_category` | Призначена категорія загрози повинна строго відповідати матриці STRIDE для типу цільового елемента. Наприклад, загроза `elevation_of_privilege` не може бути прив'язана до пасивного потоку даних `data_flow`. |
| `ERR_TRUST_GRADIENT_INVERSION` | `source.trust_level > target.trust_level` | Якщо дані з високим рівнем довіри передаються у низький без позначки санітизації або шифрування, генерується попередження про можливий витік даних (Information Disclosure). |

## Специфікація інтерфейсу командного рядка (CLI)

Інструмент валідації `threat-lint` інтегрується в інфраструктуру CI/CD за єдиним інтерфейсом виклику:

```text
Ужиток:
  threat-lint validate --model <шлях-до-файлу.yaml> [опції]

Опції:
  --model <path>         Шлях до файлу маніфесту моделі загроз у форматі YAML або JSON (обов'язковий).
  --schema <path>        Шлях до альтернативної схеми JSON Schema для кастомних розширень.
  --threshold <score>    Поріг критичності DREAD для блокування збірки (за замовчуванням: 7.0).
  --fail-on-open         Завершувати з ненульовим кодом помилки, якщо присутня хоча б одна загроза зі статусом open.
  --format <type>        Формат виводу звіту: console (текст), json (машиночитаний JSON), junit (для тест-раннерів).
  --strict               Увімкнути режим суворої валідації градієнта меж довіри.

Коди завершення процесу:
  0 — Модель валідна, всі інваріанти виконано, критичних відкритих загроз немає.
  1 — Синтаксична помилка парсингу або невідповідність базовій JSON Schema (відсутні обов'язкові поля, некоректні типи).
  2 — Порушення інваріантів безпеки архітектури (неавтентифікований перетин меж, відкриті загрози вище встановленого порогу).
  3 — Помилка доступу до файлової системи або некоректні прапорці запуску CLI.
```
