#include <stdint.h>
#include <stdbool.h>

/* Базові фізичні адреси блоків керування живленням (PWR) та тактуванням (RCC) */
#define PWR_BASE_ADDR           0x40007000U
#define RCC_BASE_ADDR           0x40021000U
#define GPIOG_BASE_ADDR         0x48001800U

/* Зсуви регістрів підсистеми живлення */
#define PWR_CR2_OFFSET          0x04U
#define PWR_CR3_OFFSET          0x08U
#define PWR_SR2_OFFSET          0x14U

/* Зсуви регістрів тактування та скидання */
#define RCC_AHB2ENR_OFFSET      0x4CU
#define RCC_AHB2RSTR_OFFSET     0x2CU

/* Доступ до апаратних регістрів через volatile-покажчики */
#define PWR_REG_CR2             (*(volatile uint32_t *)(PWR_BASE_ADDR + PWR_CR2_OFFSET))
#define PWR_REG_CR3             (*(volatile uint32_t *)(PWR_BASE_ADDR + PWR_CR3_OFFSET))
#define PWR_REG_SR2             (*(volatile uint32_t *)(PWR_BASE_ADDR + PWR_SR2_OFFSET))
#define RCC_REG_AHB2ENR         (*(volatile uint32_t *)(RCC_BASE_ADDR + RCC_AHB2ENR_OFFSET))
#define RCC_REG_AHB2RSTR        (*(volatile uint32_t *)(RCC_BASE_ADDR + RCC_AHB2RSTR_OFFSET))

/* Бітові маски конфігурації домену VDDIO2 (Порт G) */
#define PWR_CR2_PVME2           (1U << 0)  /* Увімкнення компаратора моніторингу PVM2 */
#define PWR_CR2_PWREN2          (1U << 1)  /* Замикання силового ключа живлення домену */
#define PWR_CR2_IOSV            (1U << 9)  /* Зняття ізоляції портів: 1 = шина підключена */
#define PWR_SR2_PVMO2           (1U << 1)  /* Прапорець компаратора: 1 = напруга в нормі */
#define RCC_AHB2ENR_GPIOGEN     (1U << 6)  /* Дозвіл тактування Порту G */
#define RCC_AHB2RSTR_GPIOG_RST  (1U << 6)  /* Скидання логічних тригерів Порту G */

/* Статуси виконання операцій секвенування */
typedef enum {
    PWR_SUCCESS = 0,
    PWR_ERR_VOLTAGE_FAULT,
    PWR_ERR_TIMEOUT,
    PWR_ERR_BUSY
} pwr_result_t;

/* Безпечне покрокове вмикання вторинного силового домену VDDIO2 */
pwr_result_t pwr_domain_vddio2_enable(void) {
    uint32_t timeout_counter = 100000U;

    /* Крок 1: Активація схеми моніторингу напруги зовнішньої шини (PVM2) */
    PWR_REG_CR2 |= PWR_CR2_PVME2;

    /* Крок 2: Очікування виходу напруги джерела на стабільний рівень за компаратором */
    while ((PWR_REG_SR2 & PWR_SR2_PVMO2) == 0U) {
        if (--timeout_counter == 0U) {
            /* Напруга не з'явилася: вимикаємо монітор для усунення зайвого витоку */
            PWR_REG_CR2 &= ~PWR_CR2_PVME2;
            return PWR_ERR_VOLTAGE_FAULT;
        }
    }

    /* Крок 3: Замикання силового ключа внутрішнього комутатора домену */
    PWR_REG_CR2 |= PWR_CR2_PWREN2;

    /* Апаратна затримка для завершення перехідного процесу заряду ємностей шини */
    for (volatile uint32_t delay = 0; delay < 1000U; ++delay) {
        __asm__ volatile ("nop");
    }

    /* Крок 4: Зняття апаратної ізоляції сигнальних ліній між доменами */
    PWR_REG_CR2 |= PWR_CR2_IOSV;

    /* Крок 5: Подання тактування на периферійний модуль Порту G */
    RCC_REG_AHB2ENR |= RCC_AHB2ENR_GPIOGEN;

    /* Крок 6: Імпульс скидання логіки для ініціалізації тригерів у вихідний стан */
    RCC_REG_AHB2RSTR |= RCC_AHB2RSTR_GPIOG_RST;
    RCC_REG_AHB2RSTR &= ~RCC_AHB2RSTR_GPIOG_RST;

    return PWR_SUCCESS;
}

/* Безпечне покрокове вимкнення домену VDDIO2 */
pwr_result_t pwr_domain_vddio2_disable(void) {
    /* Крок 1: Зупинка тактування та переведення блоку в статичний стан */
    RCC_REG_AHB2ENR &= ~RCC_AHB2ENR_GPIOGEN;

    /* Крок 2: Встановлення ізоляційних вентилів (затискання ліній у стані 0) */
    PWR_REG_CR2 &= ~PWR_CR2_IOSV;

    /* Крок 3: Розмикання силового ключа живлення */
    PWR_REG_CR2 &= ~PWR_CR2_PWREN2;

    /* Крок 4: Деактивація монітора напруги для повного зняття споживання */
    PWR_REG_CR2 &= ~PWR_CR2_PVME2;

    return PWR_SUCCESS;
}
