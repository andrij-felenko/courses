/* power_manager.c — облік блокувань, узгодження з драйверами, апаратний перехід. */
#include "power_manager.h"
#include "rtc_wakeup.h"
#include "sys_tick.h"

#include "stm32l4xx.h"
#include <string.h>

#define MAX_PM_CLIENTS 8u
/* Очікування прапорців RCC йде на MSI 4 МГц, без будь-якого таймбейсу:
 * лічильник обертів — єдине, що тут працює. ~200k обертів ≈ 100 мс. */
#define RCC_SPINS 200000u

static uint32_t s_locks[PM_LOCK_COUNT];
static uint32_t s_lock_underflows;
static const pm_driver_client_t *s_clients[MAX_PM_CLIENTS];
static size_t   s_client_count;
static uint32_t s_early_wakeups;
static uint32_t s_clock_faults;

static uint32_t critical_enter(void)
{
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    return primask;
}

static void critical_exit(uint32_t primask)
{
    __set_PRIMASK(primask);
}

void pm_init(void)
{
    memset(s_locks, 0, sizeof(s_locks));
    memset(s_clients, 0, sizeof(s_clients));
    s_client_count = 0;

    /* Доступ до блоку керування живленням */
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN;
    (void)RCC->APB1ENR1;

    /* Прибираємо прапорець пробудження від попереднього циклу: якщо його лишити,
     * найближчий вхід у STOP/STANDBY завершиться миттєвим виходом. */
    PWR->SCR = PWR_SCR_CWUF;

    rtc_wakeup_init();
}

bool pm_register_client(const pm_driver_client_t *client)
{
    if (!client || s_client_count >= MAX_PM_CLIENTS) {
        return false;
    }
    s_clients[s_client_count++] = client;
    return true;
}

void pm_lock_acquire(pm_lock_t lock)
{
    if (lock >= PM_LOCK_COUNT) {
        return;
    }
    uint32_t primask = critical_enter();
    s_locks[lock]++;
    critical_exit(primask);
}

void pm_lock_release(pm_lock_t lock)
{
    if (lock >= PM_LOCK_COUNT) {
        return;
    }
    uint32_t primask = critical_enter();
    if (s_locks[lock] > 0u) {
        s_locks[lock]--;
    } else {
        /* Зайвий release небезпечніший за витік: він знімає чужу заборону. */
        s_lock_underflows++;
    }
    critical_exit(primask);
}

uint32_t pm_lock_count(pm_lock_t lock)
{
    return (lock < PM_LOCK_COUNT) ? s_locks[lock] : 0u;
}

uint32_t pm_lock_underflows(void) { return s_lock_underflows; }
uint32_t pm_early_wakeups(void)   { return s_early_wakeups; }
uint32_t pm_clock_faults(void)    { return s_clock_faults; }

pm_mode_t pm_get_deepest_allowed_mode(void)
{
    if (s_locks[PM_LOCK_NO_SLEEP] > 0u)   return PM_MODE_ACTIVE;
    if (s_locks[PM_LOCK_NO_STOP] > 0u)    return PM_MODE_SLEEP;
    if (s_locks[PM_LOCK_NO_STANDBY] > 0u) return PM_MODE_STOP;
    return PM_MODE_STANDBY;
}

/* ---- дерево тактування ---------------------------------------------------- */

static bool spin_until_set(volatile uint32_t *reg, uint32_t mask)
{
    for (uint32_t i = 0; i < RCC_SPINS; ++i) {
        if ((*reg & mask) != 0u) {
            return true;
        }
    }
    return false;
}

/* Після STOP ядро йде від MSI 4 МГц. Поки SYSCLK не повернувся на PLL,
 * будь-яке звертання до периферії дає биті швидкості обміну. */
static bool restore_clock_tree(void)
{
    if ((RCC->CFGR & RCC_CFGR_SWS) == RCC_CFGR_SWS_PLL) {
        return true; /* сон був неглибокий, дерево не падало */
    }

    /* Затримку читання Flash піднімаємо ДО частоти, а не після. */
    FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_LATENCY_4WS;

    RCC->CR |= RCC_CR_HSEON;
    if (!spin_until_set(&RCC->CR, RCC_CR_HSERDY)) {
        RCC->CR &= ~RCC_CR_HSEON;
        return false;
    }

    /* Коефіцієнти PLLCFGR переживають STOP — домен VCORE збережено,
     * тож множник і дільники перезаписувати не треба, лише ввімкнути. */
    RCC->CR |= RCC_CR_PLLON;
    if (!spin_until_set(&RCC->CR, RCC_CR_PLLRDY)) {
        RCC->CR &= ~RCC_CR_PLLON;
        RCC->CR &= ~RCC_CR_HSEON;
        return false;
    }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    for (uint32_t i = 0; i < RCC_SPINS; ++i) {
        if ((RCC->CFGR & RCC_CFGR_SWS) == RCC_CFGR_SWS_PLL) {
            return true;
        }
    }
    return false;
}

