# ⚙️ Конвеєр канонічної трансформації, валідації та проекції

У розподіленій системі взаємодія різнорідних сервісів потребує надійного перетворення сторонніх та застарілих форматів у суворо типізовану канонічну модель і подальшої генерації цільових структур для систем-споживачів. Пряме розкидання мапінгу по всьому коду додатків призводить до комбінаторного дублювання логіки, витоку сторонніх абстракцій у доменне ядро та неможливості безпечного оновлення версій схем.

Нижче наведено повноцінну виробничу реалізацію конвеєра Канонічної Моделі Даних (Canonical Data Model, CDM). Архітектура конвеєра реалізує класичні патерни Enterprise Integration: Антикорупційний шар (Anticorruption Layer, ACL), валідацію доменних інваріантів контракту та генерацію цільових проекцій без створення зайвих копій даних у пам'яті.

## Архітектурний дизайн конвеєра

Конвеєр побудовано за принципом лінійного конвеєра обробки (Pipeline Pattern), де кожен етап є чистим функціональним або об'єктним перетворенням із строго типізованими входами та виходами:
1. **Вхідний антикорупційний шар (Inbound ACL Translators)**: ізолює доменну модель від двох несумісних джерел:
   - Застарілої складської системи ERP, що передає неструктуровані плоскі рядки формату `CSV/Flat` із числовими магічними статусами та сумами у дробових числах;
   - Зовнішнього партнерського маркетплейсу, що відправляє сучасний `JSON`-подібний Webhook із власним неймінгом полів та текстовими статусами.
2. **Семантична нормалізація**:
   - Конверсія грошових сум із небезпечного двійкового формату `double` у точні цілі копійки (`uint64_t cents`), що унеможливлює накопичення похибок округлення;
   - Перетворення локальних статусів у суворе типізоване перерахування `CanonicalOrderStatus`;
   - Генерація канонічного конверта з монотонними часовими мітками UTC та наскрізними ідентифікаторами трасування (`correlation_id`).
3. **Валідатор канонічної схеми (Schema Validator)**:
   - Перевірка обов'язкових інваріантів (наявність `order_id`, валідність коду валюти, додатна сума замовлення, непорожній список товарів);
   - Повернення типізованого результату через сучасний контейнер `std::expected` замість використання повільних винятків або небезпечних числових кодів помилок.
4. **Вихідні проектори (Outbound Projectors)**:
   - Генерація компактного бінарного DTO для високонавантаженого сервісу білінгу;
   - Генерація суворого фіскального XML-звіту для передачі в державні податкові органи.

## Повний вихідний код конвеєра

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <cstdint>
#include <chrono>
#include <sstream>
#include <iomanip>

// ── 1. Канонічна модель даних (CDM Domain Contract) ─────────────────────────

enum class Currency {
    UAH,
    USD,
    EUR,
    UNKNOWN
};

enum class CanonicalOrderStatus {
    Created,
    Paid,
    Shipped,
    Cancelled
};

struct CanonicalLineItem {
    std::string sku;
    uint32_t quantity;
    uint64_t unit_price_cents; // Завжди в цілих мінімальних одиницях валюти
};

struct CanonicalMessageHeader {
    std::string message_id;      // UUIDv7 або унікальний строковий ідентифікатор
    std::string correlation_id;  // Наскрізний ідентифікатор транзакції
    std::string schema_version;  // SemVer версія канонічного контракту
    uint64_t timestamp_utc_ms;   // Unix Epoch у мілісекундах
    std::string origin_system;   // Джерело надходження повідомлення
};

struct CanonicalOrderPayload {
    std::string order_id;
    std::string customer_id;
    uint64_t total_amount_cents;
    Currency currency;
    CanonicalOrderStatus status;
    std::vector<CanonicalLineItem> items;
};

struct CanonicalOrderMessage {
    CanonicalMessageHeader header;
    CanonicalOrderPayload payload;
};

