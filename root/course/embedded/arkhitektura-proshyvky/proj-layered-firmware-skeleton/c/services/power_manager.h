// services/power_manager.h — служба керування живленням.
// Підписана на EVT_SENSOR_FAULT: витягнувши подію несправності, вона знеструмлює
// лінію давачів ключем MOSFET і піднімає її знову — без перезавантаження всієї прошивки.
#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include "bsp/bsp_power.h"
#include "hal/hal_time.h"
#include "services/event_dispatcher.h"

// Драйвер після знеструмлення треба налаштувати наново. Служба не знає, який саме
// це давач: їй передають функцію переналаштування й контекст.
typedef bool (*power_manager_reinit_fn)(void* context);
typedef void (*power_manager_recovered_fn)(void* context);

typedef struct {
    bsp_power_t* rail;
    hal_time_t time;

    power_manager_reinit_fn reinit;
    void* reinit_context;

    power_manager_recovered_fn on_recovered;  // Кому сказати, що давач знову живий
    void* recovered_context;

    uint32_t min_interval_ms;  // Захист від безперервного клацання ключем
    uint32_t last_cycle_ms;
    bool cycled_once;

    uint32_t cycles_done;
    uint32_t cycles_failed;
    uint32_t cycles_suppressed;
} power_manager_t;

void power_manager_init(power_manager_t* pm, bsp_power_t* rail, hal_time_t time,
                        uint32_t min_interval_ms);

void power_manager_set_reinit(power_manager_t* pm, power_manager_reinit_fn fn, void* context);
void power_manager_set_recovered(power_manager_t* pm, power_manager_recovered_fn fn, void* context);

// Перехідник під таблицю підписників диспетчера.
void power_manager_event_handler(void* context, const event_t* evt);

// Зареєструвати службу в диспетчері на подію несправності.
bool power_manager_attach(power_manager_t* pm, event_dispatcher_t* dispatcher);

#endif  // POWER_MANAGER_H
