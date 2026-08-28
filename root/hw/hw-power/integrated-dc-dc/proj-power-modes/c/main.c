#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів підсистеми живлення (PWR / SMPS) */
#define PWR_BASE_ADDR        0x58000400UL
#define PWR_CR1_REG          (*(volatile uint32_t *)(PWR_BASE_ADDR + 0x00))
#define PWR_CR2_REG          (*(volatile uint32_t *)(PWR_BASE_ADDR + 0x04))
#define PWR_CR5_REG          (*(volatile uint32_t *)(PWR_BASE_ADDR + 0x10))
#define PWR_SR2_REG          (*(volatile uint32_t *)(PWR_BASE_ADDR + 0x18))

/* Бітові маски керування SMPS / DC-DC */
#define PWR_CR5_SMPSEN       (1UL << 0)   /* Дозвіл роботи DC-DC */
#define PWR_CR5_BORH_EN      (1UL << 8)   /* Захист від просідання напруги */
#define PWR_CR5_ILMP_SHIFT   16           /* Біти обмеження пікового струму котушки */
#define PWR_CR5_ILMP_MASK    (3UL << PWR_CR5_ILMP_SHIFT)
#define PWR_SR2_SMPSRDY      (1UL << 0)   /* Прапорець готовності виходу DC-DC */
#define PWR_CR1_LPR          (1UL << 14)  /* Вибір режиму низького споживання */
#define PWR_CR1_VOS_SHIFT    9            /* Масштабування напруги ядра (DVS) */
#define PWR_CR1_VOS_MASK     (3UL << PWR_CR1_VOS_SHIFT)

/* Статуси виконання операцій */
typedef enum {
    PWR_STATUS_OK = 0,
    PWR_STATUS_TIMEOUT,
    PWR_STATUS_HARDWARE_ERROR,
    PWR_STATUS_INVALID_PARAM
} PwrStatus_t;

/* Профілі обмеження струму індуктивності */
typedef enum {
    INDUCTOR_LIMIT_100MA = 0,
    INDUCTOR_LIMIT_150MA,
    INDUCTOR_LIMIT_200MA,
    INDUCTOR_LIMIT_300MA
} InductorLimit_t;

/* Профілі напруги ядра (DVS) */
typedef enum {
    CORE_VOLTAGE_SCALE1 = 1, /* 1.2 В (максимальна частота ядра) */
    CORE_VOLTAGE_SCALE2 = 2  /* 1.0 В (енергоощадна частота ядра) */
} CoreVoltageScale_t;

/**
 * @brief Ініціалізація та плавний запуск вбудованого DC-DC перетворювача.
 * @param limit Профіль пікового струму котушки.
 * @param timeout_cycles Максимальна кількість ітерацій очікування стабілізації.
 * @return PwrStatus_t Результат операції.
 */
PwrStatus_t Pwr_EnableDCDC(InductorLimit_t limit, uint32_t timeout_cycles) {
    /* Якщо DC-DC вже активний і стабільний, повторний запуск не потрібен */
    if ((PWR_CR5_REG & PWR_CR5_SMPSEN) && (PWR_SR2_REG & PWR_SR2_SMPSRDY)) {
        return PWR_STATUS_OK;
    }

    /* Налаштування струмового захисту котушки */
    uint32_t cr5 = PWR_CR5_REG;
    cr5 &= ~PWR_CR5_ILMP_MASK;
    cr5 |= ((uint32_t)limit << PWR_CR5_ILMP_SHIFT);
    PWR_CR5_REG = cr5;

    /* Увімкнення супервізора напруги для захисту від просідання шини */
    PWR_CR5_REG |= PWR_CR5_BORH_EN;

    /* Подача команди запуску силових ключів DC-DC */
    PWR_CR5_REG |= PWR_CR5_SMPSEN;

    /* Очікування виходу вихідної напруги ядра на стабільний рівень 1.1 В */
    while (!(PWR_SR2_REG & PWR_SR2_SMPSRDY)) {
        if (--timeout_cycles == 0) {
            /* Тайм-аут: відкат на роботу від LDO для запобігання зависанню */
            PWR_CR5_REG &= ~PWR_CR5_SMPSEN;
            return PWR_STATUS_TIMEOUT;
        }
    }

    return PWR_STATUS_OK;
}

/**
 * @brief Безпечне вимкнення DC-DC з поверненням на головний LDO.
 */
void Pwr_DisableDCDC(void) {
    /* Вимкнення імпульсного перетворювача; апаратура перемикає ядро на LDO */
    PWR_CR5_REG &= ~PWR_CR5_SMPSEN;
}

/**
 * @brief Налаштування масштабування напруги ядра (DVS).
 */
PwrStatus_t Pwr_SetCoreVoltageScale(CoreVoltageScale_t scale) {
    uint32_t cr1 = PWR_CR1_REG;
    cr1 &= ~PWR_CR1_VOS_MASK;
    cr1 |= ((uint32_t)scale << PWR_CR1_VOS_SHIFT);
    PWR_CR1_REG = cr1;

    return PWR_STATUS_OK;
}

/**
 * @brief Підготовка підсистеми живлення до входу в режим глибокого сну (Stop Mode).
 */
void Pwr_EnterDeepSleep(void) {
    /* 1. Активація режиму зниженого споживання регулятора (ULP-LDO) */
    PWR_CR1_REG |= PWR_CR1_LPR;

    /* 2. Зупинка DC-DC перетворювача для виключення втрат холостого ходу */
    PWR_CR5_REG &= ~PWR_CR5_SMPSEN;

    /* 3. Інструкції синхронізації пам'яті та очікування переривання */
    __asm volatile ("dsb");
    __asm volatile ("wfi");
    __asm volatile ("isb");

    /* 4. Після пробудження: повернення до звичайного режиму головного регулятора */
    PWR_CR1_REG &= ~PWR_CR1_LPR;
}
