#include "silicon_rev.h"

#include "stm32f4_regs.h"

/* ---------------------------------------------------------------------------
 * Таблиця 1: сирий код REV_ID → літера ревізії.
 * Числа беруться з розділу «Device identification» еррати ES0182 і
 * НЕ вигадуються: код, якого немає в таблиці, лишається UNKNOWN.
 * ------------------------------------------------------------------------ */
typedef struct {
    uint16_t      rev_id;
    silicon_rev_t rev;
    const char   *name;
} rev_row_t;

static const rev_row_t k_revisions[] = {
    { 0x1000U, SILICON_REV_A, "Rev A" },
    { 0x1001U, SILICON_REV_Z, "Rev Z" },
    { 0x1003U, SILICON_REV_1, "Rev 1" },
    { 0x1007U, SILICON_REV_2, "Rev 2" },
    { 0x100FU, SILICON_REV_Y, "Rev Y" },
    { 0x2001U, SILICON_REV_3, "Rev 3" },
};

#define REV_COUNT (sizeof(k_revisions) / sizeof(k_revisions[0]))

/* ---------------------------------------------------------------------------
 * Таблиця 2: матриця застосовності. Один біт на ревізію — це та сама
 * колонка з хрестиком у зведеній таблиці еррати.
 * ------------------------------------------------------------------------ */
#define REV_BIT(rev) (1UL << (unsigned)(rev))

#define REV_ALL (REV_BIT(SILICON_REV_A) | REV_BIT(SILICON_REV_Z) | \
                 REV_BIT(SILICON_REV_1) | REV_BIT(SILICON_REV_2) | \
                 REV_BIT(SILICON_REV_Y) | REV_BIT(SILICON_REV_3))

typedef struct {
    const char *title;
    uint32_t    affected; /* маска уражених ревізій */
} erratum_row_t;

static const erratum_row_t k_errata[ERRATUM_COUNT] = {
    [ERRATUM_RCC_CLOCK_ENABLE_DELAY] = {
        "ES0182: Delay after an RCC peripheral clock enabling",
        /* виправлення не існує в жодній ревізії — обхід потрібен завжди */
        REV_ALL,
    },
    [ERRATUM_I2C_BUSY_LOCK] = {
        "ES0182: I2C analog filter may provide wrong value, locking BUSY flag",
        /* у пізніших ревізіях кремнію дефект виправлено — обхід не потрібен */
        REV_BIT(SILICON_REV_A) | REV_BIT(SILICON_REV_Z),
    },
};

/* ------------------------------------------------------------------------ */

static silicon_info_t s_info;
static bool           s_info_valid;

static silicon_rev_t decode_revision(uint16_t rev_id, const char **name_out)
{
    for (size_t i = 0; i < REV_COUNT; ++i) {
        if (k_revisions[i].rev_id == rev_id) {
            if (name_out != NULL) {
                *name_out = k_revisions[i].name;
            }
            return k_revisions[i].rev;
        }
    }
    if (name_out != NULL) {
        *name_out = "Rev ?";
    }
    return SILICON_REV_UNKNOWN;
}

const silicon_info_t *silicon_info(void)
{
    if (!s_info_valid) {
        /* Одне-єдине читання регістра. Розкладка поля: DEV_ID [11:0],
         * REV_ID [31:16], біти [15:12] зарезервовані й маскуються. */
        const uint32_t idcode = DBGMCU->IDCODE;

        s_info.dev_id     = (uint16_t)(idcode & 0x0FFFUL);
        s_info.rev_id     = (uint16_t)((idcode >> 16) & 0xFFFFUL);
        s_info.rev        = decode_revision(s_info.rev_id, NULL);
        s_info.recognised = (s_info.dev_id == SILICON_DEV_ID_F40X);
        s_info_valid      = true;
    }
    return &s_info;
}

const char *silicon_rev_name(silicon_rev_t rev)
{
    for (size_t i = 0; i < REV_COUNT; ++i) {
        if (k_revisions[i].rev == rev) {
            return k_revisions[i].name;
        }
    }
    return "Rev ?";
}

bool silicon_affected_by(erratum_t erratum)
{
    if ((unsigned)erratum >= (unsigned)ERRATUM_COUNT) {
        return false;
    }

    const silicon_info_t *info = silicon_info();

    /* Чужий чип або незнайома ревізія: таблиця, яку ми набрали, не про нього.
     * Безпечна відповідь — «уражений»: зайвий обхід лише сповільнить старт,
     * пропущений обхід зупинить пристрій у полі. */
    if (!info->recognised || info->rev == SILICON_REV_UNKNOWN) {
        return true;
    }

    return (k_errata[erratum].affected & REV_BIT(info->rev)) != 0UL;
}

const char *erratum_title(erratum_t erratum)
{
    if ((unsigned)erratum >= (unsigned)ERRATUM_COUNT) {
        return "невідомий дефект";
    }
    return k_errata[erratum].title;
}
