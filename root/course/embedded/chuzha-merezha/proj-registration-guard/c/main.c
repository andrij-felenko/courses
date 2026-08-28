#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    GUARD_STATE_POWER_OFF,
    GUARD_STATE_BOOT,
    GUARD_STATE_CHECK_REG,
    GUARD_STATE_ONLINE_TX,
    GUARD_STATE_RECOVERY,
    GUARD_STATE_BACKOFF_SLEEP
} guard_state_t;

typedef struct {
    guard_state_t state;
    uint32_t state_enter_time_ms;
    uint32_t backoff_interval_sec;
    uint8_t  failed_attempts;
    bool     radio_registered;
} cellular_guard_t;

#define MAX_REG_TIMEOUT_MS     45000UL
#define BASE_BACKOFF_SEC       60UL
#define MAX_BACKOFF_SEC        14400UL // 4 години максимум
#define MAX_CONSECUTIVE_FAILS  3

void cellular_guard_init(cellular_guard_t *guard) {
    guard->state = GUARD_STATE_POWER_OFF;
    guard->state_enter_time_ms = 0;
    guard->backoff_interval_sec = BASE_BACKOFF_SEC;
    guard->failed_attempts = 0;
    guard->radio_registered = false;
}

// Заглушки апаратних дій платформи
extern void modem_hardware_power(bool enable);
extern bool modem_send_at_cmd(const char *cmd, const char *expected_resp, uint32_t timeout_ms);
extern int  modem_query_registration_status(void); // повертає 1 (home), 5 (roam), 2 (search), 3 (denied)

void cellular_guard_step(cellular_guard_t *guard, uint32_t now_ms) {
    uint32_t elapsed_in_state = now_ms - guard->state_enter_time_ms;

    switch (guard->state) {
    case GUARD_STATE_POWER_OFF:
        modem_hardware_power(true);
        guard->state = GUARD_STATE_BOOT;
        guard->state_enter_time_ms = now_ms;
        break;

    case GUARD_STATE_BOOT:
        if (modem_send_at_cmd("AT\r", "OK", 1000)) {
            // Налаштовуємо розширені відповіді реєстрації
            modem_send_at_cmd("AT+CEREG=2\r", "OK", 1000);
            guard->state = GUARD_STATE_CHECK_REG;
            guard->state_enter_time_ms = now_ms;
        } else if (elapsed_in_state > 10000) {
            // Модем не відповів на UART за 10 секунд — аварійне відновлення
            guard->state = GUARD_STATE_RECOVERY;
            guard->state_enter_time_ms = now_ms;
        }
        break;

    case GUARD_STATE_CHECK_REG: {
        int reg_status = modem_query_registration_status();
        if (reg_status == 1 || reg_status == 5) {
            // Успішно зареєстровано в мережі
            guard->radio_registered = true;
            guard->failed_attempts = 0;
            guard->backoff_interval_sec = BASE_BACKOFF_SEC; // скидаємо backoff
            guard->state = GUARD_STATE_ONLINE_TX;
            guard->state_enter_time_ms = now_ms;
        } else if (reg_status == 3 || elapsed_in_state > MAX_REG_TIMEOUT_MS) {
            // Мережа відхилила пристрій (Denied) або вичерпано 45 с пошуку
            guard->failed_attempts++;
            guard->state = GUARD_STATE_RECOVERY;
            guard->state_enter_time_ms = now_ms;
        }
        break;
    }

    case GUARD_STATE_RECOVERY:
        // Примусовий перезапуск радіотракту: вимикаємо RF, вмикаємо RF, скидаємо PLMN
        modem_send_at_cmd("AT+CFUN=0\r", "OK", 3000);
        modem_send_at_cmd("AT+CFUN=1\r", "OK", 3000);
        modem_send_at_cmd("AT+COPS=0\r", "OK", 5000); // Автоматичний вибір оператора

        // Переходимо в захисний сон з експоненційним інтервалом
        modem_hardware_power(false);
        guard->state = GUARD_STATE_BACKOFF_SLEEP;
        guard->state_enter_time_ms = now_ms;
        break;

    case GUARD_STATE_BACKOFF_SLEEP:
        if (elapsed_in_state >= guard->backoff_interval_sec * 1000UL) {
            // Експоненційне збільшення інтервалу (1хв -> 2хв -> 4хв -> ... до 4 год)
            guard->backoff_interval_sec *= 2;
            if (guard->backoff_interval_sec > MAX_BACKOFF_SEC) {
                guard->backoff_interval_sec = MAX_BACKOFF_SEC;
            }
            guard->state = GUARD_STATE_POWER_OFF;
            guard->state_enter_time_ms = now_ms;
        }
        break;

    case GUARD_STATE_ONLINE_TX:
        // Тут виконується прикладне відправлення телеметрії.
        // При фатальній помилці сокета повертаємося в RECOVERY.
        break;
    }
}
