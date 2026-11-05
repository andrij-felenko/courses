#include <iostream>
#include "debouncer.hpp"

int main() {
    embedded::Debouncer<20, 500> btn;

    bool trace[] = {
        false, true, false, true, true, true, true, true, true, true, // bounce into press
        true, true, true, true, true, true, true, true, true, true,   // hold
        true, true, true, true, true, false, true, false, false, false // bounce release
    };

    std::cout << "Testing C++ Debouncer FSM:\n";
    for (size_t i = 0; i < sizeof(trace) / sizeof(trace[0]); ++i) {
        uint16_t time_ms = static_cast<uint16_t>(i * 2);
        auto evt = btn.update(trace[i], 2);

        if (evt == embedded::ButtonEvent::Pressed) {
            std::cout << "[" << time_ms << " ms] Button Pressed!\n";
        } else if (evt == embedded::ButtonEvent::Released) {
            std::cout << "[" << time_ms << " ms] Button Released!\n";
        }
    }

    return 0;
}
