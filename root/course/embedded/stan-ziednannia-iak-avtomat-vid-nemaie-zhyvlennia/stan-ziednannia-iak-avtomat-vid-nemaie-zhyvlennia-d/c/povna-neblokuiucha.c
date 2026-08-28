#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Перелік станів життєвого циклу */
typedef enum {
    FSM_STATE_NO_POWER = 0,
    FSM_STATE_POWERING_ON,
    FSM_STATE_MODEM_READY,
    FSM_STATE_SIM_READY,
    FSM_STATE_NET_SEARCH,
    FSM_STATE_IP_ATTACH,
    FSM_STATE_TCP_CONNECT,
    FSM_STATE_READY_TO_SEND,
    FSM_STATE_SENDING,
    FSM_STATE_BACKOFF_WAIT,
    FSM_STATE_ERROR_RECOVERY
} conn_state_t;

/* Внутрішні події автомата */
typedef enum {
    EV_NONE = 0,
    EV_START_CONNECT,
    EV_TIMEOUT,
    EV_AT_OK,
    EV_AT_ERROR,
    EV_NET_REGISTERED,
    EV_NET_DENIED,
    EV_IP_ALLOCATED,
    EV_TCP_CONNECTED,
    EV_SOCKET_CLOSED,
    EV_TX_SUCCESS
} conn_event_t;

/* Структура контексту автомата */
typedef struct {
    conn_state_t state;
    conn_state_t rollback_target;
    uint32_t     state_enter_ms;
    uint32_t     timeout_ms;
    uint8_t      retry_count;
    uint8_t      max_retries;
    uint32_t     backoff_base_ms;
    uint32_t     backoff_wait_ms;
    bool         power_fet_status;
} conn_fsm_t;

/* Прототипи апаратного абстрактного рівня (HAL) */
void hal_modem_power_set(bool enable);
void hal_modem_pwrkey_pulse(void);
void hal_uart_send_cmd(const char *cmd);
uint32_t hal_get_tick_ms(void);
uint32_t hal_random_range(uint32_t min, uint32_t max);

/* Ініціалізація структури автомата */
void conn_fsm_init(conn_fsm_t *fsm) {
    memset(fsm, 0, sizeof(conn_fsm_t));
    fsm->state = FSM_STATE_NO_POWER;
    fsm->max_retries = 3;
    fsm->backoff_base_ms = 2000;
}

/* Зміна стану з оновленням лічильників */
static void fsm_set_state(conn_fsm_t *fsm, conn_state_t new_state, uint32_t timeout_ms) {
    fsm->state = new_state;
    fsm->state_enter_ms = hal_get_tick_ms();
    fsm->timeout_ms = timeout_ms;
}

/* Розрахунок інтервалу експоненційного відкату з джиттером */
static void fsm_enter_backoff(conn_fsm_t *fsm, conn_state_t retry_state) {
    uint32_t max_interval = fsm->backoff_base_ms * (1 << fsm->retry_count);
    if (max_interval > 300000) max_interval = 300000; // Стеля 5 хв

    fsm->backoff_wait_ms = hal_random_range(500, max_interval);
    fsm->rollback_target = retry_state;
    fsm_set_state(fsm, FSM_STATE_BACKOFF_WAIT, fsm->backoff_wait_ms);
}

