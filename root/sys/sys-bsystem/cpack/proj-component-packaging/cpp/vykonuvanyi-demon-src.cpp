#include "telemetry/metrics.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <array>

int main() {
    std::cout << "Starting Telemetry Daemon v1.4.2...\n";
    telemetry_snapshot_t snapshot{};
    std::array<char, 256> buffer{};

    for (int i = 0; i < 3; ++i) {
        if (telemetry_collect_metrics(&snapshot) == 0) {
            telemetry_format_json(&snapshot, buffer.data(), buffer.size());
            std::cout << buffer.data();
        }
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    return 0;
}
