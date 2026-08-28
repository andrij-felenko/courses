#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    PARAM_TYPE_INT32 = 0,
    PARAM_TYPE_FLOAT = 1
} param_type_t;

typedef enum {
    PARAM_FLAG_NONE          = 0,
    PARAM_FLAG_DISARMED_ONLY = 1 << 0,
    PARAM_FLAG_REBOOT_REQ    = 1 << 1,
    PARAM_FLAG_READ_ONLY     = 1 << 2
} param_flags_t;

typedef union {
    int32_t i32;
    float   f32;
    uint8_t raw[4];
} param_val_t;

// Незмінні метадані у Flash ROM (.rodata)
typedef struct {
    const char*   name;            // ASCII-ім'я (до 16 символів)
    param_type_t  type;            // Код типу даних
    param_val_t   min_val;         // Мінімальна синтаксична межа
    param_val_t   max_val;         // Максимальна синтаксична межа
    param_val_t   def_val;         // Значення за замовчуванням
    uint16_t      flags;           // Бітові прапорці доступу
} param_meta_t;

// Оперативний запис у швидкій SRAM
typedef struct {
    const param_meta_t* meta;      // Покажчик на константні метадані
    param_val_t         val;       // Поточне значення
    volatile bool       dirty;     // Ознака необхідності збереження у Flash
} param_entry_t;

// Потокобезпечна валідація та запис
bool param_set_value_safe(param_entry_t* entry, param_val_t new_val, bool is_armed) {
    if (!entry || !entry->meta) return false;

    // 1. Перевірка атрибута тільки для читання
    if (entry->meta->flags & PARAM_FLAG_READ_ONLY) {
        return false;
    }

    // 2. Перевірка блокування при зведених моторах
    if (is_armed && (entry->meta->flags & PARAM_FLAG_DISARMED_ONLY)) {
        return false;
    }

    // 3. Синтаксична перевірка діапазонів
    if (entry->meta->type == PARAM_TYPE_FLOAT) {
        if (new_val.f32 < entry->meta->min_val.f32 || new_val.f32 > entry->meta->max_val.f32) {
            return false;
        }
    } else {
        if (new_val.i32 < entry->meta->min_val.i32 || new_val.i32 > entry->meta->max_val.i32) {
            return false;
        }
    }

    // 4. Оновлення значення та встановлення прапорця dirty
    entry->val = new_val;
    entry->dirty = true;
    return true;
}
