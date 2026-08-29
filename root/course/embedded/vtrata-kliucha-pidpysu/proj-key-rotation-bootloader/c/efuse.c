#include <string.h>

#include "efuse.h"

/* ------------------------------------------------------------------ *
 *  Порт під наш SoC: карта регістрів контролера перемичок і PMU.
 * ------------------------------------------------------------------ */

typedef struct {
    volatile uint32_t CTRL;    /* керування циклом                         */
    volatile uint32_t ADDR;    /* номер рядка перемичок                    */
    volatile uint32_t WDATA;   /* маска бітів, які треба спалити           */
    volatile uint32_t RDATA;   /* прочитане слово                          */
    volatile uint32_t STATUS;  /* стан контролера                          */
    volatile uint32_t TIMING;  /* тривалість імпульсу в тактах ядра        */
} efuse_regs_t;

#define EFUSE       ((efuse_regs_t *)0x4008C000UL)

#define EFUSE_CTRL_READ_EN     (1U << 0)
#define EFUSE_CTRL_PROG_EN     (1U << 1)
#define EFUSE_CTRL_PUMP_EN     (1U << 2)  /* генератор підкачування заряду */
#define EFUSE_CTRL_MARGIN_RD   (1U << 3)  /* граничний режим опорного струму */

#define EFUSE_STATUS_BUSY      (1U << 0)
#define EFUSE_STATUS_PGM_ERR   (1U << 1)
#define EFUSE_STATUS_PUMP_RDY  (1U << 2)

typedef struct {
    volatile uint32_t STATUS;  /* стан живлення */
    volatile uint32_t BODCTRL; /* детектор просідання (Brownout Detector) */
} pmu_regs_t;

#define PMU         ((pmu_regs_t *)0x40007000UL)
#define PMU_POWER_GOOD         (1U << 0)
#define PMU_BOD_ARMED          (1U << 1)

/* Розкладка рядків перемичок. Рядок — 32 біти. */
#define EFUSE_ROW_REVOKE       0x20U
#define EFUSE_ROW_COUNTER      0x21U
#define EFUSE_ROW_DIGEST(slot) (0x40U + (uint32_t)(slot) * 8U)  /* 8 рядків = 32 байти */

/* Імпульс програмування: 12 мкс на 96 МГц ядрі. */
#define EFUSE_PULSE_CYCLES     1152U
/* Стеля очікування BUSY — на порядок довша за найповільніший цикл. */
#define EFUSE_BUSY_TIMEOUT     200000U
#define EFUSE_PUMP_TIMEOUT     50000U

static void spin_cycles(uint32_t cycles)
{
    /* Порожній цикл із volatile-лічильником: оптимізатор його не викине. */
    for (volatile uint32_t i = 0; i < cycles; ++i) {
        __asm volatile("nop");
    }
}

static boot_status_t wait_not_busy(void)
{
    for (uint32_t spins = 0; spins < EFUSE_BUSY_TIMEOUT; ++spins) {
        if ((EFUSE->STATUS & EFUSE_STATUS_BUSY) == 0U) {
            return BOOT_OK;
        }
    }
    return BOOT_ERR_EFUSE_TIMEOUT;
}

static bool power_is_good(void)
{
    /*
     * Детектор просідання мусить бути ЗВЕДЕНИЙ: якщо його вимкнули (наприклад,
     * лишився вимкненим після сплячки), ми не дізнаємось про провал напруги
     * посеред імпульсу — і саме звідси беруться напівспалені комірки.
     */
    const uint32_t status = PMU->STATUS;
    return (status & PMU_POWER_GOOD) != 0U && (status & PMU_BOD_ARMED) != 0U;
}

/* Одне читання рядка. mode — 0 або EFUSE_CTRL_MARGIN_RD. */
static boot_status_t efuse_read_row(uint32_t row, uint32_t mode, uint32_t *out)
{
    boot_status_t rc = wait_not_busy();
    if (rc != BOOT_OK) {
        return rc;
    }

    EFUSE->ADDR = row;
    EFUSE->CTRL = EFUSE_CTRL_READ_EN | mode;

    rc = wait_not_busy();
    EFUSE->CTRL = 0U;
    if (rc != BOOT_OK) {
        return rc;
    }

    *out = EFUSE->RDATA;
    return BOOT_OK;
}

/*
 * Палить рівно ті біти рядка, що задані маскою. Уже спалені біти маска не
 * містить: повторний імпульс по цілій перемичці нічого не змінює, але гріє
 * кристал і зайвий раз ганяє генератор підкачування.
 */
