# 📋 Специфікація метамоделі C4 та граматика Structurizr DSL

Цей документ є повним технічним довідником сутностей метамоделі C4 та граматики декларативної мови **Structurizr DSL** (англ. *Domain Specific Language*). Він призначений для інженерів та архітекторів, які впроваджують підхід «Архітектура як код» (Architecture as Code) і потребують вичерпного опису доступних синтаксичних конструкцій, правил успадкування властивостей, резолюції ідентифікаторів та інваріантів валідації.

---

## 1. Концептуальна архітектура метамоделі C4

Метамодель C4 визначає суворо типізовану ієрархію елементів програмної системи. На відміну від неформальних графічних схем, у моделі C4 кожен об'єкт належить до чітко визначеного типу з фіксованими правилами вкладеності.

```
Workspace (Робочий простір)
│
├── Configuration (Налаштування ідентифікаторів та користувачів)
│
├── Model (Єдина модель сутностей та зв'язків)
│   ├── Person (Людина / Роль)
│   ├── SoftwareSystem (Програмна система)
│   │   └── Container (Контейнер: процес, сховище, клієнт)
│   │       └── Component (Компонент: внутрішній модуль)
│   ├── DeploymentEnvironment (Середовище розгортання: Prod, Staging)
│   │   └── DeploymentNode (Вузол інфраструктури: сервер, VM, Pod)
│   │       ├── InfrastructureNode (Мережевий або системний вузол)
│   │       └── ContainerInstance (Екземпляр логічного контейнера)
│   └── Relationship (Спрямований зв'язок між будь-якими двома сутностями)
│
└── Views (Проєкції, фільтри та стилі)
    ├── SystemLandscapeView (Макро-ландшафт організації)
    ├── SystemContextView (Контекст окремої системи — Рівень 1)
    ├── ContainerView (Контейнери системи — Рівень 2)
    ├── ComponentView (Компоненти обраного контейнера — Рівень 3)
    ├── DynamicView (Поведінковий сценарій у часі)
    ├── DeploymentView (Топологія розгортання)
    └── Styles (Правила візуалізації, кольори, форми та товщина ліній)
```

Головний принцип метамоделі полягає в тому, що всі сутності та їхні взаємодії оголошуються **рівно один раз у блоці `model`**. Блок `views` не створює нових програмних об'єктів чи зв'язків: він лише створює візуальні вибірки (фільтровані проєкції) з уже наявної моделі даних.

---

## 2. Базові елементи моделі та їхні властивості

Кожен елемент у моделі описується фіксованим набором атрибутів, які гарантують однозначність інтерпретації.

### 2.1. Людина (Person)
Позначає користувача системи, оператора, адміністратора або зовнішнього клієнта.
- **Синтаксис:** `person <identifier> [name] [description] [tags]`
- **Властивості:**
  - `identifier` — унікальний внутрішній ідентифікатор змінної в межах DSL.
  - `name` — відображуване ім'я сутності на діаграмі (наприклад, `Покупець`).
  - `description` — стислий опис ролі та обов'язків користувача.
  - `tags` — список тегів через кому для подальшої стилізації та фільтрації.

### 2.2. Програмна система (Software System)
Найвищий рівень програмної декомпозиції. Це система, яка створює бізнес-цінність для людей або інших систем (як власна, так і зовнішня стороння система).
- **Синтаксис:** `softwareSystem <identifier> [name] [description] [tags] { ... }`
- **Особливості:**
  - Якщо система є зовнішньою (сторонній банк, поштовий сервіс), вона оголошується без вкладеного тіла й маркується тегом `External`.
  - Якщо система розробляється вашою командою, всередині її фігурних дужок оголошуються дочірні контейнери.

### 2.3. Контейнер (Container)
Будь-яка окремо розгортана та виконувана одиниця: окремий процес операційної системи, серверний мікросервіс, веб-додаток у браузері, мобільний клієнт, реляційна база даних чи черга повідомлень.
- **Синтаксис:** `container <identifier> [name] [description] [technology] [tags] { ... }`
- **Особливості:**
  - Поле `technology` є критично важливим: воно вказує точний технологічний стек (наприклад, `Go 1.22 / Gin`, `PostgreSQL 16`, `React 18 / TypeScript`).
  - Всередині контейнера можуть бути оголошені дочірні компоненти (для рівня L3).

