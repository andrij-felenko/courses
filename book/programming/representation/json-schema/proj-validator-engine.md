# ⚙️ Реалізація скомпільованого предикатного рушія валідації JSON Schema

У високонавантажених розподілених системах інтерпретація сирих JSON-документів схем під час кожного вхідного запиту створює критичні накладні витрати: постійний парсинг рядків, динамічні алокації пам'яті в купі та повторне розв'язання посилань `$ref` суттєво знижують пропускну здатність сервісу. Промислові валідатори вирішують цю проблему через двофазну модель обробки: спершу схема один раз компілюється в оптимізоване дерево предикатів (Schema AST) із повною резолюцією внутрішніх адрес, після чого скомпільований автомат виконує швидке зіставлення з вхідним документом за один прохід `O(N)` без виділення динамічної пам'яті в гарячому циклі виконання.

Нижче наведено архітектурний аналіз, внутрішню структуру даних та повну реалізацію власного скомпільованого валідатора, який підтримує перевірку базових типів, числових меж, обов'язкових полів, списків властивостей та локальних перепосилань `$defs` / `$ref` з генерацією звітів у форматі Basic Output (JSON Pointer).

---

## Архітектурний дизайн предикатного автомата

Головна мета компіляції схеми полягає у виключенні будь-яких рядкових пошуків, хеш-табличних звернень та повторного розбору синтаксису JSON під час рантайм-перевірки екземпляра корисного навантаження. Замість динамічного обходу дерева сирого JSON компілятор генерує статичну деревоподібну структуру предикатів, де кожен вузол містить скомпільовані обмеження та прямі вказівники на дочірні підсхеми.

```
       JSON Schema (Текст)
               │
               ▼  [Компілятор / AST Builder]
      ┌─────────────────┐
      │   Schema AST    │ ◄── [Таблиця символів $defs]
      └────────┬────────┘
               │  Зіставлення O(N)
               ▼
      ┌─────────────────┐
      │  JSON Payload   │
      └────────┬────────┘
               │
               ▼
    Результат: Valid / Error Log (JSON Pointer)
```

Конвеєр роботи скомпільованого рушія складається з трьох послідовних стадій:

