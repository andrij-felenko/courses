#include "pwm_driver.h"
#include <stdio.h>
#include <stddef.h>

/**
 * @brief Симуляція структури апаратних регістрів таймера мікроконтролера.
 * 
 * На реальному мікроконтролері (наприклад, STM32) ці регістри відображаються
 * на фізичні адреси периферійного таймера TIMx (наприклад, TIM1->PSC, TIM1->ARR).
 */
typedef struct {
    volatile uint32_t CR1;   /**< Control Register 1: дозвіл рахунку, напрямок */
    volatile uint32_t CCMR1; /**< Capture/Compare Mode Register 1: режим ШІМ */
    volatile uint32_t CCER;  /**< Capture/Compare Enable Register: дозвіл виходу */
    volatile uint32_t PSC;   /**< Prescaler: преддільник частоти тактування */
    volatile uint32_t ARR;   /**< Auto-Reload Register: період (TOP) таймера */
    volatile uint32_t CCR1;  /**< Capture/Compare Register 1: коефіцієнт заповнення */
} mcu_timer_registers_t;

/* Симульований екземпляр апаратного таймера */
static mcu_timer_registers_t HW_TIM1 = {0};

pwm_status_t pwm_driver_init(pwm_driver_t *driver, const pwm_config_t *config)
{
    if (driver == NULL || config == NULL) {
        return PWM_STATUS_INVALID_PARAM;
    }

    if (config->timer_clock_hz == 0 || config->pwm_frequency_hz == 0) {
        return PWM_STATUS_INVALID_PARAM;
    }

    if (config->pwm_frequency_hz > config->timer_clock_hz) {
        return PWM_STATUS_INVALID_PARAM;
    }

    if (config->timer_channel < 1 || config->timer_channel > 4) {
        return PWM_STATUS_INVALID_PARAM;
    }

    driver->config = *config;

    /*
     * Розрахунок параметрів апаратного таймера:
     * Частота ШІМ обчислюється за формулою:
     * F_pwm = F_timer / ((PSC + 1) * (ARR + 1))
     *
     * Для низькостороннього MOSFET-ключа DC-мотора важливо вибрати частоту > 15-20 кГц,
     * щоб уникнути чутного акустичного писку обмоток та зменшити пульсації струму.
     * Задамо цільове значення ARR = 1000 відліків для дискретності керування 0.1%.
     */
    uint32_t target_arr = 1000;
    uint32_t total_div = config->timer_clock_hz / (config->pwm_frequency_hz * target_arr);

    if (total_div == 0) {
        /* Якщо частота надто висока, обчислюємо без преддільника (PSC = 0) */
        driver->prescaler = 0;
        driver->period_arr = (uint16_t)((config->timer_clock_hz / config->pwm_frequency_hz) - 1);
    } else {
        driver->prescaler = (uint16_t)(total_div - 1);
        driver->period_arr = (uint16_t)(target_arr - 1);
    }

    driver->compare_ccr = 0;
    driver->current_duty_pct = 0;
    driver->is_running = false;

    /* 1. Запис налаштувань у фізичні/симульовані регістри таймера */
    HW_TIM1.PSC = driver->prescaler;
    HW_TIM1.ARR = driver->period_arr;
    HW_TIM1.CCR1 = 0; // Початковий стан — MOSFET закритий (0% ШІМ)

    /*
     * 2. Конфігурація режиму ШІМ (PWM Mode 1):
     * Вихід HIGH, поки лічильник CNT < CCR1, далі LOW.
     * Оскільки ключ низькосторонній (N-MOSFET комутує навантаження на GND):
     * - При HIGH на затворі: MOSFET відкритий, мотор підключено до GND (струм тече).
     * - При LOW на затворі: MOSFET закритий, мотор відключено від GND (струм зупинено).
     */
    HW_TIM1.CCMR1 = (6U << 4); // PWM mode 1
    HW_TIM1.CCER |= (1U << 0); // Enable output channel 1

    driver->is_initialized = true;

    printf("[PWM DRIVER] Налаштовано таймер: Тактування=%u Гц, Частота ШІМ=%u Гц\n",
           (unsigned int)config->timer_clock_hz, (unsigned int)config->pwm_frequency_hz);
    printf("[PWM DRIVER] Запис регістрів: PSC=%u, ARR=%u (Роздільна здатність ШІМ)\n",
           driver->prescaler, driver->period_arr);
    printf("[PWM DRIVER] Схемотехніка ключа: N-MOSFET (Low-Side), затвор на GPIO %u через R_g, R_pd на GND\n",
           config->gpio_pin);

    return PWM_STATUS_OK;
}

pwm_status_t pwm_driver_start(pwm_driver_t *driver)
{
    if (driver == NULL || !driver->is_initialized) {
        return PWM_STATUS_NOT_INITIALIZED;
    }

    /* Дозвіл тактування/лічильника таймера (CEN bit in CR1) */
    HW_TIM1.CR1 |= (1U << 0);
    driver->is_running = true;

    printf("[PWM DRIVER] Запуск апаратного таймера (ШІМ активний).\n");
    return PWM_STATUS_OK;
}

pwm_status_t pwm_driver_stop(pwm_driver_t *driver)
{
    if (driver == NULL || !driver->is_initialized) {
        return PWM_STATUS_NOT_INITIALIZED;
    }

    /* Встановлюємо 0% заповнення перед зупинкою для безпечного закриття ключа */
    pwm_set_duty_cycle(driver, 0);

    /* Вимикаємо лічильник (CEN = 0) */
    HW_TIM1.CR1 &= ~(1U << 0);
    driver->is_running = false;

    printf("[PWM DRIVER] Таймер зупинено. MOSFET-ключ примусово закритий (Gate = 0V).\n");
    return PWM_STATUS_OK;
}

pwm_status_t pwm_set_duty_raw(pwm_driver_t *driver, uint16_t compare_val)
{
    if (driver == NULL || !driver->is_initialized) {
        return PWM_STATUS_NOT_INITIALIZED;
    }

    /* Обмеження верхньої межі значення порівняння регістром ARR */
    if (compare_val > driver->period_arr) {
        compare_val = driver->period_arr;
    }

    driver->compare_ccr = compare_val;
    HW_TIM1.CCR1 = compare_val;

    /* Розрахунок еквівалентного відсотка */
    driver->current_duty_pct = (uint8_t)(((uint32_t)compare_val * 100U) / driver->period_arr);

    return PWM_STATUS_OK;
}

pwm_status_t pwm_set_duty_cycle(pwm_driver_t *driver, uint8_t duty_percent)
{
    if (driver == NULL || !driver->is_initialized) {
        return PWM_STATUS_NOT_INITIALIZED;
    }

    if (duty_percent > PWM_DUTY_MAX_PERCENT) {
        duty_percent = PWM_DUTY_MAX_PERCENT;
    }

    /*
     * Формула розрахунку значення регістру порівняння (CCR):
     * CCR = (Duty% * (ARR + 1)) / 100
     */
    uint32_t ccr_val = ((uint32_t)duty_percent * ((uint32_t)driver->period_arr + 1U)) / 100U;
    
    if (ccr_val > driver->period_arr) {
        ccr_val = driver->period_arr;
    }

    driver->compare_ccr = (uint16_t)ccr_val;
    driver->current_duty_pct = duty_percent;
    HW_TIM1.CCR1 = driver->compare_ccr;

    return PWM_STATUS_OK;
}

uint8_t pwm_get_current_duty(const pwm_driver_t *driver)
{
    if (driver == NULL || !driver->is_initialized) {
        return 0;
    }
    return driver->current_duty_pct;
}