static boot_status_t efuse_burn_bits(uint32_t row, uint32_t mask)
{
    if (mask == 0U) {
        return BOOT_OK;
    }

    if (!power_is_good()) {
        return BOOT_ERR_EFUSE_BROWNOUT;
    }

    boot_status_t rc = wait_not_busy();
    if (rc != BOOT_OK) {
        return rc;
    }

    /* 1. Піднімаємо напругу програмування й чекаємо готовності накачки. */
    EFUSE->CTRL = EFUSE_CTRL_PUMP_EN;
    bool pump_ready = false;
    for (uint32_t spins = 0; spins < EFUSE_PUMP_TIMEOUT; ++spins) {
        if ((EFUSE->STATUS & EFUSE_STATUS_PUMP_RDY) != 0U) {
            pump_ready = true;
            break;
        }
    }
    if (!pump_ready) {
        EFUSE->CTRL = 0U;
        return BOOT_ERR_EFUSE_TIMEOUT;
    }

    /* 2. Сам імпульс. */
    EFUSE->ADDR = row;
    EFUSE->WDATA = mask;
    EFUSE->TIMING = EFUSE_PULSE_CYCLES;
    EFUSE->CTRL = EFUSE_CTRL_PUMP_EN | EFUSE_CTRL_PROG_EN;

    rc = wait_not_busy();

    /* 3. Накачку знімаємо ЗАВЖДИ, навіть коли цикл не завершився. */
    EFUSE->CTRL = 0U;
    spin_cycles(EFUSE_PULSE_CYCLES);

    if (rc != BOOT_OK) {
        return rc;
    }
    if ((EFUSE->STATUS & EFUSE_STATUS_PGM_ERR) != 0U) {
        return BOOT_ERR_EFUSE_MARGINAL;
    }

    /*
     * 4. Якщо живлення просіло ПІД ЧАС імпульсу, детектор тримає прапорець.
     * Комірка могла лишитись у проміжному стані, і про це треба сказати вголос.
     */
    if (!power_is_good()) {
        return BOOT_ERR_EFUSE_BROWNOUT;
    }

    /* 5. Контрольне зчитування у звичайному режимі. */
    uint32_t readback = 0U;
    rc = efuse_read_row(row, 0U, &readback);
    if (rc != BOOT_OK) {
        return rc;
    }
    if ((readback & mask) != mask) {
        return BOOT_ERR_EFUSE_MARGINAL;
    }

    /*
     * 6. І ще раз — у граничному режимі опорного струму. Напівспалена перемичка
     * читається як одиниця на номінальному струмі й як нуль на граничному;
     * саме ця пара читань відрізняє надійно спалену комірку від метастабільної.
     */
    rc = efuse_read_row(row, EFUSE_CTRL_MARGIN_RD, &readback);
    if (rc != BOOT_OK) {
        return rc;
    }
    if ((readback & mask) != mask) {
        return BOOT_ERR_EFUSE_MARGINAL;
    }

    return BOOT_OK;
}

/* ------------------------------------------------------------------ *
 *  Відкритий інтерфейс
 * ------------------------------------------------------------------ */

static uint32_t popcount32(uint32_t value)
{
    uint32_t count = 0U;
    while (value != 0U) {
        value &= value - 1U;
        ++count;
    }
    return count;
}

boot_status_t efuse_read_mirror(efuse_mirror_t *out)
{
    if (out == NULL) {
        return BOOT_ERR_FLASH_READ;
    }
    memset(out, 0, sizeof(*out));

    uint32_t row = 0U;
    boot_status_t rc = efuse_read_row(EFUSE_ROW_REVOKE, 0U, &row);
    if (rc != BOOT_OK) {
        return rc;
    }
    out->revocation_bits = (uint8_t)(row & 0x0FU);

    rc = efuse_read_row(EFUSE_ROW_COUNTER, 0U, &row);
    if (rc != BOOT_OK) {
        return rc;
    }
    /*
     * Термометр читаємо через popcount, а не як число: перемичку можна лише
     * спалити, тож монотонність лічильника гарантує сама фізика, а не логіка.
     */
    out->monotonic_counter = popcount32(row);

    for (uint8_t slot = 0; slot < BOOT_KEY_SLOTS; ++slot) {
        for (uint32_t word = 0; word < SHA256_SIZE / 4U; ++word) {
            rc = efuse_read_row(EFUSE_ROW_DIGEST(slot) + word, 0U, &row);
            if (rc != BOOT_OK) {
                return rc;
            }
            /* Хеш зберігаємо у Flash-порядку: little-endian слово → чотири байти. */
            out->root_key_digest[slot][word * 4U + 0U] = (uint8_t)(row & 0xFFU);
            out->root_key_digest[slot][word * 4U + 1U] = (uint8_t)((row >> 8) & 0xFFU);
            out->root_key_digest[slot][word * 4U + 2U] = (uint8_t)((row >> 16) & 0xFFU);
            out->root_key_digest[slot][word * 4U + 3U] = (uint8_t)((row >> 24) & 0xFFU);
        }
    }

    return BOOT_OK;
}

boot_status_t efuse_burn_revocation(uint8_t slot_index)
{
    if (slot_index >= BOOT_KEY_SLOTS) {
        return BOOT_ERR_INVALID_SLOT;
    }

    uint32_t current = 0U;
    boot_status_t rc = efuse_read_row(EFUSE_ROW_REVOKE, 0U, &current);
    if (rc != BOOT_OK) {
        return rc;
    }

    const uint32_t bit = 1U << slot_index;
    if ((current & bit) != 0U) {
        return BOOT_OK;  /* уже відкликано — операція ідемпотентна */
    }

    return efuse_burn_bits(EFUSE_ROW_REVOKE, bit);
}

boot_status_t efuse_burn_counter(uint32_t version)
{
    if (version > EFUSE_COUNTER_BITS) {
        return BOOT_ERR_EFUSE_RANGE;
    }

    uint32_t current = 0U;
    boot_status_t rc = efuse_read_row(EFUSE_ROW_COUNTER, 0U, &current);
    if (rc != BOOT_OK) {
        return rc;
    }

    const uint32_t burnt = popcount32(current);
    if (version <= burnt) {
        return BOOT_OK;  /* лічильник уже не нижчий за потрібний */
    }

    /*
     * Термометр палимо по одному біту: якщо живлення зникне посеред серії,
     * лічильник просто зупиниться на досягнутому значенні, а не зіпсує
     * половину рядка одним широким імпульсом.
     */
    for (uint32_t bit = burnt; bit < version; ++bit) {
        rc = efuse_burn_bits(EFUSE_ROW_COUNTER, 1U << bit);
        if (rc != BOOT_OK) {
            return rc;
        }
    }

    return BOOT_OK;
}
