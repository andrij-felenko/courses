#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

// Фізичні та часові константи CSMA/CA (у мікросекундах)
#define CSMA_SLOT_TIME_US       100      // Тривалість слота відкату
#define CSMA_DIFS_TIME_US       400      // Інтервал тиші DIFS
#define CSMA_ACK_TIMEOUT_US     2000     // Тайм-аут очікування ACK
#define CSMA_CW_MIN             7        // Мінімальне вікно (слотів: 0..7)
#define CSMA_CW_MAX             127      // Максимальне вікно (слотів: 0..127)
#define CSMA_MAX_RETRIES        4        // Максимум повторних спроб

typedef enum {
    CSMA_STATE_IDLE,            // Очікування нового пакета
    CSMA_STATE_WAIT_DIFS,       // Очікування безперервної тиші DIFS
    CSMA_STATE_BACKOFF,         // Зворотний відлік слотів
    CSMA_STATE_TRANSMITTING,    // Фізична передача кадру
    CSMA_STATE_WAIT_ACK,        // Очікування кадру підтвердження
    CSMA_STATE_FAILED,          // Помилка доставки (вичерпано ліміт спроб)
    CSMA_STATE_SUCCESS          // Пакет успішно доставлено й підтверджено
} csma_state_t;

// Інтерфейс апаратного трансивера (HAL)
typedef struct {
    bool (*is_channel_busy)(void);              // Читання CCA (RSSI понад поріг)
    void (*start_tx)(const uint8_t *p, uint8_t len); // Запуск передавача по DMA/SPI
    bool (*is_tx_done)(void);                   // Прапорець завершення TX
    uint32_t (*get_time_us)(void);              // Системний таймер мікросекунд
} csma_radio_hal_t;

typedef struct {
    csma_state_t state;
    uint32_t timer_start_us;
    uint32_t cw_current;
    uint32_t backoff_slots;
    uint8_t retry_count;
    const uint8_t *tx_data;
    uint8_t tx_len;
    csma_radio_hal_t hal;
} csma_mac_t;

void csma_mac_init(csma_mac_t *mac, csma_radio_hal_t hal) {
    mac->state = CSMA_STATE_IDLE;
    mac->cw_current = CSMA_CW_MIN;
    mac->retry_count = 0;
    mac->hal = hal;
}

bool csma_mac_send(csma_mac_t *mac, const uint8_t *data, uint8_t len) {
    if (mac->state != CSMA_STATE_IDLE && mac->state != CSMA_STATE_SUCCESS && mac->state != CSMA_STATE_FAILED) {
        return false; // Зайнято обробкою попереднього пакета
    }
    mac->tx_data = data;
    mac->tx_len = len;
    mac->retry_count = 0;
    mac->cw_current = CSMA_CW_MIN;
    mac->state = CSMA_STATE_WAIT_DIFS;
    mac->timer_start_us = mac->hal.get_time_us();
    return true;
}

// Викликається асинхронно в головному супер-циклі або за таймером
void csma_mac_process(csma_mac_t *mac) {
    uint32_t now = mac->hal.get_time_us();

    switch (mac->state) {
        case CSMA_STATE_WAIT_DIFS:
            if (mac->hal.is_channel_busy()) {
                // Ефір зайнятий — скидаємо таймер і чекаємо спочатку
                mac->timer_start_us = now;
            } else if ((now - mac->timer_start_us) >= CSMA_DIFS_TIME_US) {
                // Ефір чистий упродовж DIFS — генеруємо слоти відкату
                mac->backoff_slots = (uint32_t)rand() % (mac->cw_current + 1);
                mac->timer_start_us = now;
                mac->state = CSMA_STATE_BACKOFF;
            }
            break;

        case CSMA_STATE_BACKOFF:
            if (mac->hal.is_channel_busy()) {
                // Заморожування відліку: повертаємося до очікування DIFS
                mac->timer_start_us = now;
                mac->state = CSMA_STATE_WAIT_DIFS;
            } else if ((now - mac->timer_start_us) >= CSMA_SLOT_TIME_US) {
                mac->timer_start_us = now;
                if (mac->backoff_slots == 0) {
                    // Відлік вичерпано — починаємо передачу
                    mac->hal.start_tx(mac->tx_data, mac->tx_len);
                    mac->state = CSMA_STATE_TRANSMITTING;
                } else {
                    mac->backoff_slots--;
                }
            }
            break;

        case CSMA_STATE_TRANSMITTING:
            if (mac->hal.is_tx_done()) {
                mac->timer_start_us = now;
                mac->state = CSMA_STATE_WAIT_ACK;
            }
            break;

        case CSMA_STATE_WAIT_ACK:
            // Перевірка тайм-ауту відповіді
            if ((now - mac->timer_start_us) >= CSMA_ACK_TIMEOUT_US) {
                // ACK не надійшов — колізія або втрата пакета
                mac->retry_count++;
                if (mac->retry_count > CSMA_MAX_RETRIES) {
                    mac->state = CSMA_STATE_FAILED;
                } else {
                    // Експоненційне подвоєння вікна: CW = min(2*CW + 1, CW_MAX)
                    mac->cw_current = (mac->cw_current << 1) | 1;
                    if (mac->cw_current > CSMA_CW_MAX) {
                        mac->cw_current = CSMA_CW_MAX;
                    }
                    mac->state = CSMA_STATE_WAIT_DIFS;
                    mac->timer_start_us = now;
                }
            }
            break;

        case CSMA_STATE_IDLE:
        case CSMA_STATE_SUCCESS:
        case CSMA_STATE_FAILED:
            break;
    }
}

// Викликається з обробника переривання прийому пакетів при валідному ACK
void csma_mac_on_ack_received(csma_mac_t *mac) {
    if (mac->state == CSMA_STATE_WAIT_ACK) {
        mac->state = CSMA_STATE_SUCCESS;
        mac->cw_current = CSMA_CW_MIN; // Скидання вікна після успіху
    }
}
