/* low_level_pmc_dvfs.h / .c — Драйвер керування живленням кристала SoC (C99) */
#include <stdint.h>
#include <stdbool.h>

#define PMC_BASE_ADDR           0x40020000UL
#define PMIC_I2C_TIMEOUT_CYCLES 500000UL
#define POWER_GOOD_TIMEOUT      100000UL

/* Зсуви регістрів домену */
#define REG_PWR_GATE_CTRL   0x00UL
#define REG_PWR_GATE_STATUS 0x04UL
#define REG_ISO_CTRL        0x08UL
#define REG_RET_CTRL        0x0CUL
#define REG_CLK_GATE_CTRL   0x10UL
#define REG_RESET_CTRL      0x14UL
#define REG_PMIC_VOLT_CMD   0x18UL

/* Бітові маски */
#define PWR_STAGE1_BIT      (1U << 0)
#define PWR_STAGE2_BIT      (1U << 1)
#define PWR_GOOD_BIT        (1U << 0)
#define ISO_ENABLE_BIT      (1U << 0)
#define RET_RESTORE_BIT     (1U << 1)
#define RET_SAVE_BIT        (1U << 0)
#define CLK_ENABLE_BIT      (1U << 0)
#define RESET_DEASSERT_BIT  (1U << 0)

typedef enum {
    OPP_LEVEL_LOW = 0,
    OPP_LEVEL_NOM = 1,
    OPP_LEVEL_HIGH = 2,
    OPP_LEVEL_TURBO = 3
} opp_level_t;

typedef struct {
    uint32_t freq_khz;
    uint32_t voltage_uv;
    uint32_t settle_delay_us;
} opp_point_t;

static const opp_point_t g_opp_table[4] = {
    [OPP_LEVEL_LOW]   = {  400000U,  650000U, 20U },
    [OPP_LEVEL_NOM]   = { 1200000U,  750000U, 25U },
    [OPP_LEVEL_HIGH]  = { 2000000U,  900000U, 35U },
    [OPP_LEVEL_TURBO] = { 2800000U, 1050000U, 50U }
};

static inline void mmio_write32(uintptr_t addr, uint32_t val) {
    *(volatile uint32_t *)addr = val;
}

static inline uint32_t mmio_read32(uintptr_t addr) {
    return *(volatile uint32_t *)addr;
}

static void delay_busy_cycles(uint32_t cycles) {
    for (volatile uint32_t i = 0; i < cycles; ++i) {
        __asm__ __volatile__("" ::: "memory");
    }
}

/* Імітація запису напруги у зовнішній PMIC через регістр контролера */
static bool pmic_set_voltage_uv(uintptr_t domain_base, uint32_t microvolts) {
    mmio_write32(domain_base + REG_PMIC_VOLT_CMD, microvolts);
    uint32_t timeout = PMIC_I2C_TIMEOUT_CYCLES;
    while ((mmio_read32(domain_base + REG_PWR_GATE_STATUS) & 0x02U) == 0U) {
        if (--timeout == 0U) {
            return false; /* Помилка зв'язку з PMIC */
        }
    }
    return true;
}

/* Увімкнення комутованого домену живлення */
bool soc_power_domain_up(uintptr_t domain_base) {
    /* Крок 1: Гарантувати активність ізоляції перед подаванням живлення */
    mmio_write32(domain_base + REG_ISO_CTRL, ISO_ENABLE_BIT);

    /* Крок 2: Увімкнути 1-й ступінь силових ключів (обмеження dI/dt) */
    mmio_write32(domain_base + REG_PWR_GATE_CTRL, PWR_STAGE1_BIT);

    /* Крок 3: Очікування апаратного сигналу Power Good */
    uint32_t timeout = POWER_GOOD_TIMEOUT;
    while ((mmio_read32(domain_base + REG_PWR_GATE_STATUS) & PWR_GOOD_BIT) == 0U) {
        if (--timeout == 0U) {
            /* Аварійне вимкнення ключа при збої живлення */
            mmio_write32(domain_base + REG_PWR_GATE_CTRL, 0U);
            return false;
        }
    }

    /* Крок 4: Увімкнути 2-й ступінь (основні силові PMOS-ключі) */
    mmio_write32(domain_base + REG_PWR_GATE_CTRL, PWR_STAGE1_BIT | PWR_STAGE2_BIT);

    /* Крок 5: Відновлення стану з тригерів Retention */
    mmio_write32(domain_base + REG_RET_CTRL, RET_RESTORE_BIT);
    delay_busy_cycles(500U);
    mmio_write32(domain_base + REG_RET_CTRL, 0U);

    /* Крок 6: Зняття ізоляції з виходів домену */
    mmio_write32(domain_base + REG_ISO_CTRL, 0U);

    /* Крок 7: Увімкнення тактового генератора */
    mmio_write32(domain_base + REG_CLK_GATE_CTRL, CLK_ENABLE_BIT);

    /* Крок 8: Зняття апаратного скидання (Reset Release) */
    mmio_write32(domain_base + REG_RESET_CTRL, RESET_DEASSERT_BIT);

    return true;
}

/* Знеструмлення домену живлення */
bool soc_power_domain_down(uintptr_t domain_base) {
    /* Крок 1: Встановлення апаратного скидання */
    mmio_write32(domain_base + REG_RESET_CTRL, 0U);

    /* Крок 2: Зупинка тактового сигналу */
    mmio_write32(domain_base + REG_CLK_GATE_CTRL, 0U);

    /* Крок 3: Збереження стану в Retention-тригери */
    mmio_write32(domain_base + REG_RET_CTRL, RET_SAVE_BIT);
    delay_busy_cycles(500U);
    mmio_write32(domain_base + REG_RET_CTRL, 0U);

    /* Крок 4: Увімкнення ізоляційних комірок */
    mmio_write32(domain_base + REG_ISO_CTRL, ISO_ENABLE_BIT);

    /* Крок 5: Розмикання силових ключів живлення */
    mmio_write32(domain_base + REG_PWR_GATE_CTRL, 0U);

    return true;
}

/* Безпечний перехід DVFS між робочими точками */
bool soc_dvfs_set_target_opp(uintptr_t domain_base, opp_level_t current_opp, opp_level_t target_opp) {
    if (target_opp == current_opp) {
        return true;
    }

    const opp_point_t *target = &g_opp_table[target_opp];

    if (target_opp > current_opp) {
        /* Підвищення продуктивності (Scale UP):
           1. Спочатку піднімаємо напругу */
        if (!pmic_set_voltage_uv(domain_base, target->voltage_uv)) {
            return false;
        }
        /* 2. Очікуємо стабілізації напруги */
        delay_busy_cycles(target->settle_delay_us * 100U);
        /* 3. Підвищуємо тактову частоту */
        mmio_write32(domain_base + REG_CLK_GATE_CTRL, (target->freq_khz / 1000U));
    } else {
        /* Зниження продуктивності (Scale DOWN):
           1. Спочатку знижуємо тактову частоту */
        mmio_write32(domain_base + REG_CLK_GATE_CTRL, (target->freq_khz / 1000U));
        /* 2. Знижуємо напругу для економії енергії P = C*V^2*f */
        if (!pmic_set_voltage_uv(domain_base, target->voltage_uv)) {
            return false;
        }
        /* 3. Очікуємо стабілізації перехідного процесу */
        delay_busy_cycles(target->settle_delay_us * 100U);
    }

    return true;
}
