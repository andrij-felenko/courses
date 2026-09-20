#include "safety_controller.h"

void safety_controller_init(safety_controller_t *ctrl) {
    if (!ctrl) return;

    ctrl->state = SAFETY_STATE_OK;
    ctrl->ossd_output_enable = false;

    // Ініціалізація підсистеми OSSD
    ctrl->ossd.channel_a_raw = false;
    ctrl->ossd.channel_b_raw = false;
    ctrl->ossd.channel_a_filtered = false;
    ctrl->ossd.channel_b_filtered = false;
    ctrl->ossd.test_pulse_counter_a = 0;
    ctrl->ossd.test_pulse_counter_b = 0;
    ctrl->ossd.discrepancy_timer_ms = 0;
    ctrl->ossd.fault_cross_short = false;

    // Ініціалізація підсистеми EDM
    ctrl->edm.edm_feedback_nc = true; // При знеструмлених контакторах НЗ контакти замкнені
    ctrl->edm.expected_state = true;
    ctrl->edm.edm_timer_ms = 0;
    ctrl->edm.max_allowed_delay_ms = SAFETY_EDM_TIMEOUT_MS;
    ctrl->edm.edm_fault = false;

    // Ініціалізація підсистеми Muting
    ctrl->muting.sensor_m1 = false;
    ctrl->muting.sensor_m2 = false;
    ctrl->muting.muting_active = false;
    ctrl->muting.m1_activation_time_ms = 0;
    ctrl->muting.m2_activation_time_ms = 0;
    ctrl->muting.max_sequence_gap_ms = SAFETY_MUTING_MAX_GAP_MS;
    ctrl->muting.muting_fault = false;
}

void safety_process_ossd(safety_controller_t *ctrl, bool raw_a, bool raw_b, uint32_t delta_ms) {
    if (!ctrl) return;

    ctrl->ossd.channel_a_raw = raw_a;
    ctrl->ossd.channel_b_raw = raw_b;

    // Фільтрація тестових імпульсів 0В (Test Pulses) для каналу A
    if (!raw_a) {
        if (ctrl->ossd.test_pulse_counter_a < SAFETY_TEST_PULSE_MAX_TICKS) {
            ctrl->ossd.test_pulse_counter_a++;
        } else {
            ctrl->ossd.channel_a_filtered = false;
        }
    } else {
        ctrl->ossd.test_pulse_counter_a = 0;
        ctrl->ossd.channel_a_filtered = true;
    }

    // Фільтрація тестових імпульсів 0В для каналу B
    if (!raw_b) {
        if (ctrl->ossd.test_pulse_counter_b < SAFETY_TEST_PULSE_MAX_TICKS) {
            ctrl->ossd.test_pulse_counter_b++;
        } else {
            ctrl->ossd.channel_b_filtered = false;
        }
    } else {
        ctrl->ossd.test_pulse_counter_b = 0;
        ctrl->ossd.channel_b_filtered = true;
    }

    // Двоканальний контроль неузгодженості сигналів A та B
    if (ctrl->ossd.channel_a_filtered != ctrl->ossd.channel_b_filtered) {
        ctrl->ossd.discrepancy_timer_ms += delta_ms;
        if (ctrl->ossd.discrepancy_timer_ms > SAFETY_DISCREPANCY_TIMEOUT_MS) {
            ctrl->ossd.fault_cross_short = true; // Фіксація короткого замикання або відмови каналу
        }
    } else {
        ctrl->ossd.discrepancy_timer_ms = 0;
    }
}

void safety_process_edm(safety_controller_t *ctrl, bool feedback_nc, uint32_t delta_ms) {
    if (!ctrl) return;

    ctrl->edm.edm_feedback_nc = feedback_nc;

    // Очікуваний стан НЗ контактів зворотного зв'язку протилежний до стану OSSD виходу
    // Якщо виходи OSSD увімкнені (робота), контактори замкнені -> НЗ контакти розімкнені (false)
    ctrl->edm.expected_state = !ctrl->ossd_output_enable;

    if (ctrl->edm.edm_feedback_nc != ctrl->edm.expected_state) {
        ctrl->edm.edm_timer_ms += delta_ms;
        if (ctrl->edm.edm_timer_ms > ctrl->edm.max_allowed_delay_ms) {
            ctrl->edm.edm_fault = true; // Залипання контактора або урвище кола зворотного зв'язку
        }
    } else {
        ctrl->edm.edm_timer_ms = 0;
    }
}

void safety_process_muting(safety_controller_t *ctrl, bool sensor_m1, bool sensor_m2, uint32_t system_time_ms) {
    if (!ctrl) return;

    // Фіксація фронтів спрацювання датчиків M1 та M2
    if (sensor_m1 && !ctrl->muting.sensor_m1) {
        ctrl->muting.m1_activation_time_ms = system_time_ms;
    }
    if (sensor_m2 && !ctrl->muting.sensor_m2) {
        ctrl->muting.m2_activation_time_ms = system_time_ms;
    }

    ctrl->muting.sensor_m1 = sensor_m1;
    ctrl->muting.sensor_m2 = sensor_m2;

    // Логіка увімкнення Muting (обидва датчики M1 та M2 мають бути перекриті)
    if (sensor_m1 && sensor_m2) {
        uint32_t time_diff = (ctrl->muting.m1_activation_time_ms > ctrl->muting.m2_activation_time_ms) ?
                             (ctrl->muting.m1_activation_time_ms - ctrl->muting.m2_activation_time_ms) :
                             (ctrl->muting.m2_activation_time_ms - ctrl->muting.m1_activation_time_ms);

        // Перевірка допустимого часового вікна послідовності спрацювання
        if (time_diff <= ctrl->muting.max_sequence_gap_ms) {
            ctrl->muting.muting_active = true;
            ctrl->muting.muting_fault = false;
        } else {
            ctrl->muting.muting_active = false;
            ctrl->muting.muting_fault = true; // Неприпустимо повільне або стороннє перекриття
        }
    } else if (!sensor_m1 && !sensor_m2) {
        ctrl->muting.muting_active = false;
    }
}

void safety_controller_update(safety_controller_t *ctrl, uint32_t delta_ms, uint32_t system_time_ms) {
    if (!ctrl) return;

    // Перевірка наявних критичних апаратних відмов
    if (ctrl->ossd.fault_cross_short) {
        ctrl->state = SAFETY_STATE_FAULT_CROSS_SHORT;
        ctrl->ossd_output_enable = false;
        return;
    }

    if (ctrl->edm.edm_fault) {
        ctrl->state = SAFETY_STATE_FAULT_EDM_TIMEOUT;
        ctrl->ossd_output_enable = false;
        return;
    }

    if (ctrl->muting.muting_fault) {
        ctrl->state = SAFETY_STATE_FAULT_MUTING_SEQ;
        ctrl->ossd_output_enable = false;
        return;
    }

    // Визначення результуючого стану безпеки
    bool ossd_valid = ctrl->ossd.channel_a_filtered && ctrl->ossd.channel_b_filtered;

    if (ossd_valid) {
        ctrl->state = SAFETY_STATE_OK;
        ctrl->ossd_output_enable = true;
    } else if (ctrl->muting.muting_active) {
        // У режимі Muting маскуємо переривання світлової завіси
        ctrl->state = SAFETY_STATE_MUTING_ACTIVE;
        ctrl->ossd_output_enable = true;
    } else {
        // Переривання променя без активного Muting викликає захисне вимкнення
        ctrl->state = SAFETY_STATE_TRIPPED;
        ctrl->ossd_output_enable = false;
    }
}
