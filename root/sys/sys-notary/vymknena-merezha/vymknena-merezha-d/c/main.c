#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Константи таймінгів та параметрів пошуку мережі */
#define MODEM_MAX_SEARCH_ATTEMPTS  5U
#define MODEM_BASE_BACKOFF_SEC     60U      /* 1 хвилина */
#define MODEM_MAX_BACKOFF_SEC      86400U   /* 24 години */
#define MODEM_SEARCH_TIMEOUT_MS    45000U   /* 45 секунд на спробу */
#define MODEM_PWRKEY_PULSE_MS      1000U    /* Імпульс PWRKEY 1 с */

/* Стани кінцевого автомата модема */
typedef enum {
    MODEM_STATE_POWERED_DOWN = 0,
    MODEM_STATE_POWERING_ON,
    MODEM_STATE_AT_CHECK,
    MODEM_STATE_CONFIG_RAT,
    MODEM_STATE_WAIT_REGISTRATION,
    MODEM_STATE_CONNECTED,
    MODEM_STATE_POWERING_OFF,
    MODEM_STATE_SLEEP_BACKOFF
} modem_state_t;

/* Технології радіодоступу (RAT) */
typedef enum {
    MODEM_RAT_LTE_M = 0,
    MODEM_RAT_NB_IOT,
    MODEM_RAT_GSM_2G
} modem_rat_t;

/* Структура апаратного інтерфейсу (HAL) */
typedef struct {
    void (*set_power_switch)(bool enable);
    void (*set_pwrkey)(bool level);
    void (*set_dtr)(bool level);
    void (*set_uart_pins)(bool active);
    bool (*send_at_command)(const char *cmd, const char *expected_resp, uint32_t timeout_ms);
    uint32_t (*get_tick_ms)(void);
    uint32_t (*get_random_jitter)(uint32_t max_jitter_sec);
} modem_hal_t;

/* Контекст керування модемом */
typedef struct {
    modem_state_t state;
    modem_rat_t current_rat;
    uint32_t attempt_count;
    uint32_t state_enter_time_ms;
    uint32_t sleep_duration_sec;
    uint32_t last_connected_timestamp;
    bool registration_successful;
    const modem_hal_t *hal;
} modem_controller_t;

/* Ініціалізація контролера */
void modem_controller_init(modem_controller_t *ctrl, const modem_hal_t *hal) {
    if (!ctrl || !hal) return;
    memset(ctrl, 0, sizeof(*ctrl));
    ctrl->hal = hal;
    ctrl->state = MODEM_STATE_POWERED_DOWN;
    ctrl->current_rat = MODEM_RAT_LTE_M;
    ctrl->hal->set_power_switch(false);
    ctrl->hal->set_uart_pins(false);
}

/* Розрахунок інтервалу експоненційного відкату з випадковим тремтінням (Jitter) */
static uint32_t modem_calculate_backoff(uint32_t attempt, const modem_hal_t *hal) {
    uint32_t shift = (attempt > 10U) ? 10U : attempt;
    uint32_t backoff = MODEM_BASE_BACKOFF_SEC * (1UL << shift);
    if (backoff > MODEM_MAX_BACKOFF_SEC) {
        backoff = MODEM_MAX_BACKOFF_SEC;
    }
    /* Додаємо псевдовипадковий jitter до 20% від базового значення */
    uint32_t jitter_max = backoff / 5U;
    if (jitter_max > 0 && hal && hal->get_random_jitter) {
        backoff += hal->get_random_jitter(jitter_max);
    }
    return backoff;
}