### 2.4. Компонент (Component)
Модульна структурна одиниця коду всередині контейнера. Компонент не можна розгорнути окремо від контейнера: він виконується в тому самому адресному просторі процесу й надає чітко визначений інтерфейс.
- **Синтаксис:** `component <identifier> [name] [description] [technology] [tags]`
- **Типові приклади:** контролер API, сервіс доменної логіки, адаптер сховища, модуль шифрування.

---

## 3. Моделювання зв'язків (Relationships)

Зв'язок у C4 — це односпрямований виклик або потік даних від сутності-джерела (Source) до сутності-приймача (Destination).

### Синтаксис оголошення зв'язку:
```dsl
<source_identifier> -> <destination_identifier> [description] [technology] [tags]
```

### Правила та інваріанти зв'язків:
1. **Явність протоколу.** Поле `technology` має містити назву мережевого або міжпроцесного протоколу: `[JSON/HTTPS]`, `[gRPC/Protobuf]`, `[SQL/TCP (Port 5432)]`, `[AMQP 0-9-1]`, `[In-process / Go Interface]`.
2. **Семантика дієслова.** Опис повинен містити активну дію в теперішньому часі (наприклад, *«Створює замовлення»*, а не *«Замовлення»*).
3. **Автоматичне згортання (Implied Relationships).** Якщо зв'язок оголошено між двома компонентами, які належать різним контейнерам, компілятор Structurizr автоматично створює відповідні неявні зв'язки вищого рівня між самими контейнерами та системами. Це звільняє інженера від необхідності дублювати зв'язки на кожному рівні масштабування вручну.

---

## 4. Специфікація блоку проєкцій (Views)

Блок `views` керує генерацією діаграм. Кожна діаграма має унікальний ключ (Key), тип та набір інструкцій компонування.

### 4.1. Доступні типи діаграм:
- `systemLandscape <key> [description]` — відображає всі програмні системи та персони організації на одній глобальній карті.
- `systemContext <softwareSystem_id> <key> [description]` — діаграма системного контексту для обраної системи (L1).
- `container <softwareSystem_id> <key> [description]` — діаграма контейнерів обраної системи (L2).
- `component <container_id> <key> [description]` — діаграма компонентів обраного контейнера (L3).
- `deployment <softwareSystem_id> <environment> <key> [description]` — топологія розгортання системи у зазначеному середовищі (`Production`, `Staging`, `Development`).
- `dynamic [softwareSystem_id | container_id] <key> [description]` — нумерована послідовність кроків виконання конкретного сценарію між елементами.

### 4.2. Інструкції керування вмістом діаграми:
- `include <element_id | *>` — включити елемент, групу або всі суміжні сутності (`*`).
- `exclude <element_id | relationship_id>` — виключити елемент або зв'язок із поточної діаграми для зменшення візуального шуму.
- `autoLayout [tb | bt | lr | rl] [rankSeparation] [nodeSeparation]` — увімкнути автоматичне розміщення блоків алгоритмом Graphviz (Top-to-Bottom, Left-to-Right тощо).
- `animation { ... }` — задати покрокову анімацію появи елементів для архітектурних презентацій.

---

## 5. Стилі та правила візуального кодування (Styles)

Стилі дозволяють застосовувати уніфіковане кольорове та геометричне кодування до елементів моделі на основі їхніх тегів.

### 5.1. Стилізація елементів (`element <tag> { ... }`)

| Властивість | Допустимі значення | Опис |
| :--- | :--- | :--- |
| `shape` | `Box`, `RoundedBox`, `Cylinder`, `Person`, `Pipe`, `Folder`, `Hexagon`, `WebBrowser`, `MobileDevicePortrait` | Геометрична форма блоку. |
| `background` | Шістнадцятковий колір (`#1e40af`, `#ffffff`) | Колір заливки блоку. |
| `color` | Шістнадцятковий колір (`#ffffff`, `#000000`) | Колір шрифту заголовка та тексту. |
| `stroke` | Шістнадцятковий колір (`#15803d`) | Колір контуру рамки. |
| `strokeWidth`| Ціле число в пікселях (`1`–`10`) | Товщина контуру рамки. |
| `fontSize` | Ціле число (`12`–`48`) | Розмір основного шрифту. |
| `border` | `solid`, `dashed`, `dotted` | Тип лінії контуру. |
| `opacity` | Число від `0` до `100` | Рівень прозорості блоку. |

