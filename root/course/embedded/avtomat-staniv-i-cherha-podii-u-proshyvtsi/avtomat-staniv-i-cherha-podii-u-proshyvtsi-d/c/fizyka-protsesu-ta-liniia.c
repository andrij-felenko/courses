#include <stdint.h>
#include <stdbool.h>

/* Сигнали системи */
typedef enum {
    EV_CP_VOLTAGE_12V, // Автомобіль відключено
    EV_CP_VOLTAGE_9V,  // Автомобіль підключено
    EV_CP_VOLTAGE_6V,  // Запит заряджання
    EV_RFID_AUTH_OK,   // Авторизація успішна
    EV_OVERCURRENT,    // Перевищення струму (аварія)
    EV_RESET_BTN       // Ручне скидання
} EvseSignal;

typedef enum {
    ST_STANDBY,
    ST_CONNECTED,
    ST_CHARGING,
    ST_FAULT
} EvseStateId;

typedef struct EvseEvse Evse;
typedef void (*EvseStateHandler)(Evse *me, EvseSignal sig);

struct EvseEvse {
    EvseStateHandler state;
    bool is_authorized;
    uint16_t current_limit_a;
};

/* Апаратні функції абстракції (HAL) */
static void HAL_SetPilotPWM(uint8_t duty_percent) { (void)duty_percent; }
static void HAL_SetRelay(bool closed) { (void)closed; }
static void HAL_SetRedLed(bool on) { (void)on; }

/* Прототипи станів */
static void state_standby(Evse *me, EvseSignal sig);
static void state_connected(Evse *me, EvseSignal sig);
static void state_charging(Evse *me, EvseSignal sig);
static void state_fault(Evse *me, EvseSignal sig);

static void evse_transition(Evse *me, EvseStateHandler next) {
    me->state = next;
    // Одразу виконуємо ініціалізацію для нового стану
}

static void state_standby(Evse *me, EvseSignal sig) {
    switch (sig) {
        case EV_CP_VOLTAGE_9V:
            // Кабель підключено -> переходимо в очікування авторизації
            HAL_SetPilotPWM(50); // 32A доступно
            evse_transition(me, state_connected);
            break;

        default:
            break;
    }
}

static void state_connected(Evse *me, EvseSignal sig) {
    switch (sig) {
        case EV_RFID_AUTH_OK:
            me->is_authorized = true;
            break;

        case EV_CP_VOLTAGE_6V:
            if (me->is_authorized) {
                // Автомобіль готовий і авторизований -> заряджаємо
                HAL_SetRelay(true);
                evse_transition(me, state_charging);
            }
            break;

        case EV_CP_VOLTAGE_12V:
            // Штекер витягли
            me->is_authorized = false;
            HAL_SetPilotPWM(100); // 12V DC
            evse_transition(me, state_standby);
            break;

        case EV_OVERCURRENT:
            HAL_SetRedLed(true);
            evse_transition(me, state_fault);
            break;

        default:
            break;
    }
}

static void state_charging(Evse *me, EvseSignal sig) {
    switch (sig) {
        case EV_CP_VOLTAGE_9V:
            // Автомобіль призупинив заряджання (акумулятор повний)
            HAL_SetRelay(false);
            evse_transition(me, state_connected);
            break;

        case EV_CP_VOLTAGE_12V:
            // Аварійне висмикування під навантаженням
            HAL_SetRelay(false);
            me->is_authorized = false;
            HAL_SetPilotPWM(100);
            evse_transition(me, state_standby);
            break;

        case EV_OVERCURRENT:
            // Аварія струму: миттєве розмикання
            HAL_SetRelay(false);
            HAL_SetPilotPWM(0);
            HAL_SetRedLed(true);
            evse_transition(me, state_fault);
            break;

        default:
            break;
    }
}

static void state_fault(Evse *me, EvseSignal sig) {
    switch (sig) {
        case EV_RESET_BTN:
            HAL_SetRedLed(false);
            HAL_SetPilotPWM(100);
            me->is_authorized = false;
            evse_transition(me, state_standby);
            break;

        default:
            break;
    }
}

void evse_init(Evse *me) {
    me->is_authorized = false;
    me->current_limit_a = 32;
    HAL_SetRelay(false);
    HAL_SetPilotPWM(100);
    HAL_SetRedLed(false);
    me->state = state_standby;
}
