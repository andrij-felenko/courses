# ⚙️ Реалізація представлення бітової карти NULL та паралельного 3VL-обчислювача

У промислових реляційних базах даних (зокрема PostgreSQL та MySQL InnoDB) наявність значення `NULL` у колонці позначається не окремим байтом чи магічним числом у тілі кортежу, а бітом у бітовій карті (Null Bitmap) заголовка рядка. Якщо біт встановлено в `1` (або `0` залежно від рушія), значення присутнє, і зсув до наступного атрибута обчислюється зі схеми. Якщо біт сигналізує про `NULL`, розмір корисних даних для цієї колонки становить рівно нуль байтів.

Така фізична організація пам'яті вирішує дві ключові інженерні задачі:
1. **Мінімізація розміру дискової сторінки:** розріджені рядки з великою кількістю порожніх полів не витрачають дисковий простір та пропускну здатність шини пам'яті на зберігання фіктивних нулів чи порожніх структур.
2. **Швидка перевірка наявності:** замість складного розбору формату даних процесор виконує бітову інструкцію `TEST` або побітове `AND` над маскою заголовка кортежу, миттєво визначаючи валідність атрибута без звернення до невирівняної пам'яті корисного навантаження.

Нижче наведено практичну реалізацію низькорівневого сховища кортежів із бітовою картою та векторного обчислювача тризначної логіки (3VL) мовами C та C++.

## Представлення кортежу з бітовою картою NULL

У цій моделі кожен кортеж складається з фіксованого заголовка, який містить 32-бітну бітову маску наявності атрибутів (`null_bitmap`), лічильник розміру корисного навантаження (`payload_size`) та вказівник на динамічний неперервний буфер корисних байтів (`payload`).

Якщо колонка містить дійсне значення (наприклад, 4-байтне ціле число `int32_t`), відповідний біт маски встановлюється в `1`, а самі 4 байти дописуються в кінець буфера корисного навантаження. Якщо значення відсутнє (`NULL`), відповідний біт скидається в `0`, а буфер даних залишається незмінним. Доступ до потрібної колонки здійснюється шляхом динамічного обчислення байтового зсуву в буфері: підсумовуються розміри лише тих колонок, біти яких у бітовій карті встановлені в `1`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_COLUMNS 32

typedef enum {
    TYPE_INT32,
    TYPE_FLOAT64
} ColumnType;

typedef struct {
    uint16_t num_columns;
    ColumnType types[MAX_COLUMNS];
} TableSchema;

/* Кортеж: заголовок з бітовою картою та динамічний масив корисних байтів */
typedef struct {
    uint32_t null_bitmap; /* 1 = NOT NULL, 0 = IS NULL */
    uint16_t payload_size;
    uint8_t* payload;
} Tuple;

void tuple_init(Tuple* t) {
    t->null_bitmap = 0;
    t->payload_size = 0;
    t->payload = NULL;
}

void tuple_free(Tuple* t) {
    if (t->payload) {
        free(t->payload);
        t->payload = NULL;
    }
    t->payload_size = 0;
    t->null_bitmap = 0;
}

bool tuple_set_int32(Tuple* t, uint16_t col_idx, int32_t val) {
    if (col_idx >= MAX_COLUMNS) return false;
    
    /* Виділяємо додаткові 4 байти під int32 */
    uint8_t* new_payload = (uint8_t*)realloc(t->payload, t->payload_size + sizeof(int32_t));
    if (!new_payload) return false;
    
    t->payload = new_payload;
    memcpy(t->payload + t->payload_size, &val, sizeof(int32_t));
    t->payload_size += sizeof(int32_t);
    
    /* Встановлюємо біт присутності */
    t->null_bitmap |= (1U << col_idx);
    return true;
}

void tuple_set_null(Tuple* t, uint16_t col_idx) {
    if (col_idx < MAX_COLUMNS) {
        /* Скидаємо біт присутності; корисні дані не виділяються */
        t->null_bitmap &= ~(1U << col_idx);
    }
}

