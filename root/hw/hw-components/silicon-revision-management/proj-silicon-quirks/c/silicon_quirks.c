/* silicon_quirks.h / silicon_quirks.c - Системна реалізація мовою C */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Числові константи апаратних ревізій кремнію */
typedef enum {
    SILICON_REV_UNKNOWN = 0x0000,
    SILICON_REV_A0      = 0x1000, /* Початковий запуск чіпа */
    SILICON_REV_A1      = 0x1001, /* Металевий ECO-фікс */
    SILICON_REV_B0      = 0x2000, /* Базовий All-layer фікс */
    SILICON_REV_B1      = 0x2001, /* Оптимізована ревізія */
} silicon_rev_t;

/* Бітова маска активних апаратних вад (Quirks) */
typedef enum {
    QUIRK_NONE                  = 0,
    QUIRK_I2C_STOP_LOCK         = (1U << 0), /* Errata #1: блокування шини при STOP */
    QUIRK_UART_FIFO_CORRUPT     = (1U << 1), /* Errata #2: спотворення байта UART */
    QUIRK_TIMER_EXT_TRIGGER     = (1U << 2), /* Errata #3: пропуск імпульсів тригера */
    QUIRK_ADC_OFFSET_DRIFT      = (1U << 3), /* Errata #4: дрейф зміщення АЦП */
} silicon_quirk_mask_t;

/* Структура опису чіпа в системі */
typedef struct {
    uint16_t dev_id;
    silicon_rev_t rev_id;
    const char *rev_name;
    uint32_t active_quirks;
} chip_info_t;

/* Елемент статичної таблиці конфігурацій */
typedef struct {
    silicon_rev_t rev_id;
    const char *name;
    uint32_t quirks;
} silicon_quirk_entry_t;

/* Адреси системних регістрів ідентифікації (STM32 DBGMCU_IDCODE) */
#define DBGMCU_IDCODE_ADDR    (0xE0042000UL)
#define DBGMCU_DEV_ID_MASK    (0x00000FFFUL)
#define DBGMCU_REV_ID_SHIFT   (16U)
#define DBGMCU_REV_ID_MASK    (0xFFFF0000UL)

/* Глобальний стан активного кремнію */
static chip_info_t g_chip_info = {
    .dev_id = 0,
    .rev_id = SILICON_REV_UNKNOWN,
    .rev_name = "UNKNOWN",
    .active_quirks = QUIRK_NONE
};

/* Статична таблиця ревізій та призначених вад */
static const silicon_quirk_entry_t QUIRK_TABLE[] = {
    {
        SILICON_REV_A0,
        "Rev A0 (Initial Silicon)",
        QUIRK_I2C_STOP_LOCK | QUIRK_UART_FIFO_CORRUPT | QUIRK_TIMER_EXT_TRIGGER
    },
    {
        SILICON_REV_A1,
        "Rev A1 (Metal ECO Fix)",
        QUIRK_UART_FIFO_CORRUPT | QUIRK_TIMER_EXT_TRIGGER
    },
    {
        SILICON_REV_B0,
        "Rev B0 (Base Layer Fix)",
        QUIRK_NONE
    },
    {
        SILICON_REV_B1,
        "Rev B1 (Production Optimized)",
        QUIRK_NONE
    }
};

#define QUIRK_TABLE_SIZE (sizeof(QUIRK_TABLE) / sizeof(QUIRK_TABLE[0]))

/* Низькорівневе зчитування системного регістра ідентифікації */
static inline uint32_t read_hardware_idcode(void) {
    /* На реальному обладнанні: return *((volatile uint32_t *)DBGMCU_IDCODE_ADDR); */
    /* Для емуляції повертаємо типовий зразок: Rev A0 (DevID=0x413, RevID=0x1000) */
    return (0x1000U << DBGMCU_REV_ID_SHIFT) | 0x413U;
}

/* Ініціалізація та налаштування маски quirks при завантаженні системи */
void silicon_management_init(void) {
    uint32_t raw_id = read_hardware_idcode();
    
    g_chip_info.dev_id = (uint16_t)(raw_id & DBGMCU_DEV_ID_MASK);
    g_chip_info.rev_id = (silicon_rev_t)((raw_id & DBGMCU_REV_ID_MASK) >> DBGMCU_REV_ID_SHIFT);
    g_chip_info.active_quirks = QUIRK_NONE;
    g_chip_info.rev_name = "UNKNOWN";

    for (size_t i = 0; i < QUIRK_TABLE_SIZE; ++i) {
        if (QUIRK_TABLE[i].rev_id == g_chip_info.rev_id) {
            g_chip_info.active_quirks = QUIRK_TABLE[i].quirks;
            g_chip_info.rev_name = QUIRK_TABLE[i].name;
            break;
        }
    }
}

/* Перевірка наявності конкретної вади в активному кристалі */
bool silicon_has_quirk(silicon_quirk_mask_t quirk) {
    return (g_chip_info.active_quirks & (uint32_t)quirk) != 0;
}

/* Отримання поточної структури чіпа */
const chip_info_t* silicon_get_info(void) {
    return &g_chip_info;
}

/* Приклад використання в периферійному драйвері I2C */
void driver_i2c_send_stop_sequence(volatile uint32_t *i2c_cr2_reg) {
    if (silicon_has_quirk(QUIRK_I2C_STOP_LOCK)) {
        /* Апаратний Workaround: встановити біт затримки генерації та зробити dummy-читання */
        *i2c_cr2_reg |= (1U << 14); /* Увімкнути захисний таймінг */
        volatile uint32_t dummy = *i2c_cr2_reg;
        (void)dummy;
    }
    
    /* Штатна генерація сигналу STOP */
    *i2c_cr2_reg |= (1U << 9); /* Біт STOP */
}
