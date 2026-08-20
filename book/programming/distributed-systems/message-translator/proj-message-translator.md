# ⚙️ Реалізація надійного транслятора повідомлень: конвеєр перетворення та карантин DLQ

У розподілених архітектурах транслятор повідомлень є першою лінією оборони внутрішніх сервісів від хаосу зовнішніх даних. Коли вебхук платіжного шлюзу, партнерський сервіс доставки або стара монолітна ERP надсилають повідомлення з нестандартними полями, нетипізованими рядками та магічними числовими статусами, система не може просто передати цей пакет далі у внутрішню шину. Помилка десеріалізації або порушення бізнес-інваріанту глибше в системі здатні зупинити конвеєр обробки замовлень для тисяч клієнтів.

Транслятор повинен виконати три послідовні задачі: безпечно розібрати вхідний сирий потік, перевірити синтаксичні та семантичні обмеження, трансформувати дані в канонічний контракт із уніфікованими метаданими трасування, а в разі будь-якого збою — ізолювати пошкоджений пакет у мертву чергу (англ. *Dead Letter Queue, DLQ*) без зупинки основного потоку обробки.

## Архітектура конвеєра: стадії, DTO та карантин

Конвеєр трансляції побудовано за схемою поетапної обробки з обов'язковим розгалуженням на успішний вихід та карантинний буфер:

```
[Вхідний сирий потік]
        │
        ▼
┌───────────────────────┐       Помилка синтаксису
│ 1. Синтаксичний аналіз ├──────────────────────────────┐
└──────────┬────────────┘                               │
           │ Успіх                                      │
           ▼                                            ▼
┌───────────────────────┐       Порушення правил    ┌─────────────────────────┐
│ 2. Семантична валідація ├─────────────────────────►│  Карантинний конверт    │
└──────────┬────────────┘                           │  (Dead Letter Queue)    │
           │ Валідно                                │                         │
           ▼                                        │  • Код та опис помилки  │
┌───────────────────────┐                           │  • Збережений сирий buf │
│ 3. Мапінг у канонічну ├───────────────────────────┤  • Мітка часу та траса  │
│    модель і конверсія │   Помилка нормалізації    └────────────┬────────────┘
└──────────┬────────────┘                                        │
           │ Готово                                              ▼
           ▼                                            [Вихід у топік DLQ]
┌───────────────────────┐
│ 4. Серіалізація в     │
│    канонічний бінарник│
└──────────┬────────────┘
           │
           ▼
[Вихід у внутрішню чергу]
```

Для демонстрації ми реалізуємо транслятор зовнішніх замовлень. Вхідний пакет надходить у вигляді тексту з роздільниками або текстового JSON-подібного словника із застарілої системи:
- `order_id`: числовий ідентифікатор застарілого зразка.
- `cust_ref`: текстовий код контрагента.
- `amount_cents`: сума у найменших одиницях валюти (ціле число).
- `curr`: літерний код валюти (очікується `"UAH"`, `"USD"`, `"EUR"`).
- `raw_status`: числовий статус застарілої системи (`101` — створено, `102` — підтверджено, `103` — відвантажено, `999` — скасовано).

Цільова канонічна модель вимагає:
1. **Канонічний конверт**: глобальний `message_id` (UUIDv4), `correlation_id` для розподіленого трасування, версія схеми (`v1`), мітка часу створення у форматі Unix Epoch (мілісекунди).
2. **Типізовані доменні сутності**: суворе перерахування статусів, перевірені коди валют, нормалізовані ідентифікатори.

## Програмна реалізація конвеєра

Нижче наведено повну реалізацію транслятора повідомлень двома мовами: на чистому C з ручним контролем буферів і строгою перевіркою кодів помилок, та ідіоматичною мовою C++20 із використанням `std::expected`, типізованих структур і безпечних строкових представлень `std::string_view`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/* Коди результатів трансляції */
typedef enum {
    TRANS_OK = 0,
    TRANS_ERR_SYNTAX = 1,
    TRANS_ERR_INVALID_CURRENCY = 2,
    TRANS_ERR_INVALID_STATUS = 3,
    TRANS_ERR_INVALID_AMOUNT = 4,
    TRANS_ERR_BUFFER_OVERFLOW = 5
} TranslateStatus;

