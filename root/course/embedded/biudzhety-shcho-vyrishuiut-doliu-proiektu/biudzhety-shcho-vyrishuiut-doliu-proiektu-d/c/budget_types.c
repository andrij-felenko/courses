#include "budget_types.h"

#include <string.h>

struct flag_name {
    budget_flags_t flag;
    const char    *name;
};

static const struct flag_name k_names[] = {
    { BUDGET_STACK_LOW,       "СТЕК:ЗАПАС"        },
    { BUDGET_STACK_OVERFLOW,  "СТЕК:ПЕРЕПОВНЕННЯ" },
    { BUDGET_HEAP_LOW,        "КУЧА:ЗАПАС"        },
    { BUDGET_HEAP_FRAGMENTED, "КУЧА:ФРАГМЕНТАЦІЯ" },
    { BUDGET_FLASH_NO_OTA,    "FLASH:БЕЗ-OTA"     },
    { BUDGET_FLASH_TIGHT,     "FLASH:ТІСНО"       },
    { BUDGET_VDD_SAG,         "VDD:ПРОСІДАННЯ"    },
    { BUDGET_VDD_BROWNOUT,    "VDD:BOR"           },
    { BUDGET_ENERGY_OVER,     "ЕНЕРГІЯ:ПЕРЕВИТРАТА" },
    { BUDGET_THERMAL_WARN,    "ТЕПЛО:ЗАПАС"       },
    { BUDGET_THERMAL_TRIP,    "ТЕПЛО:T_j_max"     },
    { BUDGET_DEADLINE_MISS,   "ЧАС:ЗРИВ-ТЕРМІНУ"  }
};

static const size_t k_name_count = sizeof k_names / sizeof k_names[0];

budget_severity_t budget_severity_of(budget_flags_t flags)
{
    if ((flags & BUDGET_CRITICAL_MASK) != 0u) {
        return BUDGET_SEVERITY_CRITICAL;
    }
    if (flags != BUDGET_OK) {
        return BUDGET_SEVERITY_WARNING;
    }
    return BUDGET_SEVERITY_OK;
}

const char *budget_flag_name(budget_flags_t single_flag)
{
    for (size_t i = 0; i < k_name_count; ++i) {
        if (k_names[i].flag == single_flag) {
            return k_names[i].name;
        }
    }
    return "?";
}

size_t budget_flags_format(budget_flags_t flags, char *out, size_t cap)
{
    if (out == NULL || cap == 0u) {
        return 0u;
    }

    size_t written = 0u;
    out[0] = '\0';

    if (flags == BUDGET_OK) {
        const char *ok = "усі бюджети в межах";
        size_t len = strlen(ok);
        if (len >= cap) {
            len = cap - 1u;
        }
        memcpy(out, ok, len);
        out[len] = '\0';
        return len;
    }

    for (size_t i = 0; i < k_name_count; ++i) {
        if ((flags & k_names[i].flag) == 0u) {
            continue;
        }

        const char *name = k_names[i].name;
        size_t need = strlen(name) + (written > 0u ? 2u : 0u);

        /* Місця не лишилося — обриваємо перелік, але не псуємо буфер. */
        if (written + need + 1u > cap) {
            break;
        }
        if (written > 0u) {
            out[written++] = ',';
            out[written++] = ' ';
        }
        memcpy(out + written, name, strlen(name));
        written += strlen(name);
        out[written] = '\0';
    }

    return written;
}
