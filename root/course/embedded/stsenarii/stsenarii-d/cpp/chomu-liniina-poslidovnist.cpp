#include <chrono>
#include <thread>

/* НАЇВНИЙ БЛОКУЮЧИЙ ПІДХІД НА C++ — ДЖЕРЕЛО КАТАСТРОФ */
void prepare_start_sequence_blocking() {
    using namespace std::chrono_literals;

    valve_open(ValveId::Drain);
    std::this_thread::sleep_for(500ms);   /* Блокування потоку */

    pump_set_power(PumpId::Main, 30);
    auto t0 = std::chrono::steady_clock::now();
    while (sensor_get_flow() < 4.0f) {    /* Блокуюче опитування */
        if (std::chrono::steady_clock::now() - t0 > 3000ms) {
            system_panic();               /* Аварійне скидання */
        }
        std::this_thread::sleep_for(10ms);
    }

    valve_close(ValveId::Drain);
    pump_set_power(PumpId::Main, 80);
    while (sensor_get_pressure() < 3.5f) {
        std::this_thread::sleep_for(10ms);
    }

    heater_enable(HeaterId::Primary);
}