/* Канонічні статуси замовлення */
typedef enum {
    CANONICAL_STATUS_CREATED = 1,
    CANONICAL_STATUS_CONFIRMED = 2,
    CANONICAL_STATUS_SHIPPED = 3,
    CANONICAL_STATUS_CANCELLED = 4
} CanonicalOrderStatus;

/* Канонічна модель даних замовлення */
typedef struct {
    char message_id[37];
    char correlation_id[64];
    uint64_t timestamp_ms;
    uint32_t schema_version;

    uint64_t order_id;
    char customer_ref[32];
    uint64_t amount_cents;
    char currency[4];
    CanonicalOrderStatus status;
} CanonicalOrderMessage;

/* Структура для мертвої черги (DLQ) */
typedef struct {
    char dlq_id[37];
    TranslateStatus error_code;
    char error_reason[128];
    uint64_t failed_at_ms;
    char raw_payload[512];
} DeadLetterEnvelope;

/* Допоміжні функції часу та генерації ID */
static uint64_t current_time_millis(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)(ts.tv_sec * 1000ULL + ts.tv_nsec / 1000000ULL);
}

static void generate_dummy_uuid(char *out, size_t size, uint64_t seed) {
    snprintf(out, size, "msg-%08lx-%04x-4000-8000-%012lx",
             (unsigned long)(seed & 0xFFFFFFFF),
             (unsigned int)((seed >> 32) & 0xFFFF),
             (unsigned long)(seed ^ 0xDEADBEEFULL));
}

/* 1. Синтаксичний парсинг і семантична валідація вхідного тексту */
TranslateStatus translate_legacy_message(
    const char *raw_input,
    const char *correlation_id,
    CanonicalOrderMessage *out_msg,
    DeadLetterEnvelope *out_dlq
) {
    if (!raw_input || !out_msg || !out_dlq) {
        return TRANS_ERR_SYNTAX;
    }

    uint64_t order_id = 0;
    char cust[32] = {0};
    uint64_t cents = 0;
    char curr[8] = {0};
    int raw_status = 0;

    /* Очікуваний формат рядка: order_id;cust_ref;amount_cents;currency;status_code */
    int parsed = sscanf(raw_input, "%lu;%31[^;];%lu;%7[^;];%d",
                        &order_id, cust, &cents, curr, &raw_status);

    if (parsed != 5) {
        out_dlq->error_code = TRANS_ERR_SYNTAX;
        snprintf(out_dlq->error_reason, sizeof(out_dlq->error_reason),
                 "Invalid syntax: expected 5 fields separated by semicolon, parsed %d", parsed);
        out_dlq->failed_at_ms = current_time_millis();
        generate_dummy_uuid(out_dlq->dlq_id, sizeof(out_dlq->dlq_id), out_dlq->failed_at_ms);
        snprintf(out_dlq->raw_payload, sizeof(out_dlq->raw_payload), "%s", raw_input);
        return TRANS_ERR_SYNTAX;
    }

    /* Семантична перевірка суми */
    if (cents == 0 || cents > 100000000000ULL) {
        out_dlq->error_code = TRANS_ERR_INVALID_AMOUNT;
        snprintf(out_dlq->error_reason, sizeof(out_dlq->error_reason),
                 "Invalid amount_cents: %lu out of allowed range (1..100000000000)", cents);
        out_dlq->failed_at_ms = current_time_millis();
        generate_dummy_uuid(out_dlq->dlq_id, sizeof(out_dlq->dlq_id), out_dlq->failed_at_ms);
        snprintf(out_dlq->raw_payload, sizeof(out_dlq->raw_payload), "%s", raw_input);
        return TRANS_ERR_INVALID_AMOUNT;
    }

    /* Семантична перевірка валюти */
    if (strcmp(curr, "UAH") != 0 && strcmp(curr, "USD") != 0 && strcmp(curr, "EUR") != 0) {
        out_dlq->error_code = TRANS_ERR_INVALID_CURRENCY;
        snprintf(out_dlq->error_reason, sizeof(out_dlq->error_reason),
                 "Unsupported currency code: '%s'", curr);
        out_dlq->failed_at_ms = current_time_millis();
        generate_dummy_uuid(out_dlq->dlq_id, sizeof(out_dlq->dlq_id), out_dlq->failed_at_ms);
        snprintf(out_dlq->raw_payload, sizeof(out_dlq->raw_payload), "%s", raw_input);
        return TRANS_ERR_INVALID_CURRENCY;
    }

    /* Мапінг застарілих статусів на канонічні */
    CanonicalOrderStatus canonical_status;
    switch (raw_status) {
        case 101: canonical_status = CANONICAL_STATUS_CREATED; break;
        case 102: canonical_status = CANONICAL_STATUS_CONFIRMED; break;
        case 103: canonical_status = CANONICAL_STATUS_SHIPPED; break;
        case 999: canonical_status = CANONICAL_STATUS_CANCELLED; break;
        default:
            out_dlq->error_code = TRANS_ERR_INVALID_STATUS;
            snprintf(out_dlq->error_reason, sizeof(out_dlq->error_reason),
                     "Unknown legacy status code: %d", raw_status);
            out_dlq->failed_at_ms = current_time_millis();
            generate_dummy_uuid(out_dlq->dlq_id, sizeof(out_dlq->dlq_id), out_dlq->failed_at_ms);
            snprintf(out_dlq->raw_payload, sizeof(out_dlq->raw_payload), "%s", raw_input);
            return TRANS_ERR_INVALID_STATUS;
    }

    /* Заповнення канонічного повідомлення */
    out_msg->timestamp_ms = current_time_millis();
    out_msg->schema_version = 1;
    generate_dummy_uuid(out_msg->message_id, sizeof(out_msg->message_id), out_msg->timestamp_ms);
    snprintf(out_msg->correlation_id, sizeof(out_msg->correlation_id), "%s",
             correlation_id ? correlation_id : "unknown-trace");

    out_msg->order_id = order_id;
    snprintf(out_msg->customer_ref, sizeof(out_msg->customer_ref), "%s", cust);
    out_msg->amount_cents = cents;
    snprintf(out_msg->currency, sizeof(out_msg->currency), "%s", curr);
    out_msg->status = canonical_status;

    return TRANS_OK;
}

