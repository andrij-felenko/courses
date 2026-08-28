// ============================================================================
// test_limp_controller.cpp - C++20 Модульні тести
// ============================================================================
#include <iostream>
#include <cassert>
#include "LimpHomeController.hpp"

using namespace embedded::limp;
using namespace std::chrono_literals;

void test_ring_buffer_freeze_frame() {
    Config cfg{
        .temp_warn_c = 90.0f, .temp_crit_c = 105.0f, .temp_fatal_c = 115.0f,
        .temp_hysteresis_c = 8.0f, .cell_volt_warn_v = 3.3f, .cell_volt_crit_v = 3.0f,
        .nominal_current_max_a = 80.0f, .limp_l1_current_max_a = 40.0f,
        .limp_l2_current_max_a = 28.0f, .min_dwell_time = 1000ms
    };

    LimpHomeController ctrl(cfg);

    SensorTelemetry t{};
    t.mosfet_temp_c = 110.0f; // Викликає Limp L1
    t.bus_voltage_v = 22.5f;
    t.min_cell_voltage_v = 3.6f;
    t.total_current_a = 52.0f;
    t.timestamp = 50ms;

    auto out = ctrl.step(t);
    assert(out.current_state == State::LimpL1);
    assert(ctrl.dtc_count() == 1);

    auto record = ctrl.get_dtc_record(0);
    assert(record.has_value());
    assert(record->code == DtcCode::MosfetOvertemp);
    assert(record->mosfet_temp_c == 110.0f);
    assert(record->bus_voltage_v == 22.5f);

    std::cout << "[PASS] test_ring_buffer_freeze_frame (C++20)\n";
}

int main() {
    test_ring_buffer_freeze_frame();
    std::cout << "Всі C++20 модульні тести успішно пройдено!\n";
    return 0;
}
