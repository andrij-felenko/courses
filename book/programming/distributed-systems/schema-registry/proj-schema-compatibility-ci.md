# ⚙️ Реалізація клієнтського кадрування, LRU-кешу та перевірки сумісності схем

Коли розподілена система обробляє сотні тисяч повідомлень на секунду, будь-яке синхронне мережеве звернення до реєстру схем під час відправлення чи отримання кожного окремого повідомлення миттєво перетворює високопродуктивний брокер повідомлень на повільний послідовний RPC-канал. Якщо затримка кругового обігу пакетів (RTT) до реєстру становить лише 2 мілісекунди, один потік продюсера фізично не зможе надіслати більше ніж 500 повідомлень на секунду.

Щоб досягти продуктивності у мільйони повідомлень на секунду, архітектура взаємодії з реєстром схем розділяється на два незалежних рівні:
1. **Гарячий шлях передачі даних (Data Plane):** Працює виключно в оперативній пам'яті процесу. Серіалізатор формує 5-байтовий двійковий кадр Confluent Wire Format і витягує збережені метадані з потокобезпечного кешу в RAM за 15–20 наносекунд без жодного мережевого вводу-виводу.
2. **Рівень управління та захисту (Control & Quality Plane):** Працює асинхронно при старті процесу та інтегрується в пайплайни безперервної інтеграції (CI/CD). Спеціалізований валідатор аналізує AST (абстрактне синтаксичне дерево) нових схем, перевіряючи правила сумісності ще до того, як код потрапить у репозиторій.

---

## 1. Кадрування повідомлень та потокобезпечний кеш у пам'яті

Клієнтський серіалізатор вирішує два завдання:
* Додає до кожного бінарного корисного навантаження службовий префікс: 1 магічний байт `0x00` та 4 байти 32-бітного беззнакового числа `Schema ID` у порядку Big-Endian.
* Під час десеріалізації миттєво розбирає заголовок, перевіряє валідність магічного маркера та знаходить відповідну схему у внутрішньому хеш-відображенні без блокування паралельних потоків обробки.

### 1.1. Порозрядне кодування та незалежність від архітектури процесора
Для пакування 32-бітного цілого числа `schema_id` у 4 байти не можна використовувати сирий виклик `memcpy(&buffer[1], &schema_id, 4)`, оскільки результат залежатиме від порядку байтів хоста (англ. *endianness*): на процесорах x86-64 (Little-Endian) молодший байт запишеться першим, що спотворить число на мережевому рівні.

Кадрувальник використовує явні побітові зсуви:
```
buffer[1] = (uint8_t)((schema_id >> 24) & 0xFF);  // Старший байт (Most Significant Byte)
buffer[2] = (uint8_t)((schema_id >> 16) & 0xFF);
buffer[3] = (uint8_t)((schema_id >> 8)  & 0xFF);
buffer[4] = (uint8_t)(schema_id         & 0xFF);  // Молодший байт (Least Significant Byte)
```
Це гарантує однакове представлення в мережі незалежно від апаратної платформи (x86_64, ARM64, RISC-V).

### 1.2. Багатопотокова масштабованість: `std::shared_mutex` (Read-Write Lock)
У типовому сервісі-споживачі 99.999% операцій десеріалізації є операціями читання з кешу (`cache hit`). Використання класичного ексклюзивного м'ютекса (`std::mutex`) створювало б штучну чергу між десятками потоків читання на багатоядерних процесорах. Використання розділеного блокування (`std::shared_mutex`) дозволяє сотням робочих потоків одночасно читати схеми без взаємного очікування (`std::shared_lock`), блокуючи кеш монопольно (`std::unique_lock`) лише в рідкісний момент першої появи нової версії схеми.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define WIRE_MAGIC_BYTE 0x00
#define WIRE_HEADER_SIZE 5
#define CACHE_CAPACITY 256

/* Елемент фіксованої таблиці локального кешу */
typedef struct {
    uint32_t schema_id;
    char *schema_json;
    bool is_active;
} SchemaCacheEntry;

typedef struct {
    SchemaCacheEntry entries[CACHE_CAPACITY];
    size_t count;
} LocalSchemaCache;

void cache_init(LocalSchemaCache *cache) {
    memset(cache, 0, sizeof(LocalSchemaCache));
}

void cache_free(LocalSchemaCache *cache) {
    for (size_t i = 0; i < CACHE_CAPACITY; ++i) {
        if (cache->entries[i].is_active && cache->entries[i].schema_json) {
            free(cache->entries[i].schema_json);
            cache->entries[i].schema_json = NULL;
            cache->entries[i].is_active = false;
        }
    }
    cache->count = 0;
}