// ── 2. Вхідні сторонні формати (Raw Inbound Payloads) ────────────────────────

// Формат 1: Застаріла ERP-система (CSV/Flat рядок)
// Формат: "ORDER_ID,CUST_REF,STATUS_CODE,AMOUNT_FLOAT,CURRENCY_STR,SKU,QTY"
struct LegacyErpPayload {
    std::string raw_csv_line;
};

// Формат 2: Зовнішній веб-маркетплейс (JSON-подібний DTO)
struct PartnerWebhookPayload {
    std::string partner_id;
    std::string ext_order_ref;
    std::string user_email;
    double order_total;
    std::string curr;
    std::string state_str;
    std::string item_sku;
    int item_count;
};

// ── 3. Вхідні антикорупційні транслятори (Inbound ACL Translators) ───────────

class InboundTranslator {
public:
    static Currency parse_currency(std::string_view code) {
        if (code == "UAH") return Currency::UAH;
        if (code == "USD") return Currency::USD;
        if (code == "EUR") return Currency::EUR;
        return Currency::UNKNOWN;
    }

    static std::expected<CanonicalOrderMessage, std::string>
    from_legacy_erp(const LegacyErpPayload& input, std::string_view correlation_id) {
        std::stringstream ss(input.raw_csv_line);
        std::string order_id, cust_id, status_code_str, amount_str, curr_str, sku, qty_str;

        if (!std::getline(ss, order_id, ',') ||
            !std::getline(ss, cust_id, ',') ||
            !std::getline(ss, status_code_str, ',') ||
            !std::getline(ss, amount_str, ',') ||
            !std::getline(ss, curr_str, ',') ||
            !std::getline(ss, sku, ',') ||
            !std::getline(ss, qty_str, ',')) {
            return std::unexpected("ERP Translation Error: пошкоджений або неповний CSV рядок");
        }

        CanonicalOrderMessage msg;
        msg.header.message_id = "msg-erp-" + order_id;
        msg.header.correlation_id = std::string(correlation_id);
        msg.header.schema_version = "2.0.0";
        msg.header.timestamp_utc_ms = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count());
        msg.header.origin_system = "LEGACY_ERP_WAREHOUSE";

        msg.payload.order_id = order_id;
        msg.payload.customer_id = cust_id;

        // Нормалізація грошей: переведення float у цілі копійки без втрати точності
        try {
            double raw_amount = std::stod(amount_str);
            if (raw_amount < 0.0) {
                return std::unexpected("ERP Translation Error: від'ємна сума замовлення");
            }
            msg.payload.total_amount_cents = static_cast<uint64_t>(raw_amount * 100.0 + 0.5);
        } catch (...) {
            return std::unexpected("ERP Translation Error: невалідний числовий формат суми");
        }

        msg.payload.currency = parse_currency(curr_str);

        // Мапінг числових статусів застарілої системи
        try {
            int sc = std::stoi(status_code_str);
            switch (sc) {
                case 10: msg.payload.status = CanonicalOrderStatus::Created; break;
                case 20: msg.payload.status = CanonicalOrderStatus::Paid; break;
                case 30: msg.payload.status = CanonicalOrderStatus::Shipped; break;
                default: msg.payload.status = CanonicalOrderStatus::Cancelled; break;
            }
        } catch (...) {
            return std::unexpected("ERP Translation Error: невалідний код статусу");
        }

        uint32_t qty = 1;
        try {
            qty = static_cast<uint32_t>(std::stoul(qty_str));
            if (qty == 0) qty = 1;
        } catch (...) {
            qty = 1;
        }

        msg.payload.items.push_back({sku, qty, msg.payload.total_amount_cents / qty});

