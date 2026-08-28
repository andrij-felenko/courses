/* link_monitor_example.cpp — Приклад використання C++ класу в диспетчері завдань */
#include "link_monitor.hpp"
#include <iostream>

void process_radio_event(LinkMonitor& monitor, bool packet_arrived, int16_t rssi, int8_t snr, uint32_t now) {
    if (packet_arrived) {
        monitor.on_packet_received(rssi, snr, now);
    } else {
        monitor.update_scheduler(now);
    }

    const auto metrics = monitor.get_metrics(now);

    switch (metrics.state) {
        case LinkMonitor::State::Excellent:
            // Зв'язок стабільний: стандартний політний режим
            break;
        case LinkMonitor::State::Degraded:
            // Початок деградації: запит на збільшення потужності передавача
            break;
        case LinkMonitor::State::Critical:
            // Stage 1 Failsafe: примусове автовирівнювання кутів у горизонт
            break;
        case LinkMonitor::State::Lost:
            // Stage 2 Failsafe: активація автономного повернення додому (RTL)
            break;
    }
}
