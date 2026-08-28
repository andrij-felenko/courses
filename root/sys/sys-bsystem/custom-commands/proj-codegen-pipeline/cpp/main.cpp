// src/main.cpp
#include "messages.hpp"
#include <iostream>

int main() {
    TelemetryFrame frame{};
    frame.timestamp = 1718000000;
    frame.voltage = 12.58f;
    frame.current = 1.42f;

    print_frame(frame);
    return 0;
}
