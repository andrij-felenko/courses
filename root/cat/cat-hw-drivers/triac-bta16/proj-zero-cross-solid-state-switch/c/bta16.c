/**
 * @file bta16.c
 * @brief Реалізація низькорівневого процедурного драйвера симістора BTA16-600B.
 *
 * Файл містить процедури налаштування GPIO із запобіганням хибному відкриттю
 * симістора під час старт-апу МК, а також функції увімкнення, вимкнення,
 * опитування стану та формування часових затримок.
 */

#include "bta16.h"
#include <stdio.h>

#if defined(_WIN32) || defined(__unix__) || defined(__APPLE__)
#include <windows.h>
#else
#include <unistd.h>
#include <time.h>
#endif

/* ========================================================================= */
/*              ІМІТАЦІЯ РЕГІСТРІВ ВБУДОВАНОГО МІКРОКОНТРОЛЕРА             */
/* ========================================================================= */

/**
 * @brief Модель апаратних регістрів GPIO для демонстрації низькорівневого керування.
 * У реальній вбудованій системі ці змінні замінюються на адреси регістрів МК
 * (наприклад, PORTB/DDRB в AVR або GPIOA->ODR/MODER в ARM Cortex-M).
 */
static volatile uint8_t MCU_GPIO_OUT_REG = 0x00; /* Вихідний регістр даних (Data Output Register) */
static volatile uint8_t MCU_GPIO_DIR_REG = 0x00; /* Регістр напрямку (Direction Register: 0-In, 1-Out) */

/**
 * @brief Внутрішня змінна зберігання поточного стану силового ключа.
 */
static volatile bool g_triac_is_active = false;

/* ========================================================================= */
/*                     РЕАЛІЗАЦІЯ ФУНКЦІЙ КЕРУВАННЯ                          */
/* ========================================================================= */

void bta16_init(void)
{
    g_triac_is_active = false;

    /*
     * КРОК 1: ГАРАНТУВАННЯ БЕЗПЕКИ ПРИ СТАРТ-АПІ.
     * Записуємо вимкнений стан у регістр даних ДО того, як налаштувати пин як вихід.
     * Якщо керування активним високим рівнем (BTA16_ACTIVE_LEVEL == 1), безпечний стан = 0.
     * Якщо активним низьким рівнем (BTA16_ACTIVE_LEVEL == 0), безпечний стан = 1.
     */
#if (BTA16_ACTIVE_LEVEL == 1)
    MCU_GPIO_OUT_REG &= ~(1U << BTA16_GPIO_PIN); /* Скидаємо біт в 0 (світлодіод оптопари вимкнено) */
#else
    MCU_GPIO_OUT_REG |= (1U << BTA16_GPIO_PIN);  /* Встановлюємо біт в 1 (світлодіод оптопари вимкнено) */
#endif

    /*
     * КРОК 2: НАЛАШТУВАННЯ НАПРЯМКУ ПИНА НА ВИХІД (OUTPUT).
     * Тепер, коли пин перемикається з High-Z (вхід) у режим Output,
     * на ньому ОДРАЗУ з'являється безпечний рівень напруги без сплесків.
     */
    MCU_GPIO_DIR_REG |= (1U << BTA16_GPIO_PIN);

    /*
     * КРОК 3: ВИЗНАЧЕННЯ СТАБІЛІЗАЦІЙНОЇ ЗАРИМКИ.
     * Витримуємо час для завершення перехідних процесів у джерелі живлення МК
     * та опторозв'язці перед початком силової комутації.
     */
    bta16_delay_ms(BTA16_INIT_SAFETY_DELAY_MS);
}

void bta16_on(void)
{
#if (BTA16_ACTIVE_LEVEL == 1)
    MCU_GPIO_OUT_REG |= (1U << BTA16_GPIO_PIN);  /* Подаємо HIGH -> світлодіод оптопари світиться */
#else
    MCU_GPIO_OUT_REG &= ~(1U << BTA16_GPIO_PIN); /* Подаємо LOW  -> світлодіод оптопари світиться */
#endif

    g_triac_is_active = true;
    bta16_delay_ms(BTA16_MIN_SWITCH_DELAY_MS);
}

void bta16_off(void)
{
#if (BTA16_ACTIVE_LEVEL == 1)
    MCU_GPIO_OUT_REG &= ~(1U << BTA16_GPIO_PIN); /* Подаємо LOW  -> світлодіод оптопари гасне */
#else
    MCU_GPIO_OUT_REG |= (1U << BTA16_GPIO_PIN);  /* Подаємо HIGH -> світлодіод оптопари гасне */
#endif

    g_triac_is_active = false;
    bta16_delay_ms(BTA16_MIN_SWITCH_DELAY_MS);
}

void bta16_toggle(void)
{
    if (g_triac_is_active) {
        bta16_off();
    } else {
        bta16_on();
    }
}

bool bta16_is_on(void)
{
    return g_triac_is_active;
}

void bta16_delay_ms(uint32_t ms)
{
#if defined(_WIN32)
    Sleep((DWORD)ms);
#else
    /* Портативна затримка для POSIX-систем */
    struct timespec req;
    req.tv_sec = ms / 1000;
    req.tv_nsec = (ms % 1000) * 1000000L;
    nanosleep(&req, NULL);
#endif
}