/* Основний крок кінцевого автомата (викликається періодично в циклі super-loop) */
void modem_controller_step(modem_controller_t *ctrl) {
    if (!ctrl || !ctrl->hal) return;

    uint32_t now = ctrl->hal->get_tick_ms();
    uint32_t elapsed = now - ctrl->state_enter_time_ms;

    switch (ctrl->state) {
        case MODEM_STATE_POWERED_DOWN:
            /* Початок сесії зв'язку: подаємо живлення на силовий ключ */
            ctrl->hal->set_power_switch(true);
            ctrl->hal->set_uart_pins(true);
            ctrl->state = MODEM_STATE_POWERING_ON;
            ctrl->state_enter_time_ms = now;
            break;

        case MODEM_STATE_POWERING_ON:
            /* Імпульс на лінії PWRKEY для активації базового процесора */
            if (elapsed < MODEM_PWRKEY_PULSE_MS) {
                ctrl->hal->set_pwrkey(true);
            } else if (elapsed < (MODEM_PWRKEY_PULSE_MS + 2000U)) {
                ctrl->hal->set_pwrkey(false);
            } else {
                ctrl->state = MODEM_STATE_AT_CHECK;
                ctrl->state_enter_time_ms = now;
            }
            break;

        case MODEM_STATE_AT_CHECK:
            /* Перевірка готовності UART-інтерфейсу модема */
            if (ctrl->hal->send_at_command("AT\r\n", "OK", 1000U)) {
                /* Вимикаємо відлуння для економії байтів */
                ctrl->hal->send_at_command("ATE0\r\n", "OK", 500U);
                ctrl->state = MODEM_STATE_CONFIG_RAT;
                ctrl->state_enter_time_ms = now;
            } else if (elapsed > 10000U) {
                /* Якщо модем не відповів за 10 с — помилка апаратного запуску */
                ctrl->state = MODEM_STATE_POWERING_OFF;
                ctrl->state_enter_time_ms = now;
            }
            break;

        case MODEM_STATE_CONFIG_RAT:
            /* Фіксація технології та обмеження списку смуг (Band Locking) */
            if (ctrl->current_rat == MODEM_RAT_LTE_M) {
                /* Режим лише LTE-M (eMTC) з європейськими смугами B8, B20 */
                ctrl->hal->send_at_command("AT+QCFG=\"nwscanmode\",3,1\r\n", "OK", 1000U);
                ctrl->hal->send_at_command("AT+QCFG=\"iotopmode\",0,1\r\n", "OK", 1000U);
                ctrl->hal->send_at_command("AT+QCFG=\"band\",0,800080,0,1\r\n", "OK", 1000U);
            } else if (ctrl->current_rat == MODEM_RAT_NB_IOT) {
                /* Режим лише NB-IoT (Cat-NB2) */
                ctrl->hal->send_at_command("AT+QCFG=\"nwscanmode\",3,1\r\n", "OK", 1000U);
                ctrl->hal->send_at_command("AT+QCFG=\"iotopmode\",1,1\r\n", "OK", 1000U);
            } else {
                /* Резервний 2G GSM (якщо підтримується апаратно) */
                ctrl->hal->send_at_command("AT+QCFG=\"nwscanmode\",1,1\r\n", "OK", 1000U);
            }

            /* Запит статусу реєстрації в мережі */
            ctrl->hal->send_at_command("AT+CEREG=2\r\n", "OK", 1000U);
            ctrl->hal->send_at_command("AT+COPS=0\r\n", "OK", 5000U);
            ctrl->state = MODEM_STATE_WAIT_REGISTRATION;
            ctrl->state_enter_time_ms = now;
            break;

        case MODEM_STATE_WAIT_REGISTRATION:
            /* Перевіряємо реєстрацію в мережі через CEREG */
            if (ctrl->hal->send_at_command("AT+CEREG?\r\n", "+CEREG: 2,1", 2000U) ||
                ctrl->hal->send_at_command("AT+CEREG?\r\n", "+CEREG: 2,5", 2000U)) {
                /* Успішна реєстрація (1 = Home, 5 = Roaming) */
                ctrl->registration_successful = true;
                ctrl->attempt_count = 0;
                ctrl->state = MODEM_STATE_CONNECTED;
                ctrl->state_enter_time_ms = now;
            } else if (elapsed > MODEM_SEARCH_TIMEOUT_MS) {
                /* Таймаут пошуку поточної технології радіодоступу */
                if (ctrl->current_rat == MODEM_RAT_LTE_M) {
                    /* Перемикаємося на NB-IoT */
                    ctrl->current_rat = MODEM_RAT_NB_IOT;
                    ctrl->state = MODEM_STATE_CONFIG_RAT;
                    ctrl->state_enter_time_ms = now;
                } else if (ctrl->current_rat == MODEM_RAT_NB_IOT) {
                    /* Перемикаємося на резервний GSM */
                    ctrl->current_rat = MODEM_RAT_GSM_2G;
                    ctrl->state = MODEM_STATE_CONFIG_RAT;
                    ctrl->state_enter_time_ms = now;
                } else {
                    /* Усі RAT перевірено, мережу не знайдено: запускаємо Backoff */
                    ctrl->current_rat = MODEM_RAT_LTE_M;
                    ctrl->attempt_count++;
                    ctrl->sleep_duration_sec = modem_calculate_backoff(ctrl->attempt_count, ctrl->hal);
                    ctrl->state = MODEM_STATE_POWERING_OFF;
                    ctrl->state_enter_time_ms = now;
                }
            }
            break;

        case MODEM_STATE_CONNECTED:
            /* Модем на зв'язку. Верхній рівень стека виконує передачу телеметрії */
            break;

        case MODEM_STATE_POWERING_OFF:
            /* Коректне відключення від мережі та знеструмлення */
            ctrl->hal->send_at_command("AT+QPOWD=1\r\n", "POWERED DOWN", 3000U);
            ctrl->hal->set_power_switch(false);
            ctrl->hal->set_uart_pins(false);
            ctrl->state = MODEM_STATE_SLEEP_BACKOFF;
            ctrl->state_enter_time_ms = now;
            break;

        case MODEM_STATE_SLEEP_BACKOFF:
            /* Очікування інтервалу експоненційного відкату в глибокому сні */
            if (elapsed >= (ctrl->sleep_duration_sec * 1000U)) {
                ctrl->state = MODEM_STATE_POWERED_DOWN;
                ctrl->state_enter_time_ms = now;
            }
            break;
    }
}