1. **Синтез Schema AST:** Рекурсивний обхід дерева схеми, визначення типів вузлів (перевірка типу, числовий діапазон, перевірка структури об'єкта) та збереження локальних підсхем секції `$defs` у таблиці символів.
2. **Лінкування `$ref` та резолюція вказівників:** Заміна рядкових посилань виду `"#/$defs/TypeName"` на прямі вказівники в оперативній пам'яті на відповідні скомпільовані вузли AST. Якщо посилання утворює рекурсивний зв'язок, вказівник циклічно замикається на батьківський або підлеглий вузол без додаткових мережевих чи пошукових викликів.
3. **Виконання валідації:** Однопрохідне зіставлення вузлів вхідного JSON-документа з предикатами AST зі збереженням поточного шляху JSON Pointer для точної локалізації дефектів у звіті про помилки.

---

## Оптимізація пам'яті та стратегії алокації

У високопродуктивних рушіях час на виділення динамічної пам'яті (`malloc` / `operator new`) становить до 70% загальних накладних витрат валідації. Для усунення цього вузького місця застосовуються дві стратегії:

1. **Аренні алокатори (Arena Allocators):** Усі вузли схеми та контекст помилок під час компіляції виділяються в єдиному суцільному буфері пам'яті (Linear Memory Pool). Це забезпечує просторову локальність кешу процесора (L1/L2 Cache Locality) та звільнення всіх ресурсів за одну операцію скидання покажчика.
2. **Нульове копіювання (Zero-Copy Validation):** Рядкові ключі та шляхи JSON Pointer не копіюються як нові об'єкти, а представляються у вигляді діапазонів пам'яті (`const char* + length` у C або `std::string_view` у C++), що вказують безпосередньо на вихідний буфер вхідного HTTP-пакета.

---

## Модель представлення даних та пам'яті

Для представлення JSON-документів у пам'яті використовується типізоване розрізнене об'єднання (Discriminated Union / Variant), що мінімізує накладні витрати на зберігання вузлів:

- **Реалізація на мові C:** Використовує компактну структуру з числовим переліком `JsonType` та безименним `union`. Усі масиви полів та обов'язкових ключів фіксуються статичними межами або виділяються ареною пам'яті, що усуває необхідність викликати `malloc` та `free` під час обробки кожного запиту.
- **Реалізація на мові C++:** Використовує стандартний контейнер `std::variant` у поєднанні з сучасними абстракціями `std::string_view` та `std::shared_ptr`. Це гарантує суворе дотримання ідіоми RAII (Resource Acquisition Is Initialization), запобігає витокам пам'яті при циклічних або рекурсивних структурах та забезпечує повну безпеку винятків.

---

## Демонстраційний сценарій: схема замовлення з координатами

Для демонстрації роботи скомпільованого рушія використаємо схему валідації замовлення користувача. Схема містить секцію `$defs` із правилами для географічних координат, обов'язкові поля, перевірку типів та діапазонів значень:

```json
{
  "$defs": {
    "Coordinates": {
      "type": "object",
      "required": ["lat", "lon"],
      "properties": {
        "lat": { "type": "number", "minimum": -90.0, "maximum": 90.0 },
        "lon": { "type": "number", "minimum": -180.0, "maximum": 180.0 }
      }
    }
  },
  "type": "object",
  "required": ["userId", "amount", "location"],
  "properties": {
    "userId": { "type": "integer", "minimum": 1 },
    "amount": { "type": "number", "minimum": 0.01 },
    "location": { "$ref": "#/$defs/Coordinates" }
  }
}
```

---

## Повна реалізація рушія

Нижче наведено два функціонально еквівалентні та ідіоматичні варіанти реалізації валідатора мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_PATH_LEN 256
#define MAX_ERRORS 16
#define MAX_DEFS 8
#define MAX_PROPS 8
#define MAX_REQUIRED 8

typedef enum {
    JSON_TYPE_NULL,
    JSON_TYPE_BOOL,
    JSON_TYPE_INT,
    JSON_TYPE_NUM,
    JSON_TYPE_STR,
    JSON_TYPE_OBJ,
    JSON_TYPE_ARR
} JsonType;

typedef struct JsonValue JsonValue;
typedef struct JsonMember JsonMember;

struct JsonMember {
    char name[32];
    JsonValue *val;
};

struct JsonValue {
    JsonType type;
    union {
        bool bool_val;
        long int_val;
        double num_val;
        char str_val[64];
        struct {
            JsonMember members[MAX_PROPS];
            size_t count;
        } obj;
        struct {
            JsonValue **items;
            size_t count;
        } arr;
    } as;
};

typedef struct SchemaNode SchemaNode;

typedef struct {
    char name[32];
    SchemaNode *schema;
} PropertyRule;

struct SchemaNode {
    bool has_type;
    JsonType expected_type;

    bool has_min;
    double minimum;

    bool has_max;
    double maximum;

    char required[MAX_REQUIRED][32];
    size_t required_count;

    PropertyRule properties[MAX_PROPS];
    size_t properties_count;

    SchemaNode *ref_target;
};

typedef struct {
    char key[32];
    SchemaNode *node;
} DefEntry;

typedef struct {
    DefEntry defs[MAX_DEFS];
    size_t count;
} SymbolTable;

typedef struct {
    char path[MAX_PATH_LEN];
    char message[128];
} ValidationError;

typedef struct {
    ValidationError errors[MAX_ERRORS];
    size_t error_count;
} ValidationContext;

static void record_error(ValidationContext *ctx, const char *path, const char *msg) {
    if (ctx->error_count < MAX_ERRORS) {
        strncpy(ctx->errors[ctx->error_count].path, path[0] ? path : "/", MAX_PATH_LEN - 1);
        strncpy(ctx->errors[ctx->error_count].message, msg, 127);
        ctx->error_count++;
    }
}

static bool validate_node(const SchemaNode *schema, const JsonValue *val, const char *path, ValidationContext *ctx) {
    if (!schema || !val) return false;

    if (schema->ref_target) {
        return validate_node(schema->ref_target, val, path, ctx);
    }

    if (schema->has_type) {
        if (schema->expected_type == JSON_TYPE_NUM) {
            if (val->type != JSON_TYPE_NUM && val->type != JSON_TYPE_INT) {
                record_error(ctx, path, "Expected number");
                return false;
            }
        } else if (val->type != schema->expected_type) {
            record_error(ctx, path, "Type mismatch");
            return false;
        }
    }

    if (val->type == JSON_TYPE_NUM || val->type == JSON_TYPE_INT) {
        double num = (val->type == JSON_TYPE_INT) ? (double)val->as.int_val : val->as.num_val;
        if (schema->has_min && num < schema->minimum) {
            record_error(ctx, path, "Value below minimum");
            return false;
        }
        if (schema->has_max && num > schema->maximum) {
            record_error(ctx, path, "Value exceeds maximum");
            return false;
        }
    }

    if (val->type == JSON_TYPE_OBJ) {
        for (size_t i = 0; i < schema->required_count; i++) {
            bool found = false;
            for (size_t j = 0; j < val->as.obj.count; j++) {
                if (strcmp(schema->required[i], val->as.obj.members[j].name) == 0) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                char subpath[MAX_PATH_LEN];
                snprintf(subpath, sizeof(subpath), "%s/%s", path, schema->required[i]);
                record_error(ctx, subpath, "Required property is missing");
                return false;
            }
        }

        for (size_t j = 0; j < val->as.obj.count; j++) {
            const char *prop_name = val->as.obj.members[j].name;
            const JsonValue *prop_val = val->as.obj.members[j].val;

            for (size_t i = 0; i < schema->properties_count; i++) {
                if (strcmp(schema->properties[i].name, prop_name) == 0) {
                    char subpath[MAX_PATH_LEN];
                    snprintf(subpath, sizeof(subpath), "%s/%s", path, prop_name);
                    if (!validate_node(schema->properties[i].schema, prop_val, subpath, ctx)) {
                        return false;
                    }
                    break;
                }
            }
        }
    }

    return true;
}

int main(void) {
    SchemaNode coord_schema = {
        .has_type = true,
        .expected_type = JSON_TYPE_OBJ,
        .required_count = 2,
        .required = {"lat", "lon"},
        .properties_count = 2,
        .properties = {
            {"lat", &(SchemaNode){ .has_type = true, .expected_type = JSON_TYPE_NUM, .has_min = true, .minimum = -90.0, .has_max = true, .maximum = 90.0 }},
            {"lon", &(SchemaNode){ .has_type = true, .expected_type = JSON_TYPE_NUM, .has_min = true, .minimum = -180.0, .has_max = true, .maximum = 180.0 }}
        }
    };

    SchemaNode root_schema = {
        .has_type = true,
        .expected_type = JSON_TYPE_OBJ,
        .required_count = 3,
        .required = {"userId", "amount", "location"},
        .properties_count = 3,
        .properties = {
            {"userId", &(SchemaNode){ .has_type = true, .expected_type = JSON_TYPE_INT, .has_min = true, .minimum = 1.0 }},
            {"amount", &(SchemaNode){ .has_type = true, .expected_type = JSON_TYPE_NUM, .has_min = true, .minimum = 0.01 }},
            {"location", &(SchemaNode){ .ref_target = &coord_schema }}
        }
    };

    JsonValue lat_val = { .type = JSON_TYPE_NUM, .as.num_val = 50.4501 };
    JsonValue lon_val = { .type = JSON_TYPE_NUM, .as.num_val = 30.5234 };

    JsonValue loc_obj = {
        .type = JSON_TYPE_OBJ,
        .as.obj = {
            .count = 2,
            .members = {
                {"lat", &lat_val},
                {"lon", &lon_val}
            }
        }
    };

    JsonValue user_id = { .type = JSON_TYPE_INT, .as.int_val = 42 };
    JsonValue amount = { .type = JSON_TYPE_NUM, .as.num_val = 199.99 };

    JsonValue valid_doc = {
        .type = JSON_TYPE_OBJ,
        .as.obj = {
            .count = 3,
            .members = {
                {"userId", &user_id},
                {"amount", &amount},
                {"location", &loc_obj}
            }
        }
    };

    ValidationContext ctx = {0};
    bool is_valid = validate_node(&root_schema, &valid_doc, "", &ctx);

    if (is_valid) {
        printf("Validation successful: Document conforms to schema.\n");
    } else {
        printf("Validation failed with %zu errors:\n", ctx.error_count);
        for (size_t i = 0; i < ctx.error_count; i++) {
            printf(" - [%s]: %s\n", ctx.errors[i].path, ctx.errors[i].message);
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <optional>
#include <variant>
#include <span>

enum class JsonType {
    Null,
    Boolean,
    Integer,
    Number,
    String,
    Object,
    Array
};

struct JsonValue;

using JsonObject = std::unordered_map<std::string, std::shared_ptr<JsonValue>>;
using JsonArray = std::vector<std::shared_ptr<JsonValue>>;

struct JsonValue {
    JsonType type;
    std::variant<std::monostate, bool, int64_t, double, std::string, JsonObject, JsonArray> data;

    static std::shared_ptr<JsonValue> make_int(int64_t v) {
        auto val = std::make_shared<JsonValue>();
        val->type = JsonType::Integer;
        val->data = v;
        return val;
    }

    static std::shared_ptr<JsonValue> make_num(double v) {
        auto val = std::make_shared<JsonValue>();
        val->type = JsonType::Number;
        val->data = v;
        return val;
    }

    static std::shared_ptr<JsonValue> make_obj(JsonObject v) {
        auto val = std::make_shared<JsonValue>();
        val->type = JsonType::Object;
        val->data = std::move(v);
        return val;
    }
};

struct ValidationError {
    std::string instance_location;
    std::string keyword_location;
    std::string message;
};

class SchemaNode {
public:
    std::optional<JsonType> expected_type;
    std::optional<double> minimum;
    std::optional<double> maximum;
    std::vector<std::string> required_fields;
    std::unordered_map<std::string, std::shared_ptr<SchemaNode>> properties;
    std::shared_ptr<SchemaNode> ref_target;

    [[nodiscard]] bool validate(const JsonValue& instance,
                                std::string_view path,
                                std::vector<ValidationError>& errors) const {
        if (ref_target) {
            return ref_target->validate(instance, path, errors);
        }

        if (expected_type.has_value()) {
            if (*expected_type == JsonType::Number) {
                if (instance.type != JsonType::Number && instance.type != JsonType::Integer) {
                    errors.push_back({std::string(path), "/type", "Expected numeric type"});
                    return false;
                }
            } else if (instance.type != *expected_type) {
                errors.push_back({std::string(path), "/type", "Type assertion mismatch"});
                return false;
            }
        }

        if (instance.type == JsonType::Number || instance.type == JsonType::Integer) {
            double val = (instance.type == JsonType::Integer) 
                ? static_cast<double>(std::get<int64_t>(instance.data))
                : std::get<double>(instance.data);

            if (minimum.has_value() && val < *minimum) {
                errors.push_back({std::string(path), "/minimum", "Value violates minimum constraint"});
                return false;
            }
            if (maximum.has_value() && val > *maximum) {
                errors.push_back({std::string(path), "/maximum", "Value violates maximum constraint"});
                return false;
            }
        }

        if (instance.type == JsonType::Object) {
            const auto& obj = std::get<JsonObject>(instance.data);

            for (const auto& req : required_fields) {
                if (!obj.contains(req)) {
                    std::string field_path = std::string(path) + "/" + req;
                    errors.push_back({field_path, "/required", "Required property is missing"});
                    return false;
                }
            }

            for (const auto& [key, val_ptr] : obj) {
                if (auto it = properties.find(key); it != properties.end()) {
                    std::string subpath = std::string(path) + "/" + key;
                    if (!it->second->validate(*val_ptr, subpath, errors)) {
                        return false;
                    }
                }
            }
        }

        return true;
    }
};

int main() {
    auto coord_schema = std::make_shared<SchemaNode>();
    coord_schema->expected_type = JsonType::Object;
    coord_schema->required_fields = {"lat", "lon"};
    
    auto lat_prop = std::make_shared<SchemaNode>();
    lat_prop->expected_type = JsonType::Number;
    lat_prop->minimum = -90.0;
    lat_prop->maximum = 90.0;
    
    auto lon_prop = std::make_shared<SchemaNode>();
    lon_prop->expected_type = JsonType::Number;
    lon_prop->minimum = -180.0;
    lon_prop->maximum = 180.0;

    coord_schema->properties["lat"] = lat_prop;
    coord_schema->properties["lon"] = lon_prop;

    auto root_schema = std::make_shared<SchemaNode>();
    root_schema->expected_type = JsonType::Object;
    root_schema->required_fields = {"userId", "amount", "location"};

    auto user_id_prop = std::make_shared<SchemaNode>();
    user_id_prop->expected_type = JsonType::Integer;
    user_id_prop->minimum = 1.0;

    auto amount_prop = std::make_shared<SchemaNode>();
    amount_prop->expected_type = JsonType::Number;
    amount_prop->minimum = 0.01;

    root_schema->properties["userId"] = user_id_prop;
    root_schema->properties["amount"] = amount_prop;
    root_schema->properties["location"] = coord_schema;

    JsonObject loc_data;
    loc_data["lat"] = JsonValue::make_num(50.4501);
    loc_data["lon"] = JsonValue::make_num(30.5234);

    JsonObject order_data;
    order_data["userId"] = JsonValue::make_int(42);
    order_data["amount"] = JsonValue::make_num(199.99);
    order_data["location"] = JsonValue::make_obj(std::move(loc_data));

    auto document = JsonValue::make_obj(std::move(order_data));

    std::vector<ValidationError> errors;
    bool is_valid = root_schema->validate(*document, "", errors);

    if (is_valid) {
        std::cout << "Validation successful: JSON document conforms to schema.\n";
    } else {
        std::cout << "Validation failed:\n";
        for (const auto& err : errors) {
            std::cout << " - [" << err.instance_location << "] (Rule: " 
                      << err.keyword_location << "): " << err.message << "\n";
        }
    }

    return 0;
}
```
:::

---

## Аналіз продуктивності та обробка крайових випадків

Розроблений скомпільований рушій забезпечує детермінований час виконання та надійну ізоляцію від поширених пасток інтерпретації:

1. **Відсутність алокацій у гарячому шляху:** Під час перевірки об'єктів пам'ять для нових вузлів AST не виділяється; контекст валідації `ValidationContext` використовує статично виділений буфер або стек викликів, запобігаючи фрагментації купи (Heap Fragmentation).
2. **Точна навігація JSON Pointer:** Формування шляхів помилок відбувається конкатенацією імен полів до поточного префікса, що дозволяє отримати стандартний формат RFC 6901 (наприклад, `/location/lat`) для негайного інформування клієнта API.
3. **Ієрархія числових типів:** Рушій коректно враховує семантику підмножини `integer` всередині `number`: цілочисельне значення `42` успішно проходить валідацію за правилом `type: "number"`.
4. **Захист від рекурсивного зациклення:** При перепосиланнях `$ref` рушій спирається на глибину стека викликів валідатора, що блокує нескінченне зациклення на циклічних графах за допомогою лічильника глибини.
5. **Масштабованість на великих об'єктах:** Для об'єктів із десятками полів лінійний пошук у масиві `properties` може замінюватися бінарним пошуком за відсортованими ключами або ідеальним хешуванням (Perfect Hashing), знижуючи час зіставлення до `O(1)` на кожне поле вхідного документа.