/* Головний квантований крок автомата (Tick) */
void conn_fsm_step(conn_fsm_t *fsm, conn_event_t event) {
    uint32_t now = hal_get_tick_ms();

    /* Перевірка таймауту перебування у стані */
    if (fsm->timeout_ms > 0 && (now - fsm->state_enter_ms >= fsm->timeout_ms)) {
        event = EV_TIMEOUT;
    }

    switch (fsm->state) {
        case FSM_STATE_NO_POWER:
            if (event == EV_START_CONNECT) {
                hal_modem_power_set(true);
                fsm->power_fet_status = true;
                hal_modem_pwrkey_pulse();
                fsm_set_state(fsm, FSM_STATE_POWERING_ON, 3000);
            }
            break;

        case FSM_STATE_POWERING_ON:
            if (event == EV_TIMEOUT) {
                // Імпульс завершено, починаємо перевірку зв'язку
                hal_uart_send_cmd("ATE0\r\n");
                fsm_set_state(fsm, FSM_STATE_MODEM_READY, 1000);
            }
            break;

        case FSM_STATE_MODEM_READY:
            if (event == EV_AT_OK) {
                fsm->retry_count = 0;
                hal_uart_send_cmd("AT+CPIN?\r\n");
                fsm_set_state(fsm, FSM_STATE_SIM_READY, 5000);
            } else if (event == EV_TIMEOUT || event == EV_AT_ERROR) {
                if (++fsm->retry_count >= fsm->max_retries) {
                    // Апаратне зависання UART: ескалація в скидання живлення
                    fsm_set_state(fsm, FSM_STATE_ERROR_RECOVERY, 0);
                } else {
                    hal_uart_send_cmd("AT\r\n");
                    fsm_set_state(fsm, FSM_STATE_MODEM_READY, 1000);
                }
            }
            break;

        case FSM_STATE_SIM_READY:
            if (event == EV_AT_OK) {
                fsm->retry_count = 0;
                hal_uart_send_cmd("AT+CREG=1\r\n");
                fsm_set_state(fsm, FSM_STATE_NET_SEARCH, 60000);
            } else if (event == EV_TIMEOUT || event == EV_AT_ERROR) {
                // Помилка SIM-карти: повторити через паузу
                fsm_enter_backoff(fsm, FSM_STATE_MODEM_READY);
            }
            break;

        case FSM_STATE_NET_SEARCH:
            if (event == EV_NET_REGISTERED) {
                fsm->retry_count = 0;
                hal_uart_send_cmd("AT+CGATT=1\r\n");
                fsm_set_state(fsm, FSM_STATE_IP_ATTACH, 30000);
            } else if (event == EV_TIMEOUT || event == EV_NET_DENIED) {
                // Радіо-збій: відкат з експоненційним очікуванням
                if (++fsm->retry_count >= fsm->max_retries) {
                    fsm_set_state(fsm, FSM_STATE_ERROR_RECOVERY, 0);
                } else {
                    fsm_enter_backoff(fsm, FSM_STATE_NET_SEARCH);
                }
            }
            break;

        case FSM_STATE_IP_ATTACH:
            if (event == EV_IP_ALLOCATED) {
                fsm->retry_count = 0;
                hal_uart_send_cmd("AT+CIPSTART=\"TCP\",\"broker.local\",1883\r\n");
                fsm_set_state(fsm, FSM_STATE_TCP_CONNECT, 20000);
            } else if (event == EV_TIMEOUT) {
                fsm_enter_backoff(fsm, FSM_STATE_IP_ATTACH);
            }
            break;

        case FSM_STATE_TCP_CONNECT:
            if (event == EV_TCP_CONNECTED) {
                fsm->retry_count = 0;
                fsm_set_state(fsm, FSM_STATE_READY_TO_SEND, 0);
            } else if (event == EV_TIMEOUT || event == EV_AT_ERROR) {
                // Сесійний збій сокета: повторна спроба підключення
                if (++fsm->retry_count >= fsm->max_retries) {
                    fsm_enter_backoff(fsm, FSM_STATE_IP_ATTACH);
                } else {
                    fsm_enter_backoff(fsm, FSM_STATE_TCP_CONNECT);
                }
            }
            break;

        case FSM_STATE_READY_TO_SEND:
            if (event == EV_SOCKET_CLOSED) {
                fsm_set_state(fsm, FSM_STATE_TCP_CONNECT, 100);
            }
            break;

        case FSM_STATE_BACKOFF_WAIT:
            if (event == EV_TIMEOUT) {
                // Час паузи минув, перехід до цільового стану
                fsm_set_state(fsm, fsm->rollback_target, 100);
            }
            break;

        case FSM_STATE_ERROR_RECOVERY:
            // Фатальний рівень: повне відключення живлення
            hal_modem_power_set(false);
            fsm->power_fet_status = false;
            fsm->retry_count = 0;
            fsm_set_state(fsm, FSM_STATE_NO_POWER, 5000);
            break;
    }
}