/* 2. Бінарна серіалізація канонічного повідомлення */
size_t serialize_canonical_message(
    const CanonicalOrderMessage *msg,
    uint8_t *out_buf,
    size_t buf_size
) {
    if (!msg || !out_buf || buf_size < 256) {
        return 0;
    }

    /* Простий двійковий формат: заголовок + фіксовані поля + строки */
    size_t offset = 0;

    /* Магічний байт формату 0xCF 0x01 (Canonical Format v1) */
    out_buf[offset++] = 0xCF;
    out_buf[offset++] = 0x01;

    /* Запис schema_version (4 байти, little-endian) */
    uint32_t ver = msg->schema_version;
    memcpy(out_buf + offset, &ver, sizeof(ver));
    offset += sizeof(ver);

    /* Запис timestamp_ms (8 байтів) */
    uint64_t ts = msg->timestamp_ms;
    memcpy(out_buf + offset, &ts, sizeof(ts));
    offset += sizeof(ts);

    /* Запис order_id (8 байтів) */
    uint64_t oid = msg->order_id;
    memcpy(out_buf + offset, &oid, sizeof(oid));
    offset += sizeof(oid);

    /* Запис amount_cents (8 байтів) */
    uint64_t amt = msg->amount_cents;
    memcpy(out_buf + offset, &amt, sizeof(amt));
    offset += sizeof(amt);

    /* Запис статусу (1 байт) */
    out_buf[offset++] = (uint8_t)msg->status;

    /* Запис валюти (4 байти фіксовано) */
    memcpy(out_buf + offset, msg->currency, 4);
    offset += 4;

    /* Запис довжини та тіла customer_ref */
    uint8_t cust_len = (uint8_t)strlen(msg->customer_ref);
    out_buf[offset++] = cust_len;
    memcpy(out_buf + offset, msg->customer_ref, cust_len);
    offset += cust_len;

    return offset;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <cstdint>
#include <chrono>
#include <expected>
#include <optional>
#include <sstream>
#include <iomanip>

namespace integration {

/* Канонічні статуси замовлення */
enum class OrderStatus : uint8_t {
    Created = 1,
    Confirmed = 2,
    Shipped = 3,
    Cancelled = 4
};

/* Коди помилок трансляції */
enum class TranslationError : uint8_t {
    SyntaxError,
    InvalidCurrency,
    InvalidStatus,
    InvalidAmount,
    BufferOverflow
};

/* Канонічна модель даних замовлення */
struct CanonicalOrderMessage {
    std::string message_id;
    std::string correlation_id;
    uint64_t timestamp_ms{0};
    uint32_t schema_version{1};

    uint64_t order_id{0};
    std::string customer_ref;
    uint64_t amount_cents{0};
    std::string currency;
    OrderStatus status{OrderStatus::Created};
};

/* Модель мертвої черги (DLQ) */
struct DeadLetterEnvelope {
    std::string dlq_id;
    TranslationError error_code;
    std::string error_reason;
    uint64_t failed_at_ms{0};
    std::string raw_payload;
};

class MessageTranslator {
public:
    static uint64_t current_time_millis() noexcept {
        const auto now = std::chrono::system_clock::now();
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()
        ).count();
    }

    static std::string generate_id(std::string_view prefix, uint64_t seed) {
        std::ostringstream ss;
        ss << prefix << "-" << std::hex << std::setfill('0')
           << std::setw(8) << (seed & 0xFFFFFFFF)
           << "-4000-8000-"
           << std::setw(12) << (seed ^ 0xDEADBEEFULL);
        return ss.str();
    }

    /* Головна точка входу: повертає канонічне повідомлення або DLQ-конверт */
    static std::expected<CanonicalOrderMessage, DeadLetterEnvelope> translate(
        std::string_view raw_input,
        std::string_view correlation_id
    ) {
        const uint64_t now_ms = current_time_millis();

        // 1. Розбір рядка за роздільником ';'
        std::vector<std::string_view> tokens;
        size_t start = 0;
        while (start < raw_input.size()) {
            const size_t end = raw_input.find(';', start);
            if (end == std::string_view::npos) {
                tokens.push_back(raw_input.substr(start));
                break;
            }
            tokens.push_back(raw_input.substr(start, end - start));
            start = end + 1;
        }

        if (tokens.size() != 5) {
            return std::unexpected(DeadLetterEnvelope{
                .dlq_id = generate_id("dlq", now_ms),
                .error_code = TranslationError::SyntaxError,
                .error_reason = "Invalid syntax: expected 5 tokens, got " + std::to_string(tokens.size()),
                .failed_at_ms = now_ms,
                .raw_payload = std::string(raw_input)
            });
        }

        // 2. Безпечне зчитування полів
        uint64_t order_id = 0;
        uint64_t cents = 0;
        int legacy_status = 0;

        try {
            order_id = std::stoull(std::string(tokens[0]));
            cents = std::stoull(std::string(tokens[2]));
            legacy_status = std::stoi(std::string(tokens[4]));
        } catch (const std::exception& e) {
            return std::unexpected(DeadLetterEnvelope{
                .dlq_id = generate_id("dlq", now_ms),
                .error_code = TranslationError::SyntaxError,
                .error_reason = std::string("Numeric parse failure: ") + e.what(),
                .failed_at_ms = now_ms,
                .raw_payload = std::string(raw_input)
            });
        }

        // 3. Семантична валідація суми
        if (cents == 0 || cents > 100'000'000'000ULL) {
            return std::unexpected(DeadLetterEnvelope{
                .dlq_id = generate_id("dlq", now_ms),
                .error_code = TranslationError::InvalidAmount,
                .error_reason = "Amount cents out of bounds: " + std::to_string(cents),
                .failed_at_ms = now_ms,
                .raw_payload = std::string(raw_input)
            });
        }

        // 4. Валідація коду валюти
        const std::string_view curr = tokens[3];
        if (curr != "UAH" && curr != "USD" && curr != "EUR") {
            return std::unexpected(DeadLetterEnvelope{
                .dlq_id = generate_id("dlq", now_ms),
                .error_code = TranslationError::InvalidCurrency,
                .error_reason = "Unsupported currency code: " + std::string(curr),
                .failed_at_ms = now_ms,
                .raw_payload = std::string(raw_input)
            });
        }

        // 5. Мапінг статусів
        OrderStatus status;
        switch (legacy_status) {
            case 101: status = OrderStatus::Created; break;
            case 102: status = OrderStatus::Confirmed; break;
            case 103: status = OrderStatus::Shipped; break;
            case 999: status = OrderStatus::Cancelled; break;
            default:
                return std::unexpected(DeadLetterEnvelope{
                    .dlq_id = generate_id("dlq", now_ms),
                    .error_code = TranslationError::InvalidStatus,
                    .error_reason = "Unknown legacy status code: " + std::to_string(legacy_status),
                    .failed_at_ms = now_ms,
                    .raw_payload = std::string(raw_input)
                });
        }

        // 6. Побудова чистої канонічної моделі
        CanonicalOrderMessage msg{
            .message_id = generate_id("msg", now_ms),
            .correlation_id = std::string(correlation_id.empty() ? "unknown-trace" : correlation_id),
            .timestamp_ms = now_ms,
            .schema_version = 1,
            .order_id = order_id,
            .customer_ref = std::string(tokens[1]),
            .amount_cents = cents,
            .currency = std::string(curr),
            .status = status
        };

        return msg;
    }

    /* 7. Бінарна серіалізація у двійковий формат без динамічних алокацій */
    static std::vector<uint8_t> serialize(const CanonicalOrderMessage& msg) {
        std::vector<uint8_t> buffer;
        buffer.reserve(128 + msg.customer_ref.size());

        // Магічний префікс (0xCF 0x01)
        buffer.push_back(0xCF);
        buffer.push_back(0x01);

        auto append_bytes = [&buffer](const auto& value) {
            const auto* ptr = reinterpret_cast<const uint8_t*>(&value);
            buffer.insert(buffer.end(), ptr, ptr + sizeof(value));
        };

        append_bytes(msg.schema_version);
        append_bytes(msg.timestamp_ms);
        append_bytes(msg.order_id);
        append_bytes(msg.amount_cents);

        buffer.push_back(static_cast<uint8_t>(msg.status));

        // Фіксовані 4 байти під код валюти
        char curr_buf[4] = {0};
        std::copy_n(msg.currency.data(), std::min(size_t{3}, msg.currency.size()), curr_buf);
        buffer.insert(buffer.end(), curr_buf, curr_buf + 4);

        // Довжина та рядок customer_ref
        const auto cust_len = static_cast<uint8_t>(std::min(size_t{255}, msg.customer_ref.size()));
        buffer.push_back(cust_len);
        buffer.insert(buffer.end(), msg.customer_ref.begin(), msg.customer_ref.begin() + cust_len);

        return buffer;
    }
};

} // namespace integration
```
:::

## Поглиблений аналіз механізмів надійності та пасток реалізації

Проєктування транслятора в промислових сервісах із високою пропускною здатністю (від 10 000 до 100 000 повідомлень за секунду) вимагає суворого врахування низки системних факторів, де кожна помилка управління пам'яттю або неточний тип даних створює каскадну аварію.

### 1. Ізоляція синтаксичних помилок і захист від переповнення буферів

Перший критичний бар'єр конвеєра — синтаксичний розбір сирого вхідного потоку. У реальних розподілених системах вхідні байти надходять через ненадійні мережеві канали, де можливі обриви TCP-з'єднань, неповні пакети, незакриті рядкові лапки у JSON, пошкоджені XML-теги або навмисні спроби атак типу переповнення буфера (*buffer overflow*).

- **У реалізації мовою C** виклик функції `sscanf` супроводжується явним обмеженням довжини для рядкових полів: `%31[^;]` та `%7[^;]`. Якщо зовнішня система надішле рядок довжиною 10 000 символів замість короткого коду контрагента, парсер безпечно зчитає перші 31 байт і зупиниться, не пошкодивши сусідні змінні на стеку виклику. Більше того, строга перевірка кількості зчитаних аргументів (`parsed == 5`) запобігає використанню частково ініціалізованої пам'яті.
- **У реалізації мовою C++** парсер реалізує техніку нуль-копіювального розбиття рядка за допомогою `std::string_view`. Під час початкового пошуку роздільників пам'ять під рядки не виділяється у динамічній купі (*heap*): вектор `tokens` зберігає лише пари «вказівник + довжина» безпосередньо у вихідному незмінному буфері. Тільки після того, як валідація структури підтвердить коректність формату, формується фінальний об'єкт `CanonicalOrderMessage`. Конверсія числових значень захищена блоком `try-catch`, що перехоплює винятки `std::invalid_argument` та `std::out_of_range`, трансформуючи їх у діагностичний запис DLQ.

### 2. Семантичні таблиці перетворення та строга типізація статусів

Застарілі монолітні системи часто оперують числовими магічними константами (`101`, `102`, `999`) або неформалізованими текстовими позначеннями (`"NEW"`, `"CONF"`, `"DONE"`). Якщо транслятор просто передасть ці сирі поля у внутрішній брокер, кожен сервіс-підписник буде змушений дублювати логіку інтерпретації чужих констант. Якщо джерело даних змінить значення `102` на `104`, уся розподілена система зазнає масштабного збою.

Транслятор бере на себе роль єдиного джерела правди (*single point of truth*):
- Він відображає числове значення на строгий перелічуваний тип `CanonicalOrderStatus` / `OrderStatus`.
- Блок `switch` обов'язково містить гілку за замовчуванням (`default`). Якщо зовнішня система впровадить новий невідомий статус (наприклад, `105`), транслятор не залишить поле в неініціалізованому стані й не пропустить пакет далі. Він негайно згенерує помилку `TRANS_ERR_INVALID_STATUS` / `TranslationError::InvalidStatus` і перенаправить повідомлення в карантин.

### 3. Фінансова арифметика: цілі копійки замість плаваючої коми

Поширена архітектурна помилка в трансляторах — зчитування грошових сум у типи з плаваючою комою `float` або `double` (наприклад, `$ 19.99`). Через особливості двійкового представлення стандарту IEEE 754 десяткові дроби не можуть бути представлені точно: число `0.1 + 0.2` перетворюється на `0.30000000000000004`. Після проходження через кілька трансляторів і сервісів накопичена похибка призводить до розбіжностей у фінансових балансах на центи й копійки, що є неприпустимим у банківському обліку.

Канонічна модель використовує підхід фіксованої точності: грошові суми завжди передаються у найменших неподільних одиницях валюти (центах, копійках, сатоші) у вигляді цілих 64-бітних чисел без знаку `uint64_t` (`amount_cents`). Сума `19.99 грн` зберігається як ціле число `1999`. Це гарантує абсолютну точність арифметичних операцій на всіх вузлах системи незалежно від мови програмування та апаратної платформи.

### 4. Анатомія карантинного конверта (Dead Letter Envelope) та стратегія Replay

Коли вхідний пакет не проходить валідацію, транслятор не повинен робити дві речі:
1. **Ковтати помилку мовчки**: якщо просто викинути пакет і записати попередження в лог, замовлення клієнта загубиться назавжди, а бізнес отримає фінансові збитки.
2. **Зациклювати повторні спроби (Retry Loop)**: якщо повідомлення синтаксично пошкоджене або містить неіснуючу валюту `"XYZ"`, жоден автоматичний повтор через 5 секунд не зробить його коректним. Нескінченний цикл повторів лише заблокує чергу і призведе до вичерпання ресурсів процесора.

Єдине правильне рішення — ізоляція в мертву чергу (*Dead Letter Queue*). Карантинний конверт формується за строгим стандартом:
- `dlq_id`: унікальний ідентифікатор інциденту для швидкого пошуку в системі моніторингу та логах.
- `error_code` та `error_reason`: точне людське та машинне пояснення, чому саме повідомлення було відхилено (наприклад, `Numeric parse failure` або `Unsupported currency code: 'GBP'`).
- `failed_at_ms`: точний момент аварії для побудови часових графіків збоїв.
- `raw_payload`: збереження оригінальних вхідних байтів повідомлення без найменших змін.

Збереження сирого тіла має фундаментальне значення: після того як черговий інженер виправить помилку в коді транслятора (наприклад, додасть підтримку валюти `"GBP"` у конфігурацію) або розробники партнерського сервісу виправлять баг у своєму експорті, спеціальна утиліта-реплеєр зчитує повідомлення з мертвої черги і повторно публікує їх у вхідний топік транслятора. Замовлення обробляється штатно, без необхідності турбувати кінцевого покупця.

### 5. Бінарна серіалізація та нуль-копіювання на гарячому шляху

У високонавантажених брокерах повідомлень (Apache Kafka, RabbitMQ) текстова серіалізація в JSON або XML створює надмірне навантаження на процесор через необхідність парсингу текстових ключів, обробки екранування символів та безперервного виділення пам'яті під динамічні структури.

У нашому проєкті функція `serialize` демонструє створення компактного бінарного представлення:
- Перші два байти відведено під магічне число `0xCF 0x01` (*Canonical Format v1*). Це дозволяє споживачам миттєво визначити версію бінарного формату ще до початку десеріалізації.
- Фіксовані поля (`schema_version`, `timestamp_ms`, `order_id`, `amount_cents`, `status`, `currency`) упаковуються у пам'яті послідовно зі збереженням фіксованого порядку байтів.
- Змінна частина (рядок `customer_ref`) записується за схемою *Length-Prefix*: 1 байт довжини, після якого йдуть корисні байти рядка без потреби в нуль-термінаторі.

Такий двійковий пакет займає лише 40–60 байтів у пам'яті (проти 250–400 байтів у форматі JSON з тими самими полями) і може бути розібраний на стороні споживача шляхом прямого відображення структури без жодної динамічної алокації пам'яті.

## Перекодування символів та нормалізація часових поясів

Дві найбільш підступні проблеми під час трансляції текстових повідомлень — невідповідність кодувань символів (*Character Encoding Mismatch*) та хаос із форматами часу й годинними поясами.

### 1. Транскодування UTF-8 та недійсні сурогатні байти

Застарілі корпоративні системи часто надсилають текст у локальних однобайтних кодуваннях (Windows-1251, Windows-1252, ISO-8859-1, KOI8-U). Якщо транслятор без перевірки інтерпретує такі байти як UTF-8, внутрішні парсери JSON або Protobuf впадуть із фатальною помилкою `Invalid UTF-8 byte sequence`.

Транслятор на етапі синтаксичного аналізу повинен виконувати валідацію UTF-8 або явне перекодування:
- Перевірка валідності послідовностей мультибайтних символів UTF-8 (заборона перекриваючих сурогатних пар та надлишкового кодування *overlong encoding*).
- Автоматичне відсікання мітки порядку байтів UTF-8 BOM (`0xEF 0xBB 0xBF`), яка часто додається утилітами Microsoft Windows на початку файлів і ламає стандартні JSON-парсери.
- Заміна пошкоджених або нерозпізнаних байтів на універсальний символ заміни Юнікоду `U+FFFD` (``) або негайне перенаправлення пакета в DLQ за прапорцем строгості конфігурації.

### 2. Нормалізація міток часу до UTC Epoch

Зовнішні джерела надсилають дати в десятках різноманітних форматів: ISO-8601 (`"2026-08-20T11:25:00Z"`), RFC 2822, локальні рядки без вказівки зміщення (`"20/08/2026 14:25:00"`) або специфічні дати мейнфреймів (`"2026232"` — рік та день за юліанським календарем).

Канонічна модель ліквідує будь-яку неоднозначність часових зон:
- Усі дати всередині канонічного повідомлення нормалізуються до **Unix Epoch у мілісекундах відносно нульового меридіана UTC** (`uint64_t timestamp_ms`).
- Якщо зовнішнє джерело надсилає час без вказівки годинного поясу, транслятор застосовує сконфігурований часовий пояс джерела (наприклад, `Europe/Kyiv`) і конвертує його в абсолютний час UTC.
- Завдяки цьому внутрішні споживачі позбавлені необхідності парсити строкові дати та виконувати перерахунок літнього/зимового часу під час кожного порівняння подій.

## Паралелізм, пули пам'яті та багатопоточність трансляції

У промислових системах транслятор працює як горизонтально масштабований пул потоків (*Worker Pool*), який вичитує повідомлення з кількох партицій вхідного журналу або паралельних черг.

Головна небезпека для продуктивності на цьому рівні — **конкуренція за блокування глобального алокатора пам'яті** (*malloc lock contention*). Якщо кожен потік-транслятор для кожного повідомлення виділяє десятки дрібних об'єктів у динамічній купі (парсинг рядків, конкатенація метаданих, виділення JSON-вузлів), потоки починають проводити більшість процесорного часу в очікуванні м'ютексів системного алокатора `glibc`.

Для досягнення високої пропускної здатності застосовують такі оптимізації:

1. **Локальні буфери потоку (Thread-Local Scratchpads)**: кожен потік транслятора ініціалізує фіксований буфер розміром 64 КБ при старті процесу. Усі проміжні операції парсингу, валідації та складання двійкового пакету виконуються всередині цього попередньо виділеного буфера без жодного звернення до `malloc` на гарячому шляху виконання.
2. **Нуль-копіювальне перенаправлення (Zero-Copy Pass-through)**: якщо повідомлення містить великі незмінні бінарні вкладення (наприклад, зашифровані цифрові підписи, скани документів або додаткові атрибути, які транслятор не трансформує), транслятор не копіює ці байти. Він зберігає лише вказівник на початок блоку та його розмір всередині вхідного мережевого буфера, а цільовий серіалізатор формує векторний запис за допомогою системних викликів розсіювання/збирання (*scatter-gather I/O*, `writev`).
3. **Пакетне підтвердження (Batched Acknowledgment)**: транслятор зчитує повідомлення пачками по 500–1000 штук, транслює їх паралельно, записує в цільовий топік і фіксує зміщення (*commit offset*) у вихідній черзі лише після успішної відправки всієї пачки. Якщо один пакет із пачки виявляється пошкодженим, він негайно відокремлюється в DLQ, а решта валідних повідомлень продовжує рух без блокування конвеєра.

## Еволюція схем і патерн толерантного читача (Tolerant Reader)

У розподілених системах різні мікросервіси оновлюються незалежно. Часто виникає ситуація, коли зовнішня система додає до повідомлення нові поля (наприклад, `discount_code` або `tracking_url`), про які стара версія транслятора ще не знає.

Наївна реалізація, яка жорстко перевіряє кількість полів і падає при появі будь-якого нового ключа, ламає систему при кожному сторонньому оновленні. Щоб забезпечити надійну сумісність, транслятор реалізує патерн **Tolerant Reader (Толерантний читач)**:
- Транслятор вичитує лише ті поля, які необхідні для поточної версії канонічного контракту.
- Усі невідомі додаткові поля ігноруються, якщо вони не оголошені як критичні прапорцем версії.
- Якщо цільова система підтримує динамічні метадані, невідомі поля упаковуються в спеціальний універсальний словник розширень (`extensions_map`), який передається далі без змін. Це дозволяє споживачам нових версій отримувати потрібні їм дані навіть тоді, коли проміжний транслятор ще не оновлювався до нової специфікації.

## Тестування стійкості: фаззинг і хаос-тести

Оскільки транслятор приймає неконтрольований потік даних із зовнішнього середовища, модуль повинен проходити обов'язкове тестування методом фаззингу (*fuzz testing* за допомогою LLVM `libFuzzer` або `AFL++`).

Фаззер генерує мільйони псевдовипадкових мутацій вхідних рядків:
- Нульові байти всередині тексту, від'ємні числа у беззнакових полях, гігантські суми, що перевищують `UINT64_MAX`.
- Рядки з мільйонами символів без роздільників, некоректні UTF-8 послідовності, пошкоджені escape-символи.

Головний інваріант транслятора під час фаззинг-тесту: **жоден вхідний потік байтів за жодних умов не повинен призводити до аварійного завершення процесу (Segmentation Fault / Panic), нескінченного циклу або витоку динамічної пам'яті**. Будь-який некоректний вхід зобов'язаний детерміновано завершуватися поверненням коду помилки та формуванням валідного DLQ-конверта.

## Спостережуваність, трасування W3C та метрики моніторингу

Надійний транслятор у хмарному середовищі надає вичерпну телеметрію для систем моніторингу та розподіленого трасування (Prometheus, Grafana, OpenTelemetry, Jaeger):
- `messages_translated_total{status="success|dlq", source="legacy_erp"}`: лічильник успішно оброблених та відхилених повідомлень. Стрибок кількості помилок DLQ негайно активує сповіщення черговим інженерам про зміну зовнішнього формату.
- `translation_duration_seconds_bucket`: гістограма часу виконання повної трансляції одного повідомлення. Нормальне значення для C/C++ транслятора лежить у діапазоні від 5 до 50 мікросекунд.
- `dlq_payload_bytes_total`: обсяг пам'яті, зайнятої повідомленнями в карантинній черзі, для контролю переповнення дисків брокера.
- **Наскрізне трасування W3C Trace Context**: транслятор зчитує заголовок `traceparent` (версія, `trace_id`, `parent_id`, `trace_flags`) з метаданих вхідного транспорту. Під час генерації канонічного повідомлення транслятор створює новий дочірній спан `span_id`, зберігаючи кореневий `trace_id`. Це дозволяє інженерам у Jaeger або OpenTelemetry побачити єдине дерево виконання: від моменту кліку користувача у браузері, через шлюз і транслятор, аж до запису в базу даних банку.
