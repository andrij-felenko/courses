/* power_monitor.h - Модуль діагностики та захисту вхідного живлення (C99/C11) */
#ifndef POWER_MONITOR_H
#define POWER_MONITOR_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PWR_STATE_OFF = 0,
    PWR_STATE_STARTING,
    PWR_STATE_NORMAL,
    PWR_STATE_FAULT_UVLO,
    PWR_STATE_FAULT_OVLO,
    PWR_STATE_FAULT_HARDWARE
} PowerState_t;

typedef struct {
    uint32_t uvlo_cutoff_mv;    /* Поріг відключення за низькою напругою (мВ) */
    uint32_t uvlo_recovery_mv;  /* Поріг повернення з UVLO з гістерезисом (мВ) */
    uint32_t ovlo_cutoff_mv;    /* Поріг відключення за перенапругою (мВ) */
    uint32_t ovlo_recovery_mv;  /* Поріг повернення з OVLO (мВ) */
    uint16_t adc_vref_mv;       /* Опорна напруга АЦП (типово 3300 мВ) */
    uint16_t divider_top_k;     /* Верхнє плече дільника (кОм, наприклад 110) */
    uint16_t divider_bottom_k;  /* Нижнє плече дільника (кОм, наприклад 10) */
    uint8_t  filter_shift;      /* Коефіцієнт IIR-фільтра (EMA: 1/2^shift) */
} PowerConfig_t;

typedef struct {
    PowerConfig_t config;
    PowerState_t  state;
    uint32_t      filtered_adc_raw;
    uint32_t      voltage_in_mv;
    uint32_t      fault_counter;
    bool          switch_enabled;
    void        (*set_switch_fn)(bool enable);
} PowerMonitor_t;

void PowerMonitor_Init(PowerMonitor_t *mon, const PowerConfig_t *cfg, void (*switch_ctrl)(bool));
void PowerMonitor_ProcessADC(PowerMonitor_t *mon, uint16_t raw_adc_sample);
void PowerMonitor_HandleHardwareFault(PowerMonitor_t *mon);
PowerState_t PowerMonitor_GetState(const PowerMonitor_t *mon);
uint32_t PowerMonitor_GetVoltageMv(const PowerMonitor_t *mon);

#ifdef __cplusplus
}
#endif

#endif /* POWER_MONITOR_H */
