/* ============================================================================
 * power_manager.c — Реалізація диспетчера та апаратної взаємодії
 * ============================================================================ */
#include "power_manager.h"
#include <string.h>

/* Псевдо-регістри та інтринсики Cortex-M для автономності прикладу */
#ifndef __NOP
#define __NOP()                 __asm volatile ("nop")
#define __WFI()                 __asm volatile ("wfi")
#define __DSB()                 __asm volatile ("dsb 0xF" ::: "memory")
#define __ISB()                 __asm volatile ("isb 0xF" ::: "memory")
#define __disable_irq()         __asm volatile ("cpsid i" : : : "memory")
#define __enable_irq()          __asm volatile ("cpsie i" : : : "memory")
#endif

#define MAX_PM_CLIENTS 16

static uint32_t s_locks[PM_LOCK_COUNT];
static const pm_driver_client_t *s_clients[MAX_PM_CLIENTS];
static size_t s_client_count = 0;

void pm_init(void) {
    memset(s_locks, 0, sizeof(s_locks));
    memset(s_clients, 0, sizeof(s_clients));
    s_client_count = 0;
}

bool pm_register_client(const pm_driver_client_t *client) {
    if (!client || s_client_count >= MAX_PM_CLIENTS) {
        return false;
    }
    s_clients[s_client_count++] = client;
    return true;
}

void pm_lock_acquire(pm_lock_t lock) {
    if (lock < PM_LOCK_COUNT) {
        __disable_irq();
        s_locks[lock]++;
        __enable_irq();
    }
}

void pm_lock_release(pm_lock_t lock) {
    if (lock < PM_LOCK_COUNT) {
        __disable_irq();
        if (s_locks[lock] > 0) {
            s_locks[lock]--;
        }
        __enable_irq();
    }
}

pm_mode_t pm_get_deepest_allowed_mode(void) {
    if (s_locks[PM_LOCK_NO_SLEEP] > 0)   return PM_MODE_ACTIVE;
    if (s_locks[PM_LOCK_NO_STOP] > 0)    return PM_MODE_SLEEP;
    if (s_locks[PM_LOCK_NO_STANDBY] > 0) return PM_MODE_STOP;
    return PM_MODE_STANDBY;
}

/* Відновлення високошвидкісного дерева тактування після пробудження з режиму STOP */
static void pm_restore_clock_tree(void) {
    /* 1. Запуск зовнішнього високочастотного кварцового генератора (HSE) */
    /* RCC->CR |= RCC_CR_HSEON; while (!(RCC->CR & RCC_CR_HSERDY)); */

    /* 2. Запуск помножувача частоти PLL */
    /* RCC->CR |= RCC_CR_PLLON; while (!(RCC->CR & RCC_CR_PLLRDY)); */

    /* 3. Перемикання системної шини SYSCLK на вихід PLL */
    /* RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL; */
}

/* Налаштування апаратного таймера низького споживання (LPTIM / RTC Wakeup) */
static void pm_setup_wakeup_timer(uint32_t ms) {
    /* Програмування регістрів авто-пробудження RTC Wakeup або LPTIM */
    (void)ms;
}

void pm_sleep_if_idle(uint32_t expected_idle_ms) {
    pm_mode_t target_mode = pm_get_deepest_allowed_mode();

    if (target_mode == PM_MODE_ACTIVE) {
        /* Сон повністю заблокований, повертаємося до виконання задач */
        return;
    }

    if (target_mode == PM_MODE_SLEEP) {
        /* Легкий сон: вимикаємо лише ядро, переривання миттєво піднімуть систему */
        __WFI();
        return;
    }

    /* Глибокий сон: вимагає узгодження з усіма периферійними клієнтами */
    size_t prepared_clients = 0;
    for (size_t i = 0; i < s_client_count; ++i) {
        if (s_clients[i]->pre_sleep) {
            if (!s_clients[i]->pre_sleep(target_mode)) {
                /* Клієнт відхилив вхід у сон — відкочуємо вже підготовлені модулі */
                for (size_t j = 0; j < prepared_clients; ++j) {
                    if (s_clients[j]->post_wakeup) {
                        s_clients[j]->post_wakeup(target_mode);
                    }
                }
                return;
            }
        }
        prepared_clients++;
    }

    /* Налаштовуємо джерело пробудження за часом */
    pm_setup_wakeup_timer(expected_idle_ms);

    /* АТОМАРНИЙ ВХІД: блокуємо виконання ISR, щоб уникнути гонитви переривань */
    __disable_irq();

    /* Перевіряємо, чи не з'явилися нові блокування за час підготовки клієнтів */
    if (pm_get_deepest_allowed_mode() >= target_mode) {
        /* Налаштування регістра керування системою Cortex-M System Control Register */
        /* SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk; */

        __DSB();
        __ISB();

        /* Перехід у глибокий сон: ядро засинає, але будь-яке виставлене переривання розбудить його */
        __WFI();

        /* Скидання біта глибокого сну після пробудження */
        /* SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk; */
    }

    /* 1. Відновлюємо тактування (HSE/PLL) ДО виклику обробників ISR */
    pm_restore_clock_tree();

    /* 2. Дозволяємо процесору виконати накопичені апаратні переривання */
    __enable_irq();

    /* 3. Сповіщаємо всі драйвери про повернення в активний режим */
    for (size_t i = 0; i < s_client_count; ++i) {
        if (s_clients[i]->post_wakeup) {
            s_clients[i]->post_wakeup(target_mode);
        }
    }
}