        return msg;
    }

    static std::expected<CanonicalOrderMessage, std::string>
    from_partner_webhook(const PartnerWebhookPayload& input, std::string_view correlation_id) {
        if (input.partner_id.empty() || input.ext_order_ref.empty()) {
            return std::unexpected("Partner Webhook Error: відсутній обов'язковий ідентифікатор");
        }

        CanonicalOrderMessage msg;
        msg.header.message_id = "msg-partner-" + input.ext_order_ref;
        msg.header.correlation_id = std::string(correlation_id);
        msg.header.schema_version = "2.0.0";
        msg.header.timestamp_utc_ms = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count());
        msg.header.origin_system = "PARTNER_" + input.partner_id;

        msg.payload.order_id = "PARTNER-" + input.ext_order_ref;
        msg.payload.customer_id = "USER-" + input.user_email;

        if (input.order_total < 0.0) {
            return std::unexpected("Partner Webhook Error: від'ємна сума в замовленні");
        }
        msg.payload.total_amount_cents = static_cast<uint64_t>(input.order_total * 100.0 + 0.5);
        msg.payload.currency = parse_currency(input.curr);

        if (input.state_str == "COMPLETED" || input.state_str == "SUCCESS") {
            msg.payload.status = CanonicalOrderStatus::Paid;
        } else if (input.state_str == "NEW") {
            msg.payload.status = CanonicalOrderStatus::Created;
        } else {
            msg.payload.status = CanonicalOrderStatus::Cancelled;
        }

        uint32_t qty = input.item_count > 0 ? static_cast<uint32_t>(input.item_count) : 1;
        msg.payload.items.push_back({input.item_sku, qty, msg.payload.total_amount_cents / qty});

        return msg;
    }
};

// ── 4. Валідатор канонічної схеми (Schema Validator) ─────────────────────────

class CanonicalSchemaValidator {
public:
    static std::expected<void, std::string> validate(const CanonicalOrderMessage& msg) {
        if (msg.header.correlation_id.empty()) {
            return std::unexpected("Validation Error: відсутній correlation_id");
        }
        if (msg.header.message_id.empty()) {
            return std::unexpected("Validation Error: відсутній message_id");
        }
        if (msg.payload.order_id.empty()) {
            return std::unexpected("Validation Error: порожній order_id");
        }
        if (msg.payload.customer_id.empty()) {
            return std::unexpected("Validation Error: порожній customer_id");
        }
        if (msg.payload.currency == Currency::UNKNOWN) {
            return std::unexpected("Validation Error: невідома або непідтримувана валюта операції");
        }
        if (msg.payload.total_amount_cents == 0) {
            return std::unexpected("Validation Error: нульова або некоректна сума замовлення");
        }
        if (msg.payload.items.empty()) {
            return std::unexpected("Validation Error: замовлення не містить жодної позиції товару");
        }
        return {};
    }
};

// ── 5. Вихідні адаптери-проектори (Outbound Projectors) ───────────────────────

struct BillingEventDto {
    std::string trace_id;
    std::string invoice_no;
    uint64_t charge_amount_cents;
    std::string currency_code;
    bool is_finalized;
};

struct FiscalXmlReportDto {
    std::string xml_document;
};

class OutboundProjector {
public:
    static BillingEventDto to_billing(const CanonicalOrderMessage& msg) {
        return BillingEventDto{
            .trace_id = msg.header.correlation_id,
            .invoice_no = "INV-" + msg.payload.order_id,
            .charge_amount_cents = msg.payload.total_amount_cents,
            .currency_code = (msg.payload.currency == Currency::UAH ? "UAH" : "USD"),
            .is_finalized = (msg.payload.status == CanonicalOrderStatus::Paid)
        };
    }

