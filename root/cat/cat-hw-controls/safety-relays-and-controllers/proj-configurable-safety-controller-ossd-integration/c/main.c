#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "safety_controller.h"

// Допоміжна функція виводу стану текстовою строкою
static const char* safety_state_to_string(safety_state_t state) {
    switch (state) {
        case SAFETY_STATE_OK:                 return "OK (Нормальна робота)";
        case SAFETY_STATE_MUTING_ACTIVE:      return "MUTING_ACTIVE (Маскування завіси)";
        case SAFETY_STATE_TRIPPED:            return "TRIPPED (Захисне вимкнення)";
        case SAFETY_STATE_FAULT_CROSS_SHORT:  return "FAULT: Крос-коротке замикання OSSD";
        case SAFETY_STATE_FAULT_EDM_TIMEOUT:  return "FAULT: Таймаут/залипання контактора EDM";
        case SAFETY_STATE_FAULT_MUTING_SEQ:   return "FAULT: Порушення часового вікна Muting";
        default:                              return "UNKNOWN_STATE";
    }
}

int main(void) {
    safety_controller_t ctrl;
    safety_controller_init(&ctrl);

    uint32_t system_time_ms = 0;
    uint32_t step_delta_ms = 10;

    printf("=== СИМУЛЯЦІЯ РЕЛЕ ТА КОНТРОЛЕРА БЕЗПЕКИ ===\n\n");

    // Сценарій 1: Нормальна робота (Світлова завіса відкрита, OSSD A=1, B=1)
    printf("[Крок 1] Нормальний режим роботи (OSSD A=1, B=1, EDM NC=false)...
");
    for (int i = 0; i < 5; i++) {
        system_time_ms += step_delta_ms;
        safety_process_ossd(&ctrl, true, true, step_delta_ms);
        safety_process_edm(&ctrl, false, step_delta_ms); // Виходи увімкнені -> НЗ контакторів розімкнені (false)
        safety_process_muting(&ctrl, false, false, system_time_ms);
        safety_controller_update(&ctrl, step_delta_ms, system_time_ms);
    }
    printf("Стан системи: %s | OSSD_OUT: %d\n\n",
           safety_state_to_string(ctrl.state), ctrl.ossd_output_enable);

    // Сценарій 2: Переривання світлової завіси (OSSD A=0, B=0) -> Спрацювання захисту
    printf("[Крок 2] Переривання світлового променя (OSSD A=0, B=0)...
");
    for (int i = 0; i < 5; i++) {
        system_time_ms += step_delta_ms;
        safety_process_ossd(&ctrl, false, false, step_delta_ms);
        safety_process_edm(&ctrl, true, step_delta_ms); // Спрацював захист -> контактори вимкнені -> NC замкнені (true)
        safety_process_muting(&ctrl, false, false, system_time_ms);
        safety_controller_update(&ctrl, step_delta_ms, system_time_ms);
    }
    printf("Стан системи: %s | OSSD_OUT: %d\n\n",
           safety_state_to_string(ctrl.state), ctrl.ossd_output_enable);

    // Сценарій 3: Штатний режим Muting (Послідовний заїзд вантажу: M1 -> M2)
    printf("[Крок 3] Активація режиму Muting (Спрацювання M1, потім M2 через 100 мс)...
");
    // Спрацювання M1
    system_time_ms += step_delta_ms;
    safety_process_ossd(&ctrl, true, true, step_delta_ms);
    safety_process_edm(&ctrl, false, step_delta_ms);
    safety_process_muting(&ctrl, true, false, system_time_ms);
    safety_controller_update(&ctrl, step_delta_ms, system_time_ms);

    // Через 100 мс спрацьовує M2
    system_time_ms += 100;
    safety_process_ossd(&ctrl, false, false, step_delta_ms); // Вантаж перекрив світлову завісу!
    safety_process_edm(&ctrl, false, step_delta_ms);
    safety_process_muting(&ctrl, true, true, system_time_ms);
    safety_controller_update(&ctrl, step_delta_ms, system_time_ms);

    printf("Стан системи під час проходження вантажу: %s | OSSD_OUT: %d\n\n",
           safety_state_to_string(ctrl.state), ctrl.ossd_output_enable);

    // Сценарій 4: Симуляція апаратної відмови EDM (Залипання силового контактора)
    printf("[Крок 4] Симуляція відмови EDM (OSSD_OUT=0, але контактор залип: NC=false)...
");
    safety_controller_init(&ctrl); // Скидання для чистоти тесту
    system_time_ms += 500;

    // Вимикаємо OSSD, але симулюємо, що НЗ-контакт контактора НЕ замкнувся (EDM NC = false)
    for (int i = 0; i < 25; i++) { // 25 * 10 мс = 250 мс (> 200 мс таймауту)
        system_time_ms += step_delta_ms;
        safety_process_ossd(&ctrl, false, false, step_delta_ms);
        safety_process_edm(&ctrl, false, step_delta_ms); // Аварія: очікуємо true, маємо false!
        safety_process_muting(&ctrl, false, false, system_time_ms);
        safety_controller_update(&ctrl, step_delta_ms, system_time_ms);
    }
    printf("Стан системи після таймауту EDM: %s | OSSD_OUT: %d\n\n",
           safety_state_to_string(ctrl.state), ctrl.ossd_output_enable);

    printf("=== ТЕСТУВАННЯ ЗАВЕРШЕНО УСПІШНО ===\n");
    return 0;
}
