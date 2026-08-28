#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    MODEM_RAT_2G_GSM = 12,
    MODEM_RAT_4G_LTE = 28,
    MODEM_RAT_5G_NR  = 30,
    MODEM_RAT_AUTO   = 255
} ModemRat_t;

typedef enum {
    STATE_POWER_OFF,
    STATE_PULSE_PWRKEY,
    STATE_WAIT_BOOT,
    STATE_SYNC_AT,
    STATE_CONFIG_RAT,
    STATE_WAIT_NETWORK,
    STATE_TRANSMIT_DATA,
    STATE_ENTER_PSM,
    STATE_ERROR_RECOVERY
} FsmState_t;

typedef struct {
    FsmState_t state;
    ModemRat_t target_rat;
    uint32_t   state_timer_ms;
    uint32_t   backoff_interval_ms;
    uint8_t    retry_count;
    bool       network_registered;
    int16_t    rsrp_dbm;
    int8_t     rsrq_db;
} ModemDriver_t;

/* Апаратні виклики платформи (BSP) */
extern void bsp_gpio_set_pwrkey(bool level);
extern void bsp_gpio_set_dtr(bool level);
extern void bsp_uart_send_string(const char *str);
extern uint32_t bsp_get_tick_ms(void);

void modem_init(ModemDriver_t *drv, ModemRat_t rat) {
    drv->state = STATE_POWER_OFF;
    drv->target_rat = rat;
    drv->state_timer_ms = 0;
    drv->backoff_interval_ms = 1000;
    drv->retry_count = 0;
    drv->network_registered = false;
    drv->rsrp_dbm = -140;
    drv->rsrq_db = -20;
}

void modem_fsm_step(ModemDriver_t *drv, const char *uart_rx_line) {
    uint32_t now = bsp_get_tick_ms();

    switch (drv->state) {
        case STATE_POWER_OFF:
            bsp_gpio_set_pwrkey(true);
            drv->state_timer_ms = now;
            drv->state = STATE_PULSE_PWRKEY;
            break;

        case STATE_PULSE_PWRKEY:
            /* Імпульс PWRKEY тривалістю 800 мс для запуску внутрішнього PMIC */
            if (now - drv->state_timer_ms >= 800) {
                bsp_gpio_set_pwrkey(false);
                drv->state_timer_ms = now;
                drv->state = STATE_WAIT_BOOT;
            }
            break;

        case STATE_WAIT_BOOT:
            /* Очікування виходу інтерфейсу UART на робочий режим (2500 мс) */
            if (now - drv->state_timer_ms >= 2500) {
                drv->retry_count = 0;
                bsp_uart_send_string("ATE0\r\n");
                drv->state_timer_ms = now;
                drv->state = STATE_SYNC_AT;
            }
            break;

        case STATE_SYNC_AT:
            if (uart_rx_line && strstr(uart_rx_line, "OK")) {
                /* Налаштування покоління зв'язку через 3GPP команду +WS46 */
                if (drv->target_rat == MODEM_RAT_4G_LTE) {
                    bsp_uart_send_string("AT+WS46=28\r\n");
                } else if (drv->target_rat == MODEM_RAT_2G_GSM) {
                    bsp_uart_send_string("AT+WS46=12\r\n");
                } else {
                    bsp_uart_send_string("AT+WS46=255\r\n");
                }
                drv->state_timer_ms = now;
                drv->state = STATE_CONFIG_RAT;
            } else if (now - drv->state_timer_ms > 1000) {
                if (++drv->retry_count > 10) {
                    drv->state = STATE_ERROR_RECOVERY;
                } else {
                    bsp_uart_send_string("AT\r\n");
                    drv->state_timer_ms = now;
                }
            }
            break;

        case STATE_CONFIG_RAT:
            if (uart_rx_line && strstr(uart_rx_line, "OK")) {
                /* Увімкнення URC сповіщень реєстрації у 4G та перевірка мережі */
                bsp_uart_send_string("AT+CEREG=2;+CESQ\r\n");
                drv->state_timer_ms = now;
                drv->state = STATE_WAIT_NETWORK;
            } else if (now - drv->state_timer_ms > 3000) {
                drv->state = STATE_ERROR_RECOVERY;
            }
            break;

        case STATE_WAIT_NETWORK:
            if (uart_rx_line) {
                if (strstr(uart_rx_line, "+CEREG: 2,1") || strstr(uart_rx_line, "+CEREG: 2,5")) {
                    drv->network_registered = true;
                    drv->state = STATE_TRANSMIT_DATA;
                }
            }
            if (now - drv->state_timer_ms > 60000) {
                /* Тайм-аут пошуку мережі (60 с) -> перехід у сон для збереження АКБ */
                drv->state = STATE_ERROR_RECOVERY;
            }
            break;

        case STATE_TRANSMIT_DATA:
            /* Відправка бінарного телеметричного кадру на сервер */
            bsp_uart_send_string("AT+QMTOPEN=...\r\n");
            drv->state = STATE_ENTER_PSM;
            break;

        case STATE_ENTER_PSM:
            /* Активація режиму глибокого сну PSM з періодом 24 години */
            bsp_uart_send_string("AT+CPSMS=1,,,\"00111000\",\"00000010\"\r\n");
            bsp_gpio_set_dtr(true); /* Дозволити модему заснути по лінії DTR */
            break;

        case STATE_ERROR_RECOVERY:
            /* Експоненційний відступ: подвоєння паузи до максимуму 15 хвилин */
            drv->backoff_interval_ms = (drv->backoff_interval_ms * 2 < 900000) 
                                       ? drv->backoff_interval_ms * 2 : 900000;
            bsp_gpio_set_dtr(true);
            drv->state = STATE_POWER_OFF;
            break;
    }
}