    static FiscalXmlReportDto to_fiscal_report(const CanonicalOrderMessage& msg) {
        std::ostringstream oss;
        oss << "<FiscalDocument id=\"" << msg.payload.order_id << "\">"
            << "<Origin>" << msg.header.origin_system << "</Origin>"
            << "<TotalCents>" << msg.payload.total_amount_cents << "</TotalCents>"
            << "<Timestamp>" << msg.header.timestamp_utc_ms << "</Timestamp>"
            << "<Status>" << (msg.payload.status == CanonicalOrderStatus::Paid ? "PAID" : "UNPAID") << "</Status>"
            << "</FiscalDocument>";
        return FiscalXmlReportDto{.xml_document = oss.str()};
    }
};

int main() {
    std::cout << "=== Тестування конвеєра Канонічної Моделі Даних ===" << std::endl;

    // Сценарій 1: Обробка замовлення зі застарілої ERP-системи
    LegacyErpPayload erp_input{"ORD-9021,CUST-4410,20,450.50,UAH,SKU-CHAIR-01,2"};
    auto erp_res = InboundTranslator::from_legacy_erp(erp_input, "corr-req-887123");

    if (erp_res) {
        auto val_res = CanonicalSchemaValidator::validate(*erp_res);
        if (val_res) {
            std::cout << "\n[ERP -> CDM]: Успішно нормалізовано канонічне замовлення:\n"
                      << "  ID: " << erp_res->payload.order_id << "\n"
                      << "  Сума (копійки): " << erp_res->payload.total_amount_cents << "\n"
                      << "  Джерело: " << erp_res->header.origin_system << "\n";

            auto billing = OutboundProjector::to_billing(*erp_res);
            std::cout << "  -> Вихідна проекція Billing Invoice: " << billing.invoice_no
                      << " (" << billing.charge_amount_cents << " cents)" << std::endl;
        } else {
            std::cerr << "Помилка валідації ERP: " << val_res.error() << std::endl;
        }
    } else {
        std::cerr << "Помилка трансляції ERP: " << erp_res.error() << std::endl;
    }

    // Сценарій 2: Обробка замовлення від зовнішнього партнера через Webhook
    PartnerWebhookPayload partner_input{
        .partner_id = "AMZN_STORE",
        .ext_order_ref = "EXT-554433",
        .user_email = "alex@example.com",
        .order_total = 129.99,
        .curr = "USD",
        .state_str = "SUCCESS",
        .item_sku = "SKU-HEADPHONES",
        .item_count = 1
    };

    auto partner_res = InboundTranslator::from_partner_webhook(partner_input, "corr-req-999001");
    if (partner_res) {
        auto val_res = CanonicalSchemaValidator::validate(*partner_res);
        if (val_res) {
            std::cout << "\n[Partner -> CDM]: Успішно нормалізовано канонічне замовлення:\n"
                      << "  ID: " << partner_res->payload.order_id << "\n"
                      << "  Клієнт: " << partner_res->payload.customer_id << "\n"
                      << "  Джерело: " << partner_res->header.origin_system << "\n";

            auto fiscal = OutboundProjector::to_fiscal_report(*partner_res);
            std::cout << "  -> Вихідна фіскальна XML-проекція:\n    "
                      << fiscal.xml_document << std::endl;
        } else {
            std::cerr << "Помилка валідації Partner: " << val_res.error() << std::endl;
        }
    } else {
        std::cerr << "Помилка трансляції Partner: " << partner_res.error() << std::endl;
    }

    return 0;
}
```
```ts
// TypeScript / Node.js еквівалент промислового конвеєра

export enum Currency {
    UAH = "UAH",
    USD = "USD",
    EUR = "EUR",
    UNKNOWN = "UNKNOWN"
}

export enum CanonicalOrderStatus {
    Created = "CREATED",
    Paid = "PAID",
    Shipped = "SHIPPED",
    Cancelled = "CANCELLED"
}

export interface CanonicalLineItem {
    sku: string;
    quantity: number;
    unitPriceCents: bigint;
}

export interface CanonicalMessageHeader {
    messageId: string;
    correlationId: string;
    schemaVersion: string;
    timestampUtcMs: number;
    originSystem: string;
}

