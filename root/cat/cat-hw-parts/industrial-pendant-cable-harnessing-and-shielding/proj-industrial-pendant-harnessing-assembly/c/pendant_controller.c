/**
 * @file pendant_controller.c
 * @brief Реалізація кінцевого автомата опитування, антибрязкання, E-Stop та CRC-16.
 */

#include "pendant_controller.h"
#include <string.h>

/** Поріг інтегруючого фільтра антибрязкання (кількість однакових циклів) */
#define DEBOUNCE_THRESHOLD 5

void pendant_init(PendantController *ctrl) {
    if (!ctrl) return;
    
    memset(ctrl, 0, sizeof(PendantController));
    ctrl->e_stop.is_closed = false; // За замовчуванням при старті вважаємо аварію до першої валідації лінії NC
    ctrl->e_stop.fault_count = 0;
    ctrl->packet_counter = 0;
    
    for (int i = 0; i < PENDANT_BUTTON_COUNT; i++) {
        ctrl->buttons[i].raw_state = false;
        ctrl->buttons[i].debounced_state = false;
        ctrl->buttons[i].counter = 0;
    }
}

void pendant_poll_inputs(PendantController *ctrl, uint8_t raw_inputs, bool e_stop_pin_level) {
    if (!ctrl) return;

    // 1. Безперервний моніторинг лінії Emergency Stop (NC - Normally Closed)
    // Якщо лінія розімкнена (низький рівень або обрив), миттєво переводимо в аварійний стан.
    if (!e_stop_pin_level) {
        if (ctrl->e_stop.is_closed) {
            ctrl->e_stop.fault_count++;
        }
        ctrl->e_stop.is_closed = false;
    } else {
        ctrl->e_stop.is_closed = true;
    }

    // 2. Опитування дискретних кнопок із програмним антибрязканням (інтегруючий фільтр)
    for (int i = 0; i < PENDANT_BUTTON_COUNT; i++) {
        bool current_raw = (raw_inputs & (1 << i)) != 0;
        ctrl->buttons[i].raw_state = current_raw;

        if (current_raw != ctrl->buttons[i].debounced_state) {
            // Якщо стан відрізняється від стабільного, інкрементуємо або декрементуємо лічильник
            if (current_raw) {
                if (ctrl->buttons[i].counter < DEBOUNCE_THRESHOLD) {
                    ctrl->buttons[i].counter++;
                }
            } else {
                if (ctrl->buttons[i].counter > 0) {
                    ctrl->buttons[i].counter--;
                }
            }

            // Перевірка досягнення порогу стабілізації
            if (ctrl->buttons[i].counter >= DEBOUNCE_THRESHOLD) {
                ctrl->buttons[i].debounced_state = true;
            } else if (ctrl->buttons[i].counter == 0) {
                ctrl->buttons[i].debounced_state = false;
            }
        } else {
            // Якщо стан збігається, плавно скидаємо лічильник у відповідний крайній стан
            if (current_raw) {
                ctrl->buttons[i].counter = DEBOUNCE_THRESHOLD;
            } else {
                ctrl->buttons[i].counter = 0;
            }
        }
    }

    // Якщо спрацював E-Stop, примусово скидаємо всі команди кнопок руху для безпеки
    if (!ctrl->e_stop.is_closed) {
        for (int i = 0; i < PENDANT_BUTTON_COUNT; i++) {
            ctrl->buttons[i].debounced_state = false;
            ctrl->buttons[i].counter = 0;
        }
    }
}

uint16_t pendant_calculate_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF; // Стандартне початкове значення для Modbus CRC-16
    
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001; // Поліном Modbus (стан зворотного порядку 0x8005)
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

void pendant_build_frame(PendantController *ctrl, PendantTelemetryFrame *frame) {
    if (!ctrl || !frame) return;

    frame->preamble = PENDANT_FRAME_PREAMBLE;
    frame->packet_id = ctrl->packet_counter++;
    
    // Формування бітової маски кнопок
    uint8_t mask = 0;
    for (int i = 0; i < PENDANT_BUTTON_COUNT; i++) {
        if (ctrl->buttons[i].debounced_state) {
            mask |= (1 << i);
        }
    }
    frame->button_mask = mask;
    
    // Статус E-Stop (1 - все гаразд, 0 - аварія / обрив)
    frame->e_stop_status = ctrl->e_stop.is_closed ? 1 : 0;
    
    // Обчислення CRC-16 для полів кадру без самого поля crc16
    size_t payload_size = sizeof(PendantTelemetryFrame) - sizeof(uint16_t);
    frame->crc16 = pendant_calculate_crc16((const uint8_t *)frame, payload_size);
}