### 5.2. Стилізація зв'язків (`relationship <tag> { ... }`)

| Властивість | Допустимі значення | Опис |
| :--- | :--- | :--- |
| `thickness` | Число в пікселях (`1`–`8`) | Товщина лінії стрілки. |
| `color` | Шістнадцятковий колір (`#334155`) | Колір лінії та підпису. |
| `style` | `solid`, `dashed`, `dotted` | Суцільна, пунктирна чи крапкова лінія. |
| `routing` | `Direct`, `Orthogonal`, `Curved` | Алгоритм прокладання траєкторії стрілки. |
| `fontSize` | Ціле число (`10`–`32`) | Розмір шрифту підпису зв'язку. |
| `width` | Число в пікселях | Максимальна ширина тексту підпису перед переносом рядка. |

---

## 6. Приклад повної специфікації робочого простору

Нижче наведено самодостатній приклад робочого простору Structurizr DSL, який демонструє всі ключові конструкції мови:

```dsl
workspace "Платіжна платформа" "Еталонний приклад моделі C4 на Structurizr DSL" {

    !identifiers hierarchical

    model {
        # Стейкхолдери
        customer = person "Покупець" "Клієнт сервісу, який замовляє послуги" "User"

        # Зовнішні системи
        acquiringBank = softwareSystem "Банк-еквайр" "Обробка транзакцій карток Visa/Mastercard" "External"

        # Наша програмна система
        platform = softwareSystem "Платіжна система" "Обробляє платежі та баланси" {
            webClient = container "Web SPA" "Клієнтський кабінет" "React / TypeScript" "WebBrowser"
            gateway = container "API Gateway" "Термінація TLS, маршрутизація, auth" "Envoy / Go" "Gateway"
            
            paymentEngine = container "Payment Engine" "Оркестрація транзакцій" "Go 1.22" "Microservice" {
                apiController = component "Payment Controller" "Приймає gRPC запити" "gRPC Server"
                sagaEngine = component "Saga Orchestrator" "Керує життєвим циклом транзакції" "State Machine"
                outbox = component "Outbox Publisher" "Атомарна фіксація подій" "Transactional Outbox"
                bankAdapter = component "Bank Gateway Adapter" "Клієнт банківського API" "ISO 8583 Client"
            }

            ledgerEngine = container "Ledger Service" "Бухгалтерський баланс" "C++20" "Microservice"
            mainDb = container "Payment DB" "Зберігає транзакції та outbox" "PostgreSQL 16" "Database"
            eventBus = container "Подієва шина" "Шина подій транзакцій" "Apache Kafka" "MessageBroker"
        }

        # Зв'язки бізнес-контексту
        customer -> platform.webClient "Створює платіж" "HTTPS"
        platform.webClient -> platform.gateway "REST API виклики" "JSON / HTTPS"
        platform.gateway -> platform.paymentEngine.apiController "ProcessPayment()" "gRPC / Protobuf"
        platform.gateway -> platform.ledgerEngine "GetBalance()" "gRPC / Protobuf"

        # Зв'язки всередині Payment Engine
        platform.paymentEngine.apiController -> platform.paymentEngine.sagaEngine "Передає команду" "In-process"
        platform.paymentEngine.sagaEngine -> platform.paymentEngine.outbox "Фіксує подію" "In-process"
        platform.paymentEngine.sagaEngine -> platform.paymentEngine.bankAdapter "Авторизація коштів" "In-process"
        platform.paymentEngine.bankAdapter -> acquiringBank "AuthorizeTransaction()" "ISO 8583 / TLS"

        # Зв'язки зі сховищами та шиною
        platform.paymentEngine.outbox -> platform.mainDb "Атомарний запис" "SQL / TCP"
        platform.paymentEngine.outbox -> platform.eventBus "Публікує подію PaymentApproved" "Kafka Wire Protocol"
        platform.eventBus -> platform.ledgerEngine "Споживає події платежів" "Kafka Consumer Group"
    }

    views {
        systemContext platform "System_Context" {
            include *
            autoLayout lr
        }

        container platform "Containers_Overview" {
            include *
            autoLayout lr
        }

        component platform.paymentEngine "PaymentEngine_Components" {
            include *
            autoLayout lr
        }

        dynamic platform "Payment_Saga_Execution" "Послідовність успішної оплати" {
            customer -> platform.webClient "1. Натискає сплатити"
            platform.webClient -> platform.gateway "2. POST /v1/payments [HTTPS]"
            platform.gateway -> platform.paymentEngine.apiController "3. ProcessPayment [gRPC]"
            platform.paymentEngine.sagaEngine -> platform.paymentEngine.bankAdapter "4. Authorize [ISO 8583]"
            platform.paymentEngine.bankAdapter -> acquiringBank "5. Відправка транзакції [TLS]"
            acquiringBank -> platform.paymentEngine.bankAdapter "6. Підтвердження оплати [TLS]"
            platform.paymentEngine.outbox -> platform.mainDb "7. Запис Payment(SUCCESS) [SQL]"
            platform.paymentEngine.outbox -> platform.eventBus "8. Публікація PaymentCompleted [Kafka]"
            autoLayout lr
        }

        styles {
            element "User" { shape Person background #15803d color #ffffff }
            element "Software System" { background #1e40af color #ffffff }
            element "External" { background #64748b color #ffffff }
            element "Container" { background #2563eb color #ffffff }
            element "Component" { background #7c3aed color #ffffff }
            element "Database" { shape Cylinder background #b45309 color #ffffff }
            element "MessageBroker" { shape Pipe background #b45309 color #ffffff }
            relationship "Relationship" { color #334155 thickness 2 fontSize 16 }
        }
    }
}
```