export interface CanonicalOrderPayload {
    orderId: string;
    customerId: string;
    totalAmountCents: bigint;
    currency: Currency;
    status: CanonicalOrderStatus;
    items: CanonicalLineItem[];
}

export interface CanonicalOrderMessage {
    header: CanonicalMessageHeader;
    payload: CanonicalOrderPayload;
}

export class InboundTranslator {
    static parseCurrency(code: string): Currency {
        switch (code.toUpperCase()) {
            case "UAH": return Currency.UAH;
            case "USD": return Currency.USD;
            case "EUR": return Currency.EUR;
            default: return Currency.UNKNOWN;
        }
    }

    static fromPartnerWebhook(raw: any, correlationId: string): CanonicalOrderMessage {
        const orderTotal = Number(raw.order_total || 0);
        if (orderTotal < 0) {
            throw new Error("Partner Webhook Error: від'ємна сума замовлення");
        }
        const cents = BigInt(Math.round(orderTotal * 100));

        let status = CanonicalOrderStatus.Cancelled;
        if (raw.state_str === "SUCCESS" || raw.state_str === "COMPLETED") {
            status = CanonicalOrderStatus.Paid;
        } else if (raw.state_str === "NEW") {
            status = CanonicalOrderStatus.Created;
        }

        const qty = Number(raw.item_count) || 1;

        return {
            header: {
                messageId: `msg-ext-${raw.ext_order_ref}`,
                correlationId,
                schemaVersion: "2.0.0",
                timestampUtcMs: Date.now(),
                originSystem: `PARTNER_${raw.partner_id}`
            },
            payload: {
                orderId: `PARTNER-${raw.ext_order_ref}`,
                customerId: `USER-${raw.user_email}`,
                totalAmountCents: cents,
                currency: this.parseCurrency(String(raw.curr || "")),
                status,
                items: [{
                    sku: String(raw.item_sku || ""),
                    quantity: qty,
                    unitPriceCents: cents / BigInt(qty)
                }]
            }
        };
    }
}