bool cache_put(LocalSchemaCache *cache, uint32_t id, const char *json) {
    size_t slot = id % CACHE_CAPACITY;
    if (cache->entries[slot].is_active) {
        free(cache->entries[slot].schema_json);
    } else {
        cache->count++;
    }
    cache->entries[slot].schema_id = id;
    cache->entries[slot].schema_json = strdup(json);
    cache->entries[slot].is_active = true;
    return cache->entries[slot].schema_json != NULL;
}

const char* cache_get(const LocalSchemaCache *cache, uint32_t id) {
    size_t slot = id % CACHE_CAPACITY;
    if (cache->entries[slot].is_active && cache->entries[slot].schema_id == id) {
        return cache->entries[slot].schema_json;
    }
    return NULL;
}

/* Кодування кадру Confluent Wire Format (1 магічний байт + 4 байти Big-Endian ID) */
uint8_t* wire_encode(uint32_t schema_id, const uint8_t *payload, size_t payload_len, size_t *out_len) {
    *out_len = WIRE_HEADER_SIZE + payload_len;
    uint8_t *buffer = (uint8_t*)malloc(*out_len);
    if (!buffer) return NULL;

    /* Байт 0: Magic byte */
    buffer[0] = WIRE_MAGIC_BYTE;

    /* Байти 1–4: 32-бітний Schema ID у мережевому порядку (Big-Endian) */
    buffer[1] = (uint8_t)((schema_id >> 24) & 0xFF);
    buffer[2] = (uint8_t)((schema_id >> 16) & 0xFF);
    buffer[3] = (uint8_t)((schema_id >> 8) & 0xFF);
    buffer[4] = (uint8_t)(schema_id & 0xFF);

    /* Байти 5...N: Бінарне тіло */
    memcpy(buffer + WIRE_HEADER_SIZE, payload, payload_len);
    return buffer;
}

