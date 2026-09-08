#include "relay.h"
#include <stdio.h>

/* Апаратний рівень комутації: у реальному мікроконтролері (AVR/STM32)
 * тут відбувається запис у вихідний регістр GPIO через бітову маску */
static void hardware_set_relay_pin(bool high) {
    /* Наприклад для AVR: if (high) PORTB |= (1 << PB0); else PORTB &= ~(1 << PB0);
     * Для демонстрації емулюємо вивід у консоль або лог */
    if (high) {
        printf("[АПАРАТНИЙ РІВЕНЬ] Реле: АКТИВОВАНО (котушка під напругою 5 В)\n");
    } else {
        printf("[АПАРАТНИЙ РІВЕНЬ] Реле: ВИМКНЕНО (контакти розімкнені)\n");
    }
}

void relay_init(relay_controller_t *ctrl, uint32_t deadtime_ms, uint32_t debounce_ms) {
    if (!ctrl) return;
    
    ctrl->state = RELAY_STATE_OFF;
    ctrl->pending_on = false;
    ctrl->last_switch_time_ms = 0;
    ctrl->deadtime_duration_ms = deadtime_ms;
    
    ctrl->last_raw_button = false;
    ctrl->debounced_button = false;
    ctrl->last_debounce_time_ms = 0;
    ctrl->debounce_delay_ms = debounce_ms;

    /* Початковий безпечний стан виходу при старті живлення від HLK-PM01 */
    hardware_set_relay_pin(false);
}

void relay_set_target(relay_controller_t *ctrl, bool target_on, uint32_t now_ms) {
    if (!ctrl) return;

    if (!target_on) {
        /* Аварійне або планове вимкнення виконується миттєво */
        ctrl->pending_on = false;
        if (ctrl->state == RELAY_STATE_ON) {
            hardware_set_relay_pin(false);
            ctrl->state = RELAY_STATE_DEADTIME;
            ctrl->last_switch_time_ms = now_ms;
            printf("[РЕХИМ] Перехід у DEADTIME на %u мс для захисту контактів\n", 
                   (unsigned int)ctrl->deadtime_duration_ms);
        }
        return;
    }

    /* Запит на увімкнення */
    if (ctrl->state == RELAY_STATE_OFF) {
        hardware_set_relay_pin(true);
        ctrl->state = RELAY_STATE_ON;
        ctrl->last_switch_time_ms = now_ms;
        ctrl->pending_on = false;
        printf("[РЕХИМ] Навантаження успішно увімкнено\n");
    } else if (ctrl->state == RELAY_STATE_DEADTIME) {
        /* Якщо реле щойно вимкнули, фіксуємо відкладений запит */
        ctrl->pending_on = true;
        printf("[ПОПЕРЕДЖЕННЯ] Захисна пауза активна. Увімкнення відкладено\n");
    }
}

void relay_toggle(relay_controller_t *ctrl, uint32_t now_ms) {
    if (!ctrl) return;
    if (ctrl->state == RELAY_STATE_ON) {
        relay_set_target(ctrl, false, now_ms);
    } else {
        relay_set_target(ctrl, true, now_ms);
    }
}

void relay_update_button(relay_controller_t *ctrl, bool raw_input, uint32_t now_ms) {
    if (!ctrl) return;

    /* Виявлення зміни сирого стану кнопки */
    if (raw_input != ctrl->last_raw_button) {
        ctrl->last_debounce_time_ms = now_ms;
        ctrl->last_raw_button = raw_input;
    }

    /* Якщо стан стабільний довше часу антибрязкання */
    if ((now_ms - ctrl->last_debounce_time_ms) >= ctrl->debounce_delay_ms) {
        if (raw_input != ctrl->debounced_button) {
            ctrl->debounced_button = raw_input;
            /* Фіксація натискання (передній фронт) */
            if (ctrl->debounced_button) {
                printf("[ВХІД] Зафіксовано натискання кнопки вимикача\n");
                relay_toggle(ctrl, now_ms);
            }
        }
    }
}

void relay_process(relay_controller_t *ctrl, uint32_t now_ms) {
    if (!ctrl) return;

    /* Обробка стану мертвого часу (dead-time) */
    if (ctrl->state == RELAY_STATE_DEADTIME) {
        if ((now_ms - ctrl->last_switch_time_ms) >= ctrl->deadtime_duration_ms) {
            printf("[РЕХИМ] Захисна пауза (dead-time) завершилась\n");
            ctrl->state = RELAY_STATE_OFF;

            /* Якщо під час паузи було запрошено увімкнення — активуємо */
            if (ctrl->pending_on) {
                ctrl->pending_on = false;
                hardware_set_relay_pin(true);
                ctrl->state = RELAY_STATE_ON;
                ctrl->last_switch_time_ms = now_ms;
                printf("[РЕХИМ] Відкладене увімкнення виконано\n");
            }
        }
    }
}

bool relay_is_active(const relay_controller_t *ctrl) {
    return (ctrl && ctrl->state == RELAY_STATE_ON);
}
