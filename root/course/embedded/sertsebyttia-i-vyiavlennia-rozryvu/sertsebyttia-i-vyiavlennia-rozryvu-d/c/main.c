#include <stdint.h>
#include <stdbool.h>

#define HB_DEFAULT_PERIOD_MS    200
#define HB_MAX_MISSED_COUNT     3
#define HB_MIN_RECOVERY_PACKETS 5
#define RTO_MIN_MS              100
#define RTO_MAX_MS              2000

typedef enum {
    LINK_DISCONNECTED = 0,
    LINK_CONNECTING,
    LINK_CONNECTED_OK,
    LINK_SUSPECT,
    LINK_FAILSAFE
} link_state_t;

typedef struct {
    uint32_t last_rx_time_ms;
    uint32_t last_tx_time_ms;
    uint32_t period_ms;
    uint32_t missed_count;
    uint32_t recovery_counter;
    
    // Метрики алгоритму Якобсона
    int32_t srtt_scaled;    // SRTT * 8
    int32_t rttvar_scaled;  // RTTVAR * 4
    uint32_t rto_ms;
    
    link_state_t state;
    void (*on_failsafe_enter)(void);
    void (*on_failsafe_exit)(void);
} heartbeat_monitor_t;

// Ініціалізація монітора
void heartbeat_init(heartbeat_monitor_t *mon,
                    void (*failsafe_enter_cb)(void),
                    void (*failsafe_exit_cb)(void)) {
    mon->last_rx_time_ms = 0;
    mon->last_tx_time_ms = 0;
    mon->period_ms = HB_DEFAULT_PERIOD_MS;
    mon->missed_count = 0;
    mon->recovery_counter = 0;
    
    // Початкові налаштування RTT: припускаємо стартовий RTT = 50 мс
    mon->srtt_scaled = 50 * 8;
    mon->rttvar_scaled = (50 / 2) * 4;
    mon->rto_ms = 150;
    
    mon->state = LINK_DISCONNECTED;
    mon->on_failsafe_enter = failsafe_enter_cb;
    mon->on_failsafe_exit = failsafe_exit_cb;
}

// Оновлення замірів RTT за алгоритмом Якобсона
static void update_rtt(heartbeat_monitor_t *mon, uint32_t rtt_sample_ms) {
    int32_t err = (int32_t)rtt_sample_ms - (mon->srtt_scaled >> 3);
    mon->srtt_scaled += err; // alpha = 1/8
    
    if (err < 0) {
        err = -err;
    }
    int32_t err_var = err - (mon->rttvar_scaled >> 2);
    mon->rttvar_scaled += err_var; // beta = 1/4
    
    // RTO = SRTT + 4 * RTTVAR
    uint32_t rto = (mon->srtt_scaled >> 3) + mon->rttvar_scaled;
    if (rto < RTO_MIN_MS) rto = RTO_MIN_MS;
    if (rto > RTO_MAX_MS) rto = RTO_MAX_MS;
    mon->rto_ms = rto;
}

// Виклик при надходженні валідного кадру від партнера
void heartbeat_on_rx(heartbeat_monitor_t *mon, uint32_t now_ms, uint32_t rtt_sample_ms, bool is_retransmit) {
    mon->last_rx_time_ms = now_ms;
    mon->missed_count = 0;

    // Оновлюємо RTT тільки якщо це не повторний кадр (правило Карна)
    if (!is_retransmit && rtt_sample_ms > 0) {
        update_rtt(mon, rtt_sample_ms);
    }

    switch (mon->state) {
        case LINK_DISCONNECTED:
        case LINK_CONNECTING:
            mon->state = LINK_CONNECTED_OK;
            mon->recovery_counter = 0;
            break;

        case LINK_SUSPECT:
            mon->state = LINK_CONNECTED_OK;
            break;

        case LINK_FAILSAFE:
            // Гістерезис відновлення: вимагаємо серію стабільних пакетів
            mon->recovery_counter++;
            if (mon->recovery_counter >= HB_MIN_RECOVERY_PACKETS) {
                mon->state = LINK_CONNECTED_OK;
                mon->recovery_counter = 0;
                if (mon->on_failsafe_exit) {
                    mon->on_failsafe_exit();
                }
            }
            break;

        case LINK_CONNECTED_OK:
            break;
    }
}

// Періодичний крок моніторингу (викликається в головному циклі або системному таймері)
void heartbeat_tick(heartbeat_monitor_t *mon, uint32_t now_ms) {
    if (mon->state == LINK_DISCONNECTED) {
        return;
    }

    uint32_t elapsed_since_rx = now_ms - mon->last_rx_time_ms;

    // Перевірка таймауту очікування пульсу
    if (elapsed_since_rx >= mon->rto_ms) {
        mon->missed_count++;
        mon->last_rx_time_ms = now_ms; // Зсуваємо вікно для підрахунку наступного пропуску

        if (mon->state == LINK_CONNECTED_OK) {
            mon->state = LINK_SUSPECT;
        }

        // Досягнуто критичної кількості пропусків -> перехід у FAILSAFE
        if (mon->missed_count >= HB_MAX_MISSED_COUNT && mon->state != LINK_FAILSAFE) {
            mon->state = LINK_FAILSAFE;
            mon->recovery_counter = 0;
            if (mon->on_failsafe_enter) {
                mon->on_failsafe_enter();
            }
        }
    }
}