## 7. Модульність, константи та розширені механізми DSL

У великих корпоративних проєктах модель системи може містити сотні мікросервісів та тисячі зв'язків. Зберігати такий обсяг коду в одному файлі незручно, тому Structurizr DSL надає потужні засоби декомпозиції та автоматизації.

### 7.1. Модульна декомпозиція через директиву `!include`
Директива `!include` дозволяє розділяти опис великої системи на незалежні модулі, за які відповідають окремі команди:

```dsl
workspace "Enterprise Architecture" {
    model {
        customer = person "Customer" "Клієнт банку"
        
        # Підключення підсистем з окремих файлів
        !include components/payment-system.dsl
        !include components/fraud-engine.dsl
        !include components/notification-service.dsl

        customer -> paymentSystem.apiGateway "Створює замовлення [HTTPS]"
    }
}
```

### 7.2. Константи та параметризація моделі
Директива `!constant` дозволяє оголошувати глобальні змінні для версій протоколів, портів або технологічних стеків, що запобігає дублюванню рядків:

```dsl
!constant DEFAULT_DB_TECH "PostgreSQL 16.2 with pgvector"
!constant API_PROTOCOL "gRPC / HTTP2 via Envoy"

container "Analytics DB" "Сховище векторних ембеддінгів" "${DEFAULT_DB_TECH}"
```

### 7.3. Складні селектори та вирази вибірки в проєкціях
У блоці `views` можна використовувати логічні селектори на основі тегів для точного фільтрування діаграм:
- `include "element.tag == Microservice and element.tag == Critical"` — включити лише критичні мікросервіси.
- `exclude "relationship.tag == Async"` — приховати всі асинхронні зв'язки, залишивши лише синхронний RPC-потік для аналізу латентності.
- `include "element.parent == paymentPlatform"` — автоматично вибрати всі дочірні контейнери конкретної системи.

Ця декларативна специфікація є єдиним джерелом правди для всієї системи. Будь-які зміни в архітектурі вносяться через редагування цього коду в системі контролю версій.
