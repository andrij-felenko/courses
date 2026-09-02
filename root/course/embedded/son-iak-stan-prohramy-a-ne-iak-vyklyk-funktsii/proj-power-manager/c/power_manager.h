/* power_manager.h — диспетчер енергозбереження: режими, блокування, хуки драйверів.
 * Ціль: STM32L4 (Cortex-M4), SYSCLK 80 МГц від HSE+PLL, RTC на LSE 32768 Гц. */
#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Точка беззбитковості: перезапуск HSE+PLL коштує близько 2 мс і сотень мікроджоулів,
 * тож простій, коротший за цей горизонт, дешевше пересидіти в звичайному WFI. */
#define PM_BREAKEVEN_MS 3u

/* Рівні енергозбереження мікроконтролера */
typedef enum {
    PM_MODE_ACTIVE = 0, /* ядро та периферія активні */
    PM_MODE_SLEEP,      /* зупинено лише ядро (WFI), PLL і периферія живі */
    PM_MODE_STOP,       /* PLL зупинено, SRAM збережено, регулятор у режимі LP */
    PM_MODE_STANDBY     /* домен ядра знеструмлено, пробудження = рестарт */
} pm_mode_t;

/* Типи блокувань. Драйвер бере те, без чого його транзакція розсиплеться. */
typedef enum {
    PM_LOCK_NO_SLEEP   = 0, /* заборонено навіть зупиняти ядро */
    PM_LOCK_NO_STOP    = 1, /* потрібні PLL і тактування шин APB */
    PM_LOCK_NO_STANDBY = 2, /* потрібен уміст SRAM */
    PM_LOCK_COUNT
} pm_lock_t;

/* Хуки життєвого циклу периферійного драйвера */
typedef struct {
    const char *name;
    /* Перед зупинкою тактування. false — вхід у сон скасовується цілком. */
    bool (*pre_sleep)(pm_mode_t target_mode);
    /* Після відновлення дерева тактування, до повернення керування задачам. */
    void (*post_wakeup)(pm_mode_t from_mode);
} pm_driver_client_t;

void      pm_init(void);
bool      pm_register_client(const pm_driver_client_t *client);

void      pm_lock_acquire(pm_lock_t lock);
void      pm_lock_release(pm_lock_t lock);
uint32_t  pm_lock_count(pm_lock_t lock);
/* Скільки разів release викликали при нульовому лічильнику — чиста ознака
 * розпареного acquire/release у драйвері. Дивитися в діагностиці. */
uint32_t  pm_lock_underflows(void);

pm_mode_t pm_get_deepest_allowed_mode(void);

/* Головний вхід із циклу простою: expected_idle_ms — горизонт до найближчої
 * запланованої події (мінімум по всіх таймерах і тайм-аутах задач). */
void      pm_sleep_if_idle(uint32_t expected_idle_ms);

/* Явний перехід у STANDBY: рішення застосунку, а не диспетчера, бо пробудження
 * еквівалентне перезапуску. Повертає false, якщо драйвер відмовив; інакше не
 * повертається взагалі. */
bool      pm_enter_standby(uint32_t wakeup_after_ms);

/* Діагностика: скільки разів систему підняв не таймер, а периферія,
 * і скільки разів дерево тактування піднімалося не з першої спроби. */
uint32_t  pm_early_wakeups(void);
uint32_t  pm_clock_faults(void);

#endif /* POWER_MANAGER_H */
