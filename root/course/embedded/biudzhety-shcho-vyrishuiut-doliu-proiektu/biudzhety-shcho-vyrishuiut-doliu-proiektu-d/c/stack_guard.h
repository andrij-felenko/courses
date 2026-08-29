#ifndef STACK_GUARD_H
#define STACK_GUARD_H

/*
 * Вимірювання найгіршого залишку стеків задач методом вотермарки.
 *
 * Стек задачі заливається шаблоном при створенні; глибина занурення дорівнює
 * кількості слів, які так і лишилися незайманими від дна. Найнижче слово
 * лишається сторожовим: його затирання означає, що стек уже вибіг за межі
 * виділеної області й пам'ять сусіда пошкоджено.
 */

#include "budget_types.h"

#define STACK_GUARD_MAX_TASKS 8u
#define STACK_GUARD_PATTERN   0xA5A5A5A5u

typedef struct {
    const char *name;          /* ім'я задачі у звіті */
    uint32_t   *base;          /* найнижча адреса області (стек росте вниз) */
    size_t      words;         /* розмір області у 32-бітних словах */
    size_t      reserve_bytes; /* мінімальний запас, нижче якого — тривога */
} stack_guard_entry_t;

typedef struct {
    stack_guard_entry_t entries[STACK_GUARD_MAX_TASKS];
    size_t              count;
} stack_registry_t;

typedef struct {
    size_t      task_count;
    size_t      free_bytes[STACK_GUARD_MAX_TASKS];
    size_t      worst_index;   /* задача з найменшим запасом */
    size_t      worst_free;    /* її запас у байтах */
    const char *worst_name;
} stack_report_t;

void stack_registry_init(stack_registry_t *reg);

/*
 * Реєструє область стеку й заливає її шаблоном. Заливати можна лише стек, який
 * ще не почав виконуватися, — інакше буде затерто збережений контекст.
 * Повертає false, якщо таблиця заповнена або аргументи некоректні.
 */
bool stack_guard_register(stack_registry_t *reg, const char *name, void *base,
                          size_t size_bytes, size_t reserve_bytes);

/* Незайманий запас конкретної області в байтах. */
size_t stack_guard_free_bytes(const stack_registry_t *reg, size_t index);

/* Чи ціле сторожове слово на дні області. */
bool stack_guard_intact(const stack_registry_t *reg, size_t index);

budget_flags_t stack_guard_audit(const stack_registry_t *reg,
                                 stack_report_t *report);

#endif /* STACK_GUARD_H */