static void restore_clock_tree_or_reset(void)
{
    if (restore_clock_tree()) {
        return;
    }
    s_clock_faults++;
    if (restore_clock_tree()) {
        return; /* друга спроба: кварц інколи піднімається довше за розрахунок */
    }
    /* Іти далі нікуди: периферія налаштована на 80 МГц, а шина йде від MSI 4 МГц.
     * Чесний перезапуск кращий за годину мовчазно спотвореної телеметрії. */
    NVIC_SystemReset();
}

/* ---- узгодження з драйверами --------------------------------------------- */

static bool prepare_clients(pm_mode_t target)
{
    for (size_t i = 0; i < s_client_count; ++i) {
        const pm_driver_client_t *c = s_clients[i];
        if (c->pre_sleep && !c->pre_sleep(target)) {
            /* Відкат у зворотному порядку — так само, як розкручують стек. */
            for (size_t j = i; j-- > 0;) {
                if (s_clients[j]->post_wakeup) {
                    s_clients[j]->post_wakeup(target);
                }
            }
            return false;
        }
    }
    return true;
}

static void restore_clients(pm_mode_t from_mode)
{
    for (size_t i = s_client_count; i-- > 0;) {
        if (s_clients[i]->post_wakeup) {
            s_clients[i]->post_wakeup(from_mode);
        }
    }
}

/* ---- апаратний перехід ---------------------------------------------------- */

static void enter_low_power(pm_mode_t mode)
{
    uint32_t lpms = (mode == PM_MODE_STANDBY) ? PWR_CR1_LPMS_STANDBY
                                              : PWR_CR1_LPMS_STOP1;
    PWR->CR1 = (PWR->CR1 & ~PWR_CR1_LPMS) | lpms;
    PWR->SCR = PWR_SCR_CWUF;

    SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
    __DSB();
    __ISB();
    __WFI();
    /* Сюди повертаємося лише з STOP: із STANDBY виходять через рестарт. */
    SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
}

void pm_sleep_if_idle(uint32_t expected_idle_ms)
{
    pm_mode_t target = pm_get_deepest_allowed_mode();

    if (target == PM_MODE_ACTIVE) {
        return; /* сон заборонено, повертаємося в цикл задач */
    }
    if (target == PM_MODE_STANDBY) {
        /* Втрату SRAM диспетчер сам не призначає — це рішення застосунку. */
        target = PM_MODE_STOP;
    }
    if (target == PM_MODE_SLEEP || expected_idle_ms < PM_BREAKEVEN_MS) {
        __WFI(); /* легкий сон: перше ж переривання підніме ядро миттєво */
        return;
    }

    if (!prepare_clients(target)) {
        return; /* драйвер відмовив, підготовлені вже відкочені */
    }

    /* SysTick мусить замовкнути: інакше він розбудить нас через мілісекунду. */
    sys_tick_suspend();
    uint32_t horizon_ms = rtc_wakeup_arm(expected_idle_ms);

    uint32_t slept_ms = 0;
    uint32_t primask  = critical_enter();

    /* Перевірка після хуків: переривання могло взяти блокування, поки
     * драйвери готувалися, і тоді засинати вже не можна. */
    if (pm_get_deepest_allowed_mode() >= target) {
        enter_low_power(target);
        slept_ms = rtc_wakeup_elapsed_ms();
    }
    rtc_wakeup_disarm();

    /* 1. Спершу частота — і лише потім будь-що інше. */
    restore_clock_tree_or_reset();
    /* 2. Компенсація лічильника тіків: планувальник не має помітити пропуску. */
    sys_tick_resume(slept_ms);

    if (slept_ms + 1u < horizon_ms) {
        s_early_wakeups++; /* підняв не таймер, а периферія */
    }

    /* 3. Аж тепер накопичені ISR виконуються — на правильній частоті. */
    critical_exit(primask);

    restore_clients(target);
}

bool pm_enter_standby(uint32_t wakeup_after_ms)
{
    if (!prepare_clients(PM_MODE_STANDBY)) {
        return false;
    }
    sys_tick_suspend();
    (void)rtc_wakeup_arm(wakeup_after_ms);

    __disable_irq();
    enter_low_power(PM_MODE_STANDBY);

    /* Якщо ми тут — STANDBY не відбувся (наприклад, висів невичищений WUF).
     * Повертаємо систему в робочий стан, а не лишаємо напівмертвою. */
    rtc_wakeup_disarm();
    restore_clock_tree_or_reset();
    sys_tick_resume(0);
    __enable_irq();
    restore_clients(PM_MODE_STANDBY);
    return false;
}
