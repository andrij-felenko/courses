#include <iostream>
#include <string_view>
#include <chrono>
#include <thread>
#include <systemd/sd-daemon.h>

class SystemdNotifier {
public:
    static bool notify(std::string_view message) noexcept {
        int res = sd_notify(0, message.data());
        return res > 0;
    }

    static bool notify_ready(std::string_view status = "") noexcept {
        if (status.empty()) {
            return notify("READY=1");
        }
        std::string payload = "READY=1\nSTATUS=";
        payload.append(status);
        return notify(payload);
    }

    static bool watchdog_ping() noexcept {
        return notify("WATCHDOG=1");
    }
};

int main() {
    std::cout << "[C++] Starting service setup...\n";
    std::this_thread::sleep_for(std::chrono::seconds(2));

    if (SystemdNotifier::notify_ready("C++ Service ready and serving traffic.")) {
        std::cout << "[C++] Systemd readiness acknowledged.\n";
    }

    for (int i = 0; i < 5; ++i) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        SystemdNotifier::watchdog_ping();
    }

    SystemdNotifier::notify("STOPPING=1\nSTATUS=Terminating process.");
    return 0;
}
