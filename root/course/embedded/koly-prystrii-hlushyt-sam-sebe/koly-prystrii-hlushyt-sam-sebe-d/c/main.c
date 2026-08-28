#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ARBITER_MAX_DEVICES      4
#define ARBITER_RX_TIMEOUT_TICKS  5000 /* Захисний тайм-аут зависання прийому (мс/тіки) */

typedef enum {
    BUS_PRIORITY_LOW = 0,    /* Дисплей, фонове логування — глушити негайно */
    BUS_PRIORITY_MEDIUM,     /* Читання Flash — призупиняти за можливістю */
    BUS_PRIORITY_HIGH,       /* Силові датчики безпеки — не призупиняти */
    BUS_PRIORITY_CRITICAL    /* Аварійні переривання */
} bus_priority_t;

typedef enum {
    ARBITER_STATE_IDLE = 0,
    ARBITER_STATE_BUS_ACTIVE,
    ARBITER_STATE_RX_QUIET_ACTIVE,
    ARBITER_STATE_TIMEOUT_RECOVERY
} arbiter_state_t;

/* Зворотні виклики керування активністю периферійного пристрою */
typedef void (*bus_pause_fn_t)(void *context);
typedef void (*bus_resume_fn_t)(void *context);

typedef struct {
    const char     *name;
    bus_priority_t  priority;
    bus_pause_fn_t  pause_cb;
    bus_resume_fn_t resume_cb;
    void           *context;
    bool            is_paused;
} bus_device_t;

typedef struct {
    arbiter_state_t state;
    bus_device_t    devices[ARBITER_MAX_DEVICES];
    size_t          device_count;
    uint32_t        rx_start_tick;
    uint32_t        total_quiet_windows;
    uint32_t        timeout_count;
} bus_arbiter_t;

static bus_arbiter_t g_arbiter;

void bus_arbiter_init(void) {
    g_arbiter.state = ARBITER_STATE_IDLE;
    g_arbiter.device_count = 0;
    g_arbiter.rx_start_tick = 0;
    g_arbiter.total_quiet_windows = 0;
    g_arbiter.timeout_count = 0;
}

bool bus_arbiter_register_device(const char *name, bus_priority_t priority,
                                 bus_pause_fn_t pause_cb, bus_resume_fn_t resume_cb,
                                 void *context) {
    if (g_arbiter.device_count >= ARBITER_MAX_DEVICES) {
        return false;
    }
    bus_device_t *dev = &g_arbiter.devices[g_arbiter.device_count++];
    dev->name = name;
    dev->priority = priority;
    dev->pause_cb = pause_cb;
    dev->resume_cb = resume_cb;
    dev->context = context;
    dev->is_paused = false;
    return true;
}

/* Обробник входу в захищене вікно прийому (викликається з ISR детектора преамбули) */
void bus_arbiter_on_radio_rx_start(uint32_t current_tick) {
    g_arbiter.state = ARBITER_STATE_RX_QUIET_ACTIVE;
    g_arbiter.rx_start_tick = current_tick;
    g_arbiter.total_quiet_windows++;

    /* Зупиняємо всі шини низького та середнього пріоритету */
    for (size_t i = 0; i < g_arbiter.device_count; ++i) {
        bus_device_t *dev = &g_arbiter.devices[i];
        if (dev->priority <= BUS_PRIORITY_MEDIUM && !dev->is_paused) {
            if (dev->pause_cb) {
                dev->pause_cb(dev->context);
            }
            dev->is_paused = true;
        }
    }
}

/* Обробник завершення прийому пакета (викликається з ISR завершення кадру/CRC) */
void bus_arbiter_on_radio_rx_end(void) {
    if (g_arbiter.state != ARBITER_STATE_RX_QUIET_ACTIVE) {
        return;
    }

    /* Відновлюємо роботу всіх призупинених шин */
    for (size_t i = 0; i < g_arbiter.device_count; ++i) {
        bus_device_t *dev = &g_arbiter.devices[i];
        if (dev->is_paused) {
            if (dev->resume_cb) {
                dev->resume_cb(dev->context);
            }
            dev->is_paused = false;
        }
    }
    g_arbiter.state = ARBITER_STATE_IDLE;
}

/* Періодичний сторож для захисту від зависання приймача без події RX_END */
void bus_arbiter_poll_watchdog(uint32_t current_tick) {
    if (g_arbiter.state == ARBITER_STATE_RX_QUIET_ACTIVE) {
        if ((current_tick - g_arbiter.rx_start_tick) > ARBITER_RX_TIMEOUT_TICKS) {
            g_arbiter.timeout_count++;
            g_arbiter.state = ARBITER_STATE_TIMEOUT_RECOVERY;
            bus_arbiter_on_radio_rx_end();
        }
    }
}
