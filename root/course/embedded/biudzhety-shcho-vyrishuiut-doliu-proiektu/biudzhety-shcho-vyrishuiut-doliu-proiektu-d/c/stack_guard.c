#include "stack_guard.h"

#include <string.h>

void stack_registry_init(stack_registry_t *reg)
{
    if (reg == NULL) {
        return;
    }
    memset(reg, 0, sizeof *reg);
}

bool stack_guard_register(stack_registry_t *reg, const char *name, void *base,
                          size_t size_bytes, size_t reserve_bytes)
{
    if (reg == NULL || name == NULL || base == NULL) {
        return false;
    }
    if (reg->count >= STACK_GUARD_MAX_TASKS) {
        return false;
    }

    /* Вотермарка працює по 32-бітних словах, тож область має бути вирівняна. */
    if (((uintptr_t)base % sizeof(uint32_t)) != 0u) {
        return false;
    }

    size_t words = size_bytes / sizeof(uint32_t);
    if (words < 2u) {
        return false;
    }

    stack_guard_entry_t *e = &reg->entries[reg->count];
    e->name          = name;
    e->base          = (uint32_t *)base;
    e->words         = words;
    e->reserve_bytes = reserve_bytes;

    for (size_t i = 0; i < words; ++i) {
        e->base[i] = STACK_GUARD_PATTERN;
    }

    reg->count++;
    return true;
}

static const stack_guard_entry_t *entry_at(const stack_registry_t *reg,
                                           size_t index)
{
    if (reg == NULL || index >= reg->count) {
        return NULL;
    }
    return &reg->entries[index];
}

size_t stack_guard_free_bytes(const stack_registry_t *reg, size_t index)
{
    const stack_guard_entry_t *e = entry_at(reg, index);
    if (e == NULL) {
        return 0u;
    }

    size_t intact = 0u;
    while (intact < e->words && e->base[intact] == STACK_GUARD_PATTERN) {
        ++intact;
    }
    return intact * sizeof(uint32_t);
}

bool stack_guard_intact(const stack_registry_t *reg, size_t index)
{
    const stack_guard_entry_t *e = entry_at(reg, index);
    if (e == NULL) {
        return false;
    }
    return e->base[0] == STACK_GUARD_PATTERN;
}

budget_flags_t stack_guard_audit(const stack_registry_t *reg,
                                 stack_report_t *report)
{
    if (reg == NULL) {
        return BUDGET_STACK_OVERFLOW;
    }

    budget_flags_t flags = BUDGET_OK;
    size_t worst_free = (size_t)-1;
    size_t worst_index = 0u;

    for (size_t i = 0; i < reg->count; ++i) {
        const stack_guard_entry_t *e = &reg->entries[i];
        size_t free_bytes = stack_guard_free_bytes(reg, i);

        if (!stack_guard_intact(reg, i)) {
            flags |= BUDGET_STACK_OVERFLOW;
        } else if (free_bytes < e->reserve_bytes) {
            flags |= BUDGET_STACK_LOW;
        }

        if (report != NULL) {
            report->free_bytes[i] = free_bytes;
        }
        if (free_bytes < worst_free) {
            worst_free  = free_bytes;
            worst_index = i;
        }
    }

    if (report != NULL) {
        report->task_count  = reg->count;
        report->worst_index = worst_index;
        report->worst_free  = (reg->count > 0u) ? worst_free : 0u;
        report->worst_name  = (reg->count > 0u)
                                  ? reg->entries[worst_index].name
                                  : "—";
    }

    return flags;
}