export class CanonicalSchemaValidator {
    static validate(msg: CanonicalOrderMessage): void {
        if (!msg.header.correlationId) throw new Error("Validation Error: відсутній correlationId");
        if (!msg.header.messageId) throw new Error("Validation Error: відсутній messageId");
        if (!msg.payload.orderId) throw new Error("Validation Error: порожній orderId");
        if (msg.payload.currency === Currency.UNKNOWN) throw new Error("Validation Error: невідома валюта");
        if (msg.payload.totalAmountCents <= 0n) throw new Error("Validation Error: сума повинна бути більшою за 0");
        if (msg.payload.items.length === 0) throw new Error("Validation Error: список товарів порожній");
    }
}
```
:::

## Детальний розбір фаз та інженерні механізми

У наведеному коді реалізовано ключові інженерні принципи розподіленої інтеграції:

### 1. Ізоляція домену через типізовані адаптери
Зверніть увагу: доменний об'єкт `CanonicalOrderPayload` нічого не знає про те, чи прийшли дані з CSV-файлу 20-річної давнини, чи з сучасного хмарного Webhook. Уся брудна робота з парсингу рядків, вилучення роздільників, перевірки довжин та конверсії числових кодів інкапсульована всередині методів класу `InboundTranslator`. Якщо структура CSV-файлу зміниться (наприклад, додасться нова колонка з кодом відділення), правка буде внесена рівно в один метод `from_legacy_erp`, а доменне ядро та всі вихідні проекції залишаться непорушними.

### 2. Запобігання витоку похибок чисел із плаваючою комою
Коли джерело надсилає дробове число `450.50` або `129.99`, виконання математичних операцій безпосередньо над типом `double` є джерелом катастрофічних багів у фінансових системах. У нашому конвеєрі перетворення у цілі копійки відбувається одразу на вході за формулою:

```cpp
msg.payload.total_amount_cents = static_cast<uint64_t>(raw_amount * 100.0 + 0.5);
```

Додавання `0.5` гарантує коректне округлення найближчого двійкового дробу перед відтинанням дробової частини. Надалі у всіх внутрішніх розрахунках, розподілі податків та знижок використовується виключно 64-бітне ціле число.

### 3. Контроль відмов без винятків через `std::expected`
У високонавантажених сервісах обробка некоректних вхідних пакетів через механізм `try/catch` створює неприпустимі затримки (розгортання стеку вимагає тисяч тактів процесора). Використання стандарту C++23 `std::expected<T, E>` перетворює результат парсингу та валідації на легку структуру значення-або-помилка, що повертається через регістри процесора без виділення динамічної пам'яті.

## Керування ресурсами та продуктивність конвеєра

У системах із навантаженням понад `100 000` повідомлень на секунду наївне створення проміжних об'єктів створює значне навантаження на диспетчер пам'яті (Heap Allocator) операційної системи.

Для досягнення мінімальної затримки (Sub-Millisecond P99 Latency) у виробничих конвеєрах застосовують такі оптимізації:
- **Передача через `std::string_view`**: під час аналізу синтаксису вхідного повідомлення токенайзер не створює нові рядки для кожного поля, а оперує зрізами початкового буфера сокета без копіювання байтів (Zero-Copy Deserialization).
- **Поліморфні ресурси пам'яті (`std::pmr`)**: виділення пам'яті для контейнерів `std::vector` спирається на попередньо виділені арени на стеку або в пулі пам'яті потоку (`std::pmr::monotonic_buffer_resource`), повністю усуваючи системні виклики `malloc` та `free` на гарячому шляху виконання.
- **Попереднє резервування пам'яті**: масив товарів `items.reserve(N)` виділяє пам'ять один раз перед заповненням, запобігаючи багаторазовій релокації масиву.

## Багатопотоковість і масштабування обробки

Для забезпечення максимальної пропускної здатності на багатоядерних серверах вхідний конвеєр проектується як пул неблокуючих воркерів (Worker Pool) із прив'язкою потоків до ядер процесора (CPU Pinning / Core Affinity):
- Кожен робочий потік володіє власним локальним буфером пам'яті (Thread-Local Arena) для побудови канонічного повідомлення;
- Після валідації сформований пакет публікується у lock-free чергу відправника або безпосередньо в мережевий сокет брокера (Kafka Producer Ring Buffer);
- Відсутність спільних блокувань м'ютексів (Mutex Contention) між потоками дозволяє лінійно масштабувати продуктивність трансляції до мільйонів пакетів на секунду на сучасних 64-ядерних серверах.

## Пастки експлуатації та захист від аварій

Під час експлуатації канонічних конвеєрів виникають критичні ситуації, які вимагають надійних архітектурних захистів:
- **Отруйні повідомлення (Poison Messages)**: повідомлення, які не проходять валідацію схеми, ніколи не повинні повертатися назад у чергу повторно (Infinite Retry Loop). Якщо рядок містить битий синтаксис, жоден повторний виклик не виправить його. Таке повідомлення негайно перенаправляється у Мертву чергу (Dead Letter Queue) разом із повним діагностичним контекстом `TranslationError` для ручного аналізу інженерами.
- **Втрата контексту трасування (Trace Context Leak)**: якщо вхідний транслятор створює новий `message_id`, але забуває скопіювати вхідний `correlation_id` або заголовок `traceparent`, уся система розподіленого моніторингу втрачає зв'язок між діями користувача та фоновими задачами.
- **Неконтрольований витік внутрішніх полів**: якщо розробник додає в канонічну модель внутрішні специфічні прапорці однієї конкретної бази даних (наприклад, `ORACLE_ROW_ID_HASH`), канонічна модель втрачає нейтральність і починає отруювати всі підсистеми-споживачі.
