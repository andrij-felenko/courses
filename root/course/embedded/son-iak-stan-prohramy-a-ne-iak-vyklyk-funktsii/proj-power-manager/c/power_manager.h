/* ============================================================================
 * power_manager.h — Диспетчер енергозбереження на мові C
 * ============================================================================ */
#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Рівні енергозбереження мікроконтролера */
typedef enum {
    PM_MODE_ACTIVE = 0, /* Ядро та периферія активні */
    PM_MODE_SLEEP,      /* Ядро зупинено, периферія та PLL активні */
    PM_MODE_STOP,       /* PLL зупинено, SRAM збережено, мікроспоживання */
    PM_MODE_STANDBY     /* Повне знеструмлення ядра, рестарт по RTC */
} pm_mode_t;

/* Типи блокувань енергозбереження */
typedef enum {
    PM_LOCK_NO_SLEEP   = 0, /* Заборона навіть легкого сну (WFI) */
    PM_LOCK_NO_STOP    = 1, /* Заборона переходу в STOP (потрібні PLL або APB) */
    PM_LOCK_NO_STANDBY = 2, /* Заборона переходу в STANDBY (потрібна пам'ять SRAM) */
    PM_LOCK_COUNT
} pm_lock_t;

/* Структура хуків життєвого циклу периферійного драйвера */
typedef struct {
    const char *name;
    /* Викликається перед зупинкою тактування. Якщо повертає false — вхід скасовується */
    bool (*pre_sleep)(pm_mode_t target_mode);
    /* Викликається після відновлення PLL та системної частоти */
    void (*post_wakeup)(pm_mode_t from_mode);
} pm_driver_client_t;

/* Ініціалізація диспетчера живлення */
void pm_init(void);

/* Реєстрація клієнта (драйвера периферії) */
bool pm_register_client(const pm_driver_client_t *client);

/* Захоплення блокування (збільшує лічильник відповідного блокування) */
void pm_lock_acquire(pm_lock_t lock);

/* Звільнення блокування (зменшує лічильник) */
void pm_lock_release(pm_lock_t lock);

/* Опитування найглибшого дозволеного режиму сну */
pm_mode_t pm_get_deepest_allowed_mode(void);

/* Головна функція диспетчера: оцінює блокування та атомарно занурює систему в сон */
void pm_sleep_if_idle(uint32_t expected_idle_ms);

#ifdef __cplusplus
}
#endif

#endif /* POWER_MANAGER_H */
