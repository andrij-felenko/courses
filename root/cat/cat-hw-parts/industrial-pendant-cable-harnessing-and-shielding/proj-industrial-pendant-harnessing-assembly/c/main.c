/**
 * @file main.c
 * @brief Головний цикл програми з ініціалізацією, опитуванням та симуляцією RS-485.
 */

#include <stdio.h>
#include <stdbool.h>
#include "pendant_controller.h"

int main(void) {
    printf("=== Ініціалізація контролера промислового підвісного пульта ===\n");
    
    PendantController pendant;
    pendant_init(&pendant);
    
    // Симуляційний цикл опитування (10 ітерацій для демонстрації)
    for (int step = 1; step <= 10; step++) {
        printf("\n--- Цикл опитування #%d ---\n", step);
        
        uint8_t simulated_raw_buttons = 0;
        bool simulated_e_stop_line = true; // За замовчуванням ланцюг NC замкнений
        
        if (step == 2 || step == 3) {
            simulated_raw_buttons = (1 << BTN_UP); // Натиснута кнопка "Вгору"
        } else if (step == 5) {
            simulated_raw_buttons = (1 << BTN_DOWN) | (1 << BTN_START); // Натиснуті "Вниз" і "Старт"
        } else if (step == 7) {
            // Симуляція обриву кабелю або натискання аварійної кнопки E-Stop
            simulated_e_stop_line = false;
            simulated_raw_buttons = (1 << BTN_LEFT); // Навіть якщо натиснута кнопка, E-Stop блокує
        } else if (step >= 8) {
            // Відновлення лінії E-Stop
            simulated_e_stop_line = true;
            simulated_raw_buttons = 0;
        }
        
        // Опитування входів контролером
        pendant_poll_inputs(&pendant, simulated_raw_buttons, simulated_e_stop_line);
        
        // Формування телеметричного фрейму
        PendantTelemetryFrame frame;
        pendant_build_frame(&pendant, &frame);
        
        // Вивід станів
        printf("E-Stop статус (NC): %s (Аварій: %u)\n", 
               pendant.e_stop.is_closed ? "НОРМА (Замкнено)" : "АВАРІЯ / ОБРИВ",
               pendant.e_stop.fault_count);
        
        printf("Стабільні стани кнопок (маска 0x%02X):\n", frame.button_mask);
        printf("  UP:    %s\n", pendant.buttons[BTN_UP].debounced_state ? "[ON]" : "[OFF]");
        printf("  DOWN:  %s\n", pendant.buttons[BTN_DOWN].debounced_state ? "[ON]" : "[OFF]");
        printf("  LEFT:  %s\n", pendant.buttons[BTN_LEFT].debounced_state ? "[ON]" : "[OFF]");
        printf("  RIGHT: %s\n", pendant.buttons[BTN_RIGHT].debounced_state ? "[ON]" : "[OFF]");
        printf("  START: %s\n", pendant.buttons[BTN_START].debounced_state ? "[ON]" : "[OFF]");
        printf("  STOP:  %s\n", pendant.buttons[BTN_STOP].debounced_state ? "[ON]" : "[OFF]");
        
        // Вивід сформованого пакету RS-485
        printf("RS-485 Фрейм [ID: %u]: Preamble=0x%04X, Mask=0x%02X, EStop=%u, CRC=0x%04X\n",
               frame.packet_id, frame.preamble, frame.button_mask, frame.e_stop_status, frame.crc16);
        
        // Перевірка цілісності CRC-16
        size_t payload_size = sizeof(PendantTelemetryFrame) - sizeof(uint16_t);
        uint16_t rx_crc = pendant_calculate_crc16((const uint8_t *)&frame, payload_size);
        bool crc_valid = (rx_crc == frame.crc16);
        printf("Перевірка CRC на прийманні: %s (rx_crc = 0x%04X)\n", crc_valid ? "УСПІХ" : "ПОМИЛКА", rx_crc);
    }
    
    printf("\n=== Роботу симулятора завершено успішно ===\n");
    return 0;
}
