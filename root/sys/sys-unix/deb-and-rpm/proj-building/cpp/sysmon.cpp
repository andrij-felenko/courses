// sysmon.cpp — Системний демон фонового моніторингу на C++
#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <csignal>
#include <syslog.h>

namespace {
    std::atomic<bool> g_keep_running{true};
}

void signal_handler(int signal) {
    if (signal == SIGINT || signal == SIGTERM) {
        g_keep_running = false;
    }
}

class SyslogGuard {
public:
    explicit SyslogGuard(const char* ident) {
        openlog(ident, LOG_PID | LOG_CONS, LOG_DAEMON);
    }
    ~SyslogGuard() {
        syslog(LOG_INFO, "Демон sysmon зупинено за сигналом (RAII).");
        closelog();
    }
};

int main() {
    SyslogGuard log_guard("sysmon");
    syslog(LOG_INFO, "Демон sysmon (C++) успішно запущено.");

    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    while (g_keep_running) {
        syslog(LOG_INFO, "sysmon: системний статус OK");
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }

    return 0;
}