/* Декодування та валідація кадру */
bool wire_decode(const uint8_t *buffer, size_t buffer_len, uint32_t *out_schema_id, const uint8_t **out_payload, size_t *out_payload_len) {
    if (buffer_len < WIRE_HEADER_SIZE) {
        return false;
    }
    if (buffer[0] != WIRE_MAGIC_BYTE) {
        return false; /* Невідомий магічний байт: повідомлення пошкоджене або не є Wire Format */
    }

    *out_schema_id = ((uint32_t)buffer[1] << 24) |
                     ((uint32_t)buffer[2] << 16) |
                     ((uint32_t)buffer[3] << 8)  |
                     ((uint32_t)buffer[4]);

    *out_payload = buffer + WIRE_HEADER_SIZE;
    *out_payload_len = buffer_len - WIRE_HEADER_SIZE;
    return true;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <unordered_map>
#include <optional>
#include <shared_mutex>
#include <mutex>
#include <cstdint>
#include <stdexcept>

namespace schema_wire {

inline constexpr uint8_t MAGIC_BYTE = 0x00;
inline constexpr size_t HEADER_SIZE = 5;

/* Потокобезпечний кеш схем для гарячого шляху десеріалізації без копіювання */
class ThreadSafeSchemaCache {
public:
    void put(uint32_t schema_id, std::string schema_json) {
        std::unique_lock lock(mutex_);
        cache_[schema_id] = std::move(schema_json);
    }

    [[nodiscard]] std::optional<std::string> get(uint32_t schema_id) const {
        std::shared_lock lock(mutex_);
        if (auto it = cache_.find(schema_id); it != cache_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    [[nodiscard]] size_t size() const {
        std::shared_lock lock(mutex_);
        return cache_.size();
    }

private:
    mutable std::shared_mutex mutex_;
    std::unordered_map<uint32_t, std::string> cache_;
};

/* Серіалізація повідомлення у Confluent Wire Format (std::span) */
[[nodiscard]] std::vector<uint8_t> encode(uint32_t schema_id, std::span<const uint8_t> payload) {
    std::vector<uint8_t> buffer;
    buffer.reserve(HEADER_SIZE + payload.size());

    // Байт 0: Magic byte
    buffer.push_back(MAGIC_BYTE);

    // Байти 1–4: Schema ID у Big-Endian форматі
    buffer.push_back(static_cast<uint8_t>((schema_id >> 24) & 0xFF));
    buffer.push_back(static_cast<uint8_t>((schema_id >> 16) & 0xFF));
    buffer.push_back(static_cast<uint8_t>((schema_id >> 8) & 0xFF));
    buffer.push_back(static_cast<uint8_t>(schema_id & 0xFF));

    // Тіло повідомлення
    buffer.insert(buffer.end(), payload.begin(), payload.end());
    return buffer;
}

struct ParsedFrame {
    uint32_t schema_id;
    std::span<const uint8_t> payload;
};

/* Декодування та витягнення ідентифікатора схеми без додаткового виділення пам'яті */
[[nodiscard]] std::optional<ParsedFrame> decode(std::span<const uint8_t> frame) noexcept {
    if (frame.size() < HEADER_SIZE || frame[0] != MAGIC_BYTE) {
        return std::nullopt;
    }

    uint32_t schema_id = (static_cast<uint32_t>(frame[1]) << 24) |
                         (static_cast<uint32_t>(frame[2]) << 16) |
                         (static_cast<uint32_t>(frame[3]) << 8)  |
                         (static_cast<uint32_t>(frame[4]));

    return ParsedFrame{
        .schema_id = schema_id,
        .payload = frame.subspan(HEADER_SIZE)
    };
}

} // namespace schema_wire
```
:::

---

## 2. Алгоритмічний валідатор сумісності схем (Compatibility Checker)

Валідатор порівнює дві структури даних: схему старої версії писаря (Writer Schema) та схему нової версії читача (Reader Schema).

### 2.1. Поглиблений аналіз правил сумісності
Розгляньмо, як алгоритм обробляє критичні сценарії еволюції:

1. **Інваріант нових полів (New Field Invariant):**
   * Коли споживач оновлюється на нову схему (режим `BACKWARD`), у черзі все ще знаходяться старі повідомлення.
   * Оскільки стара схема писаря не містила цього поля, у бінарному тілі повідомлення немає відповідних байтів.
   * Якщо нове поле має `has_default == false`, десеріалізатор не зможе ініціалізувати поле об'єкта і кине виняток. Тому наявність значення за замовчуванням є обов'язковою умовою для нових полів.

2. **Граф безпечного розширення числових типів (Type Widening Graph):**
   * Перетворення `Int32 → Int64`: Безпечне, оскільки будь-яке 32-бітне ціле значення гарантовано вміщується у 64-бітне без втрати точності чи зміни знаку.
   * Перетворення `Int64 → Int32`: Небезпечне і блокується валідатором. Якщо продюсер запише велике число (наприклад, `5 000 000 000`), спроба помістити його в 32-бітний тип призведе до переповнення розрядної сітки та спотворення даних.
   * Перетворення між несумісними класами (наприклад, `String ↔ Int32` або `Boolean ↔ Int64`): Суворо заборонене, оскільки двійкове представлення рядків і чисел кардинально різниться.

3. **Правило видалення полів (Field Deletion Rule):**
   * У режимі `BACKWARD` видалення поля зі схеми читача є цілком безпечним: бібліотека Avro вичитує довжину невідомого поля зі схеми писаря і просто пропускає відповідні байти в потоці.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    TYPE_INT32,
    TYPE_INT64,
    TYPE_STRING,
    TYPE_BOOLEAN
} FieldType;

typedef struct {
    char name[64];
    FieldType type;
    bool has_default;
} SchemaField;

typedef struct {
    SchemaField fields[32];
    size_t field_count;
} RecordSchema;

bool is_type_compatible(FieldType old_t, FieldType new_t) {
    if (old_t == new_t) return true;
    /* Дозволене розширення числових типів: 32-бітний int безпечно читається як 64-бітний long */
    if (old_t == TYPE_INT32 && new_t == TYPE_INT64) return true;
    return false;
}

const SchemaField* find_field(const RecordSchema *schema, const char *name) {
    for (size_t i = 0; i < schema->field_count; ++i) {
        if (strcmp(schema->fields[i].name, name) == 0) {
            return &schema->fields[i];
        }
    }
    return NULL;
}

/* Перевірка зворотної сумісності BACKWARD */
bool validate_backward_compatibility(const RecordSchema *old_schema, const RecordSchema *new_schema, char *error_buf, size_t err_len) {
    for (size_t i = 0; i < new_schema->field_count; ++i) {
        const SchemaField *new_f = &new_schema->fields[i];
        const SchemaField *old_f = find_field(old_schema, new_f->name);

        if (old_f == NULL) {
            /* Поле нове: зобов'язане мати default для старих повідомлень */
            if (!new_f->has_default) {
                snprintf(error_buf, err_len, "Нове поле '%s' не має значення за замовчуванням", new_f->name);
                return false;
            }
        } else {
            /* Поле існувало: перевірка сумісності типів */
            if (!is_type_compatible(old_f->type, new_f->type)) {
                snprintf(error_buf, err_len, "Несумісна зміна типу для поля '%s'", new_f->name);
                return false;
            }
        }
    }
    return true;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <optional>
#include <expected>

namespace schema_validator {

enum class DataType {
    Int32,
    Int64,
    String,
    Boolean
};

struct Field {
    std::string name;
    DataType type;
    bool has_default{false};
    std::optional<std::string> default_value{std::nullopt};
};

struct RecordSchema {
    std::string record_name;
    std::vector<Field> fields;

    [[nodiscard]] const Field* find_field(std::string_view name) const noexcept {
        for (const auto& field : fields) {
            if (field.name == name) return &field;
        }
        return nullptr;
    }
};

class SchemaCompatibilityEngine {
public:
    [[nodiscard]] static bool is_type_widening_allowed(DataType writer_type, DataType reader_type) noexcept {
        if (writer_type == reader_type) return true;
        // 32-бітне ціле число безпечно розширюється до 64-бітного
        if (writer_type == DataType::Int32 && reader_type == DataType::Int64) return true;
        return false;
    }

    /* Перевірка BACKWARD: Reader(new) може прочитати дані Writer(old) */
    [[nodiscard]] static std::expected<void, std::string> check_backward(
        const RecordSchema& old_writer,
        const RecordSchema& new_reader) {

        for (const auto& r_field : new_reader.fields) {
            const auto* w_field = old_writer.find_field(r_field.name);
            if (!w_field) {
                // Нове поле обов'язково повинно мати значення за замовчуванням
                if (!r_field.has_default) {
                    return std::unexpected(
                        "Помилка сумісності BACKWARD: Нове поле '" + r_field.name +
                        "' відсутнє у старій схемі та не має значення за замовчуванням."
                    );
                }
            } else {
                // Перевірка сумісності типу даних
                if (!is_type_widening_allowed(w_field->type, r_field->type)) {
                    return std::unexpected(
                        "Помилка сумісності BACKWARD: Поле '" + r_field.name +
                        "' має несумісну зміну типу даних."
                    );
                }
            }
        }
        return {};
    }

    /* Перевірка FORWARD: Reader(old) може прочитати дані Writer(new) */
    [[nodiscard]] static std::expected<void, std::string> check_forward(
        const RecordSchema& old_reader,
        const RecordSchema& new_writer) {
        // Пряма сумісність еквівалентна зворотній з обміном ролей читача й писаря
        return check_backward(new_writer, old_reader);
    }

    /* Перевірка FULL: Двостороння сумісність */
    [[nodiscard]] static std::expected<void, std::string> check_full(
        const RecordSchema& old_schema,
        const RecordSchema& new_schema) {

        if (auto res = check_backward(old_schema, new_schema); !res) {
            return res;
        }
        return check_forward(old_schema, new_schema);
    }
};

} // namespace schema_validator
```
:::

---

## 3. Демонстраційний тестовий стенд: перевірка кадрування та виявлення помилок

Для перевірки коректності роботи кодувальника та алгоритму валідації сумісності побудуємо повний тестовий стенд.

Стенд перевіряє три ключові сценарії:
1. **Коректність упаковки та розпаковки двійкового кадру:** Перевірка того, що магічний байт `0x00` зберігається на нульовій позиції, числовий `Schema ID: 42` успішно кодується й декодується через Big-Endian зсуви, а сире корисне навантаження передається без спотворень.
2. **Успішне схвалення валідної еволюції схеми:** Додавання необов'язкового поля `currency` з дефолтним значенням `"EUR"` та розширення типу суми з `int32` до `int64`. Валідатор зобов'язаний повернути позитивний результат.
3. **Перехоплення деструктивної зміни контракту:** Додавання обов'язкового поля `fraud_score` без значення за замовчуванням. Валідатор зобов'язаний виявити порушення інваріанту та повернути структуровану помилку із зазначенням проблемного поля.

:::tabs
```c
int main(void) {
    printf("=== ТЕСТ 1: Перевірка кадрування Wire Format ===\n");
    uint32_t original_schema_id = 42;
    const uint8_t raw_data[] = {0xDE, 0xAD, 0xBE, 0xEF};
    size_t encoded_len = 0;

    uint8_t *frame = wire_encode(original_schema_id, raw_data, sizeof(raw_data), &encoded_len);
    printf("Закодовано кадр довжиною: %zu байтів\n", encoded_len);

    uint32_t decoded_schema_id = 0;
    const uint8_t *decoded_payload = NULL;
    size_t decoded_payload_len = 0;

    if (wire_decode(frame, encoded_len, &decoded_schema_id, &decoded_payload, &decoded_payload_len)) {
        printf("✓ Успішне декодування: Schema ID = %u, Payload Len = %zu\n", decoded_schema_id, decoded_payload_len);
    } else {
        printf("✗ Помилка декодування кадру!\n");
    }
    free(frame);

    printf("\n=== ТЕСТ 2: Перевірка валідатора сумісності ===\n");
    RecordSchema v1 = {
        .fields = {
            {"order_id", TYPE_INT64, false},
            {"amount_cents", TYPE_INT32, false}
        },
        .field_count = 2
    };

    /* Схема V2 з валідною зміною: розширення типу та нове поле з дефолтом */
    RecordSchema v2_valid = {
        .fields = {
            {"order_id", TYPE_INT64, false},
            {"amount_cents", TYPE_INT64, false}, // int32 -> int64 (OK)
            {"currency", TYPE_STRING, true}      // нове поле з дефолтом (OK)
        },
        .field_count = 3
    };

    char err_buf[256];
    if (validate_backward_compatibility(&v1, &v2_valid, err_buf, sizeof(err_buf))) {
        printf("✓ Схема V2 визнана повністю сумісною (BACKWARD)\n");
    } else {
        printf("✗ Помилка валідації: %s\n", err_buf);
    }

    /* Схема V3 з небезпечною зміною: нове поле без дефолту */
    RecordSchema v3_broken = {
        .fields = {
            {"order_id", TYPE_INT64, false},
            {"amount_cents", TYPE_INT32, false},
            {"mandatory_tax_code", TYPE_STRING, false} // НЕМАЄ ДЕФОЛТУ!
        },
        .field_count = 3
    };

    if (!validate_backward_compatibility(&v1, &v3_broken, err_buf, sizeof(err_buf))) {
        printf("✓ Валідатор успішно заблокував дефектну схему: %s\n", err_buf);
    } else {
        printf("✗ Помилка: валідатор пропустив небезпечну схему!\n");
    }

    return 0;
}
```
```cpp
int main() {
    using namespace schema_wire;
    using namespace schema_validator;

    std::cout << "=== ТЕСТ 1: C++ Wire Framing та потокобезпечний кеш ===\n";
    ThreadSafeSchemaCache cache;
    cache.put(42, R"({"type":"record","name":"Order","fields":[{"name":"id","type":"long"}]})");

    std::vector<uint8_t> payload = {0xCA, 0xFE, 0xBA, 0xBE};
    auto encoded_frame = encode(42, payload);
    std::cout << "Розмір кадру: " << encoded_frame.size() << " байтів (оверхед = 5 байтів)\n";

    auto parsed = decode(encoded_frame);
    if (parsed) {
        std::cout << "✓ Розпарсено ID: " << parsed->schema_id << "\n";
        auto schema = cache.get(parsed->schema_id);
        if (schema) {
            std::cout << "✓ Схему знайдено в локальному RAM-кеші: " << *schema << "\n";
        }
    }

    std::cout << "\n=== ТЕСТ 2: C++ Валідатор еволюції схем ===\n";
    RecordSchema old_v1{
        .record_name = "OrderPlaced",
        .fields = {
            Field{.name = "order_id", .type = DataType::Int64, .has_default = false},
            Field{.name = "amount", .type = DataType::Int32, .has_default = false}
        }
    };

    RecordSchema new_v2_ok{
        .record_name = "OrderPlaced",
        .fields = {
            Field{.name = "order_id", .type = DataType::Int64, .has_default = false},
            Field{.name = "amount", .type = DataType::Int64, .has_default = false}, // Розширення типу
            Field{.name = "currency", .type = DataType::String, .has_default = true, .default_value = "EUR"}
        }
    };

    auto res_ok = SchemaCompatibilityEngine::check_backward(old_v1, new_v2_ok);
    if (res_ok) {
        std::cout << "✓ Валідація BACKWARD успішна для сумісної схеми V2.\n";
    }

    RecordSchema new_v3_bad{
        .record_name = "OrderPlaced",
        .fields = {
            Field{.name = "order_id", .type = DataType::Int64, .has_default = false},
            Field{.name = "amount", .type = DataType::Int32, .has_default = false},
            Field{.name = "fraud_score", .type = DataType::Int32, .has_default = false} // Обов'язкове поле без дефолту!
        }
    };

    auto res_bad = SchemaCompatibilityEngine::check_backward(old_v1, new_v3_bad);
    if (!res_bad) {
        std::cout << "✓ Перевірка перехопила порушення контракту:\n  " << res_bad.error() << "\n";
    }

    return 0;
}
```
:::

---

## 4. Автоматизація перевірки в CI/CD пайплайні (GitHub Actions)

Покладатися виключно на те, що продюсер отримає помилку `409 Conflict` під час розгортання в продакшені — небезпечно, оскільки це блокує процес викатки релізу в останній момент і змушує команду терміново шукати причину збою.

Інженерна практика вимагає перенесення перевірки сумісності на етап розробки — у фазу Pull Request. Спеціальний крок CI-пайплайну знаходить усі змінені файли схем (`schemas/*.avsc` або `schemas/*.proto`) і виконує запит у режимі `dry-run` до тестового реєстру схем.

Якщо хоча б один файл порушує сумісність із відповідним суб'єктом, білд завершується з ненульовим кодом повернення (`exit 1`), а розробник отримує точний список несумісних полів прямо в коментарях до пулл-реквесту.

```yaml
name: Schema Compatibility Gate

on:
  pull_request:
    paths:
      - 'schemas/**'

jobs:
  validate-schema-compatibility:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Execute Compatibility Dry-Run
        env:
          REGISTRY_URL: "https://schema-registry.internal.example.com"
        run: |
          set -e
          for schema_path in schemas/*.avsc; do
            subject_name="$(basename "$schema_path" .avsc)-value"
            echo "Перевірка сумісності контракту для суб'єкта: $subject_name"
            
            # Екранування JSON-структури схеми для передачі у тілі HTTP-запиту
            SCHEMA_BODY=$(jq -Rs '.' < "$schema_path")
            PAYLOAD=$(printf '{"schema": %s, "schemaType": "AVRO"}' "$SCHEMA_BODY")
            
            # Виклик endpoint валідації сумісності
            RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
              -H "Content-Type: application/vnd.schemaregistry.v1+json" \
              --data "$PAYLOAD" \
              "$REGISTRY_URL/compatibility/subjects/$subject_name/versions/latest")
            
            HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
            BODY=$(echo "$RESPONSE" | sed '$d')
            
            if [ "$HTTP_CODE" -ne 200 ]; then
              echo "❌ ПОМИЛКА: Мережевий запит до реєстру завершився зі статусом $HTTP_CODE"
              echo "$BODY"
              exit 1
            fi
            
            IS_COMPATIBLE=$(echo "$BODY" | jq -r '.is_compatible')
            
            if [ "$IS_COMPATIBLE" != "true" ]; then
              echo "❌ ВІДХИЛЕНО: Схема $schema_path ламає сумісність із суб'єктом $subject_name!"
              echo "Деталі відхилення: $BODY"
              exit 1
            fi
            
            echo "✅ Схема $schema_path успішно пройшла перевірку сумісності."
          done
```

Такий підхід забезпечує **зсув контролю якості ліворуч** (англ. *Shift-Left Quality Assurance*): дефекти контрактів виявляються за хвилини під час компіляції та перевірки PR, повністю усуваючи ризик потрапляння отруєних повідомлень у робочий журнал подій.

---

## 5. Профілювання продуктивності та навантажувальний аналіз

Для оцінки ефективності локального кешування проведемо аналіз накладних витрат у високопродуктивному середовищі:

### 5.1. Затримка доступу: пам'ять процесу проти мережевого виклику
* **Прямий мережевий виклик до реєстру схем через HTTP:**
  * Затримка (RTT в одній зоні доступності): ~1.2–3.5 мілісекунди.
  * Витрати CPU: контекстні перемикання операційної системи, парсинг HTTP-заголовків, виділення сокетних буферів.
  * Максимальна пропускна здатність на одне ядро: ~300–800 повідомлень на секунду.
* **Зчитування з потокобезпечного локального кешу (RAM Cache Hit):**
  * Затримка (L3 Cache / RAM lookup): ~14–22 наносекунди (приблизно у 100 000 разів швидше за мережу).
  * Витрати CPU: одне атомарне інкрементування лічильника `std::shared_lock` та пошук у хеш-таблиці.
  * Максимальна пропускна здатність на одне ядро: понад 2 500 000 повідомлень на секунду.

### 5.2. Витрати оперативної пам'яті (Memory Footprint)
Один розпарсений JSON-опис схеми середньої складності (15 полів із вкладеними структурами) займає в купі близько 2.5 КБ пам'яті.
* Для системи, яка працює зі 100 різними топіками та підтримує до 10 активних історичних версій у кожному, загальний обсяг кешу становить:
  ```
  100 топіків × 10 версій × 2.5 КБ ≈ 2.5 МБ
  ```
* Такий обсяг повністю вміщується у спільний кеш L3 сучасного серверного процесора (який становить від 32 до 256 МБ), що гарантує відсутність промахів кешу пам'яті (англ. *cache thrashing*) під час постійного циклу вичитування повідомлень.

---

## 6. Обробка крайових випадків та відмовостійкість клієнта

У реальному продакшені клієнтський серіалізатор стикається з нештатними ситуаціями, які вимагають детермінованої обробки:

### 6.1. Урізані кадри та захист від переповнення буфера (Truncated Frames)
Якщо брокер повертає пошкоджений або обрізаний масив байтів довжиною менше 5 байтів, виклик `wire_decode` негайно повертає помилку `false` ще до спроби прочитати байти ідентифікатора. Це запобігає виходу за межі пам'яті (англ. *out-of-bounds memory read* / *segmentation fault*).

### 6.2. Поведінка під час недоступності реєстру схем при холодному старті
Якщо новий под споживача запускається під час планового перезапуску або тимчасового падіння кластера реєстру схем:
* Клієнтська бібліотека не повинна падати аварійно після першої помилки.
* Серіалізатор застосовує стратегію повторних спроб із експоненційним відступом та випадковим джитером (англ. *Exponential Backoff with Jitter*), наприклад: 100мс, 200мс, 400мс, 800мс.
* Якщо реєстр не відповідає довше встановленого таймауту (наприклад, 10 секунд), споживач призупиняє вичитування з партиції (англ. *Kafka Consumer pause*), щоб запобігти каскадному накопиченню помилок у Dead Letter Queue.

### 6.3. Чому кеш ідентифікаторів не потребує інвалідації (TTL)
На відміну від звичайних кешів даних, де значення в базі можуть оновлюватися і вимагають інвалідації за часом (TTL), зв'язка `Schema ID ↔ Schema Definition` у реєстрі є **математично незмінною (Immutable)**.

Одного разу призначений `Schema ID: 42` назавжди закріплений за конкретним відбитком структури. Навіть якщо команда оновить схему топіка до версії 3, нова версія отримає новий унікальний `Schema ID: 43`. Старі повідомлення з `ID: 42` завжди десеріалізуватимуться за старою схемою, тому локальний кеш клієнта може зберігати дані безстроково без ризику застарівання.

---

## 7. Архітектура нульового копіювання (Zero-Copy Processing з `std::span`)

У високонавантажених C++ сервісах критично уникати копіювання пам'яті під час проходження повідомлення крізь сокетний рівень.

Традиційний підхід вимагає копіювання вхідного буфера:
1. Зчитування кадру з сокета в буфер ядра TCP.
2. Копіювання в буфер користувацького простору (`std::vector<uint8_t>`).
3. Виділення окремого підрядка чи підмасиву для корисного навантаження (`sub-vector` або новий `std::string`).

Використання `std::span<const uint8_t>` у C++20 усуває третій крок:
* Структура `ParsedFrame` не виділяє жодного байта в динамічній пам'яті (Heap).
* Вона містить лише 64-бітний вказівник на початок корисного навантаження `buffer + 5` та 64-бітний лічильник довжини `buffer_len - 5`.
* Десеріалізатор Avro/Protobuf парсить байти безпосередньо з оригінального буфера мережевого драйвера. На обсязі в один мільйон повідомлень на секунду це усуває гігабайти марних алокацій пам'яті та повністю позбавляє збирач сміття від навантаження.

---

## 8. Дисципліна обробки аномалій та захисний чекліст

Під час експлуатації клієнтських серіалізаторів інженери дотримуються чіткого операційного протоколу:

| Симптом або збій | Першопричина | Інженерне рішення та дія |
|---|---|---|
| Помилка `Magic byte mismatch: 0x7B` | Продюсер надіслав сирий JSON (`0x7B` — символ `{`) замість Wire Format | Маршрутизація в DLQ; перевірка налаштувань конфігурації серіалізатора продюсера. |
| Помилка `Schema ID 40403 not found` | Схема була зареєстрована у тестовому реєстрі, а повідомлення відправлено в прод-брокер | Увімкнення експортерів схем або централізованого CI/CD пайплайну реєстрації. |
| Різке зростання затримок десеріалізації (p99) | Холодний старт кількох сотень подів споживачів, що спричинив шторм запитів до реєстру | Прогрів локального кешу при ініціалізації контейнера або горизонтальне масштабування реєстру. |
| Збій валідації `Incompatible Schema (409)` | Спроба додати обов'язкове поле без значення за замовчуванням | Додавання атрибута `default` або перехід до стратегії багатоетапної міграції (Expand/Contract). |

---

## 9. Покроковий регламент усунення збоїв у CI (Troubleshooting Runbook)

Коли крок перевірки `Schema Compatibility Gate` у Pull Request завершується помилкою, інженер виконує наступну послідовність дій для відновлення сумісності:

1. **Аналіз JSON Pointer у звіті валідатора:**
   * Лог містить точне поле: наприклад, `Path: '/fields/2/default': Missing default value for newly added field 'discount_rate'`.
2. **Вибір стратегії виправлення:**
   * **Сценарій А (Адитивна еволюція):** Якщо поле можна зробити необов'язковим, до опису поля у файлі `.avsc` додається `"default": 0.0` або тип загортається в об'єднання `["null", "double"]` із дефолтом `null`.
   * **Сценарій Б (Перейменування поля):** Замість прямої заміни імені поля `old_name → new_name`, старе ім'я зберігається в масиві псевдонімів `"aliases": ["old_name"]`. Це дозволяє новим споживачам прозоро читати старі повідомлення.
   * **Сценарій В (Кардинальна зміна бізнес-моделі):** Якщо зміна є принципово несумісною (наприклад, зміна типу ключового ідентифікатора з `long` на складний об'єкт `UUID`), перехід здійснюється через створення нового суб'єкта та нового топіка (наприклад, `orders.v2`). Старий та новий топіки функціонують паралельно за шаблоном подвійного запису (Dual Writing) до повного виведення з експлуатації старих споживачів.

---

## 10. Порівняльний аналіз та реалізація стратегій іменування суб'єктів

Під час конструювання клієнтського драйвера вибір способу формування назви суб'єкта визначає ступінь ізоляції подій у чергах:

1. **`TopicNameStrategy` (за замовчуванням):**
   * *Формула:* `<topic-name>-value` (або `<topic-name>-key`).
   * *Коли використовувати:* Ідеально підходить для потокової аналітики (Kafka Streams, Apache Flink), де кожна партиція топіка містить суворо однорідний потік подій одного типу.
   * *Обмеження:* Неможливо опублікувати різні структури даних в один топік без порушення сумісності.
2. **`RecordNameStrategy`:**
   * *Формула:* `<namespace>.<RecordName>`.
   * *Коли використовувати:* Підходить для DDD-архітектури (Domain-Driven Design), де агрегат публікує кілька споріднених типів подій (наприклад, `OrderCreated`, `OrderCancelled`, `PaymentReceived`) у спільний бізнес-топік `orders-lifecycle`. Сумісність перевіряється окремо для кожного класу подій незалежно від імені черги.
3. **`TopicRecordNameStrategy`:**
   * *Формула:* `<topic-name>-<namespace>.<RecordName>`.
   * *Коли використовувати:* Забезпечує максимальну ізоляцію в мультитенантних середовищах: однаковий тип події може мати різну швидкість еволюції в різних топіках (наприклад, `staging-orders-OrderCreated` та `prod-orders-OrderCreated`).

---

## 11. Оптимізація виділення пам'яті: кільцеві буфери та арени (Ring Buffer Arena)

У сервісах із пропускною здатністю понад 500 000 RPS стандартні системні виклики `malloc` та `free` на кожному повідомленні призводять до фрагментації оперативної пам'яті та конкуренції за глобальний heap lock.

Для досягнення максимальної продуктивності клієнтські драйвери використовують пули заздалегідь виділеної пам'яті (англ. *Memory Arena*):
* **Арена для продюсера:** Потік серіалізації виділяє фіксований кільцевий буфер розміром 16 МБ при старті процесу. Кожен новий бінарний кадр записується за локальним атомарним зміщенням без виклику системного алокатора. Коли буфер заповнюється, вказівник циклічно повертається на початок після підтвердження відправлення пачки повідомлень (Acks).
* **Стек тимчасових об'єктів для десеріалізатора:** Усі двійкові структури читача ініціалізуються на локальному стеку потоку (`alloca` або стек-буфер фіксованого розміру). Якщо розмір повідомлення не перевищує 64 КБ (що охоплює 99.9% бізнес-подій), виділення в купі взагалі не відбувається. Це забезпечує передбачувану затримку та виключає будь-яку деградацію продуктивності під час пікових сплесків навантаження.

---

## 12. Підсумкові інженерні висновки

Розділення взаємодії з реєстром схем на автономний In-Memory Data Plane та автоматизований CI Control Plane вирішує фундаментальну проблему розподілених систем:
* **Нульовий вплив на затримку:** Серіалізація та десеріалізація з локального RAM-кешу додають менше ніж 20 наносекунд до загального часу обробки події.
* **Математичний захист журналів:** Жодна деструктивна зміна контракту не може пройти крізь автоматичні ворота валідації, гарантуючи довготривалу стабільність і надійність сервісів підприємства.
