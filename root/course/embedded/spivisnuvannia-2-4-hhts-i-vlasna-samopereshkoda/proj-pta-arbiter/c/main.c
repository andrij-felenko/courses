#include <stdint.h>
#include <stdbool.h>

/* Апаратні часові константи інтерфейсу PTA */
#define PTA_REQ_LEAD_TIME_US   30
#define PTA_GRANT_TIMEOUT_US   100

typedef enum {
    PTA_PRIORITY_LOW = 0,
    PTA_PRIORITY_HIGH = 1
} pta_priority_t;

typedef enum {
    PTA_STATE_IDLE = 0,
    PTA_STATE_REQUESTING,
    PTA_STATE_GRANTED,
    PTA_STATE_DENIED,
    PTA_STATE_ABORTED
} pta_state_t;

typedef struct {
    uint8_t pin_req;
    uint8_t pin_pri;
    uint8_t pin_gnt;
    pta_state_t state;
    pta_priority_t current_priority;
} pta_driver_t;

/* Низькорівневі виклики апаратного рівня (HAL) */
extern void hal_gpio_write(uint8_t pin, bool level);
extern bool hal_gpio_read(uint8_t pin);
extern void hal_delay_us(uint32_t us);
extern void hal_radio_abort_tx(void);

void pta_init(pta_driver_t *drv, uint8_t req, uint8_t pri, uint8_t gnt) {
    drv->pin_req = req;
    drv->pin_pri = pri;
    drv->pin_gnt = gnt;
    drv->state = PTA_STATE_IDLE;
    drv->current_priority = PTA_PRIORITY_LOW;

    hal_gpio_write(drv->pin_req, false);
    hal_gpio_write(drv->pin_pri, false);
}

bool pta_request_access(pta_driver_t *drv, pta_priority_t pri, uint32_t timeout_us) {
    drv->current_priority = pri;
    drv->state = PTA_STATE_REQUESTING;

    /* 1. Виставляємо пріоритет перед підняттям запиту */
    hal_gpio_write(drv->pin_pri, (pri == PTA_PRIORITY_HIGH));
    hal_gpio_write(drv->pin_req, true);

    /* 2. Забезпечуємо мінімальний час попередження для Wi-Fi арбітра */
    hal_delay_us(PTA_REQ_LEAD_TIME_US);

    /* 3. Опитування лінії підтвердження COEX_GNT */
    uint32_t elapsed = 0;
    while (elapsed < timeout_us) {
        if (hal_gpio_read(drv->pin_gnt)) {
            drv->state = PTA_STATE_GRANTED;
            return true;
        }
        hal_delay_us(5);
        elapsed += 5;
    }

    /* Доступ відхилено або таймаут — знімаємо запит */
    hal_gpio_write(drv->pin_req, false);
    hal_gpio_write(drv->pin_pri, false);
    drv->state = PTA_STATE_DENIED;
    return false;
}

void pta_release_access(pta_driver_t *drv) {
    hal_gpio_write(drv->pin_req, false);
    hal_gpio_write(drv->pin_pri, false);
    drv->state = PTA_STATE_IDLE;
}

/* Обробник апаратного переривання на спадний фронт лінії COEX_GNT */
void pta_grant_lost_isr(pta_driver_t *drv) {
    if (drv->state == PTA_STATE_GRANTED) {
        /* Екстрена зупинка радіотракту при відкликанні дозволу арбітром */
        hal_radio_abort_tx();
        hal_gpio_write(drv->pin_req, false);
        hal_gpio_write(drv->pin_pri, false);
        drv->state = PTA_STATE_ABORTED;
    }
}