bool tuple_is_null(const Tuple* t, uint16_t col_idx) {
    return !(t->null_bitmap & (1U << col_idx));
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <optional>
#include <variant>
#include <span>
#include <cstring>

enum class ColumnType {
    Int32,
    Float64
};

struct TableSchema {
    std::vector<ColumnType> types;
};

/* Ідіоматичний C++ кортеж із RAII-управлінням пам'яттю */
class Tuple {
public:
    Tuple() : null_bitmap_(0) {}

    void set_null(uint16_t col_idx) noexcept {
        null_bitmap_ &= ~(1U << col_idx);
    }

    void set_int32(uint16_t col_idx, int32_t val) {
        null_bitmap_ |= (1U << col_idx);
        const auto* src = reinterpret_cast<const uint8_t*>(&val);
        payload_.insert(payload_.end(), src, src + sizeof(int32_t));
    }

    [[nodiscard]] bool is_null(uint16_t col_idx) const noexcept {
        return !(null_bitmap_ & (1U << col_idx));
    }

    [[nodiscard]] std::optional<int32_t> get_int32(uint16_t col_idx, const TableSchema& schema) const noexcept {
        if (is_null(col_idx)) {
            return std::nullopt;
        }

        size_t offset = 0;
        for (uint16_t i = 0; i < col_idx; ++i) {
            if (!is_null(i)) {
                if (schema.types[i] == ColumnType::Int32) offset += sizeof(int32_t);
                else if (schema.types[i] == ColumnType::Float64) offset += sizeof(double);
            }
        }

        int32_t result = 0;
        std::memcpy(&result, payload_.data() + offset, sizeof(int32_t));
        return result;
    }

private:
    uint32_t null_bitmap_{0}; /* 1 = NOT NULL, 0 = IS NULL */
    std::vector<uint8_t> payload_;
};
```
:::

## Векторний обчислювач тризначної логіки (3VL)

Під час виконання аналітичних SQL-запитів над великими масивами даних (OLAP) класичне розгалуження через умовні інструкції `if (is_null)` призводить до масових промахів блоку передбачення переходів сучасних процесорів (branch misprediction penalty). Кожен такий промах скидає конвеєр команд процесора і коштує від 15 до 20 тактів.

Щоб усунути умовні переходи, аналітичні рушії використовують **безрозгалужувальне векторне кодування** (branchless evaluation). Кожен тризначний стан кодується парою бітових масок:
1. `val`: булеве значення результату (0 або 1).
2. `is_known`: прапорець достовірності (1 якщо результат строго визначений, 0 якщо результат `UNKNOWN`).

У такій структурі логічні зв'язки обчислюються за допомогою простих комбінацій побітових операцій, які процесор здатний виконувати паралельно над пакетами з сотень кортежів за допомогою інструкцій SIMD.

:::tabs
```c
/* Кодування 3VL:
   TRI_FALSE:   val=0, is_known=1
   TRI_TRUE:    val=1, is_known=1
   TRI_UNKNOWN: val=0, is_known=0
*/
typedef struct {
    uint8_t val;      /* 0 або 1 */
    uint8_t is_known; /* 1 - визначено, 0 - UNKNOWN */
} TriBool;

TriBool tri_make_bool(bool b) {
    TriBool res = { (uint8_t)(b ? 1 : 0), 1 };
    return res;
}

TriBool tri_make_unknown(void) {
    TriBool res = { 0, 0 };
    return res;
}

TriBool tri_and(TriBool a, TriBool b) {
    TriBool res;
    /* Якщо хоча б один FALSE (val=0, is_known=1) -> результат FALSE */
    if ((a.is_known && a.val == 0) || (b.is_known && b.val == 0)) {
        res.val = 0;
        res.is_known = 1;
    } else if (a.is_known && b.is_known) {
        res.val = a.val & b.val;
        res.is_known = 1;
    } else {
        res.val = 0;
        res.is_known = 0; /* UNKNOWN */
    }
    return res;
}

TriBool tri_or(TriBool a, TriBool b) {
    TriBool res;
    /* Якщо хоча б один TRUE (val=1, is_known=1) -> результат TRUE */
    if ((a.is_known && a.val == 1) || (b.is_known && b.val == 1)) {
        res.val = 1;
        res.is_known = 1;
    } else if (a.is_known && b.is_known) {
        res.val = a.val | b.val;
        res.is_known = 1;
    } else {
        res.val = 0;
        res.is_known = 0; /* UNKNOWN */
    }
    return res;
}

TriBool tri_not(TriBool a) {
    TriBool res;
    if (!a.is_known) {
        res.val = 0;
        res.is_known = 0;
    } else {
        res.val = (uint8_t)(1 - a.val);
        res.is_known = 1;
    }
    return res;
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <optional>

enum class TriState : uint8_t {
    False = 0,
    Unknown = 1,
    True = 2
};

class TriBool {
public:
    constexpr TriBool() noexcept : state_(TriState::Unknown) {}
    constexpr explicit TriBool(bool val) noexcept : state_(val ? TriState::True : TriState::False) {}
    constexpr explicit TriBool(TriState st) noexcept : state_(st) {}

    [[nodiscard]] constexpr TriState state() const noexcept { return state_; }
    [[nodiscard]] constexpr bool is_true() const noexcept { return state_ == TriState::True; }
    [[nodiscard]] constexpr bool is_false() const noexcept { return state_ == TriState::False; }
    [[nodiscard]] constexpr bool is_unknown() const noexcept { return state_ == TriState::Unknown; }

    /* A AND B = min(state(A), state(B)) за порядком False (0) < Unknown (1) < True (2) */
    [[nodiscard]] constexpr TriBool operator&&(TriBool rhs) const noexcept {
        const auto s1 = static_cast<uint8_t>(state_);
        const auto s2 = static_cast<uint8_t>(rhs.state_);
        return TriBool(static_cast<TriState>(s1 < s2 ? s1 : s2));
    }

    /* A OR B = max(state(A), state(B)) */
    [[nodiscard]] constexpr TriBool operator||(TriBool rhs) const noexcept {
        const auto s1 = static_cast<uint8_t>(state_);
        const auto s2 = static_cast<uint8_t>(rhs.state_);
        return TriBool(static_cast<TriState>(s1 > s2 ? s1 : s2));
    }

    /* NOT A: False <-> True, Unknown <-> Unknown */
    [[nodiscard]] constexpr TriBool operator!() const noexcept {
        if (state_ == TriState::True) return TriBool(TriState::False);
        if (state_ == TriState::False) return TriBool(TriState::True);
        return TriBool(TriState::Unknown);
    }

private:
    TriState state_;
};
```
:::

## Оцінка предикатів фільтрації WHERE проти обмежень CHECK

Прикладний код нижче демонструє принципову інженерну різницю між обчисленням умов у фільтрах запиту (`WHERE` / `HAVING`) та обмеженнях цілісності схеми (`CHECK constraints`).

У фільтрі `WHERE` кортеж вважається валідним виключно тоді, коли результат обчислення виразу є строго `TRUE`. Стан `UNKNOWN` відкидається так само, як і `FALSE`. Навпаки, механізм перевірки обмежень `CHECK` сигналізує про помилку порушення цілісності виключно у випадку, коли вираз оцінюється як `FALSE`. Якщо результатом є `UNKNOWN`, обмеження вважається задоволеним, і кортеж успішно записується в базу даних.

:::tabs
```c
/* Демонстрація відмінності між WHERE та CHECK */
void evaluate_conditions(TriBool condition_result) {
    /* Правило WHERE: Accept ONLY TRUE */
    bool where_passed = (condition_result.is_known && condition_result.val == 1);
    
    /* Правило CHECK: Reject ONLY FALSE */
    bool check_passed = !(condition_result.is_known && condition_result.val == 0);
    
    printf("Результат 3VL: %s\n", 
           !condition_result.is_known ? "UNKNOWN" : (condition_result.val ? "TRUE" : "FALSE"));
    printf("  Фільтр WHERE (пропуск кортежу): %s\n", where_passed ? "ПРИЙНЯТО" : "ВІДХИЛЕНО");
    printf("  Обмеження CHECK (валідація):   %s\n", check_passed ? "ДОЗВОЛЕНО" : "ПОМИЛКА");
}
```
```cpp
#include <iostream>
#include <string_view>

void evaluate_conditions_cpp(TriBool cond) {
    /* WHERE: пропускає лише якщо результат строго TRUE */
    const bool where_passed = cond.is_true();

    /* CHECK: відхиляє лише якщо результат строго FALSE (Unknown дозволено!) */
    const bool check_passed = !cond.is_false();

    std::string_view state_str = "UNKNOWN";
    if (cond.is_true()) state_str = "TRUE";
    else if (cond.is_false()) state_str = "FALSE";

    std::cout << "Результат 3VL: " << state_str << '\n';
    std::cout << "  Фільтр WHERE (пропуск кортежу): " << (where_passed ? "ПРИЙНЯТО" : "ВІДХИЛЕНО") << '\n';
    std::cout << "  Обмеження CHECK (валідація):   " << (check_passed ? "ДОЗВОЛЕНО" : "ПОМИЛКА") << '\n';
}
```
:::

## Вирівнювання пам'яті, деформація кортежів та масштабування для широких схем

Реальні СУБД (зокрема PostgreSQL) накладають жорсткі вимоги на вирівнювання адрес пам'яті (`MAXALIGN`, зазвичай 8 байтів на 64-бітних архітектурах x86_64 та ARM64). Якщо після 23 байтів фіксованого заголовка `HeapTupleHeaderData` та бітової карти `t_bits` загальний зсув не кратний 8, рушій додає байти заповнення (padding), аби перше числове поле лягло на кратну адресу. Це запобігає апаратним штрафам за некратне читання пам'яті (unaligned memory access).

Для таблиць із широкими схемами (понад 32 чи 64 колонки) бітова карта автоматично масштабується у динамічний масив байтів довжиною `ceil(num_columns / 8)`. Перевірка біта здійснюється через двовимірну індексацію `t_bits[col_idx / 8] & (1 << (col_idx % 8))`.

Для прискорення читання кортежів PostgreSQL реалізує механізм «деформації» (`slot_deform_tuple` у файлі `heaptuple.c`). Під час першого звернення до рядка рушій один раз сканує бітову карту та розпаковує всі зміщення атрибутів у плоский кешований масив покажчиків, уникаючи повторного побітового обчислення зсувів для кожного звернення до колонки у виразі.

Використання бітових карт наявності також суттєво оптимізує операції модифікації структури таблиць (Schema Evolution). Коли адміністратор бази даних виконує команду додавання нового стовпця з можливістю зберігання `NULL` (`ALTER TABLE users ADD COLUMN middle_name VARCHAR(100) DEFAULT NULL`), сучасні СУБД (зокрема PostgreSQL починаючи з версії 11) не перезаписують терабайти існуючих сторінок на диску.

Замість фізичного переписування рушій оновлює лише системний каталог метаданих (`pg_attribute`), фіксуючи нову арність схеми. Під час майбутніх операцій читання старих кортежів рушій бачить, що бітова карта рядка коротша за поточну кількість колонок у схемі, і автоматично підставляє `NULL` для всіх доданих полів «на льоту» з нульовими витратами дискового введення-виведення.
