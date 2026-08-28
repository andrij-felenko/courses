#include <iostream>
#include <fstream>
#include <filesystem>
#include <chrono>
#include <thread>
#include <syslog.h>
#include <format>

namespace fs = std::filesystem;

class SwiotlbWatcher {
    fs::path base_{"/sys/kernel/debug/swiotlb"};
    unsigned long nslabs_{0};
    unsigned long last_highwater_{0};
    unsigned long last_overflow_{0};

    [[nodiscard]] unsigned long read_ulong(std::string_view name) const {
        std::ifstream f(base_ / name);
        unsigned long v = 0;
        if (f >> v) return v;
        return 0;
    }

public:
    bool init() {
        openlog("swiotlb-watcher-cpp", LOG_PID | LOG_CONS, LOG_DAEMON);
        nslabs_ = read_ulong("io_tlb_nslabs");
        if (nslabs_ == 0) {
            syslog(LOG_ERR, "Помилка: не вдалося зчитати io_tlb_nslabs з debugfs");
            return false;
        }
        syslog(LOG_INFO, "Демон моніторингу запущено. Розмір пулу: %lu слотів", nslabs_);
        return true;
    }

    ~SwiotlbWatcher() {
        closelog();
    }

    void run(std::chrono::seconds interval) {
        while (true) {
            const auto cur_highwater = read_ulong("io_tlb_used_highwater");
            const auto cur_overflow = read_ulong("io_tlb_overflow");

            if (cur_overflow > last_overflow_) {
                const auto diff = cur_overflow - last_overflow_;
                const auto msg = std::format("КРИТИЧНО: Нові переповнення пулу (+{})! Загалом: {}", diff, cur_overflow);
                syslog(LOG_CRIT, "%s", msg.c_str());
                last_overflow_ = cur_overflow;
            }

            if (cur_highwater > last_highwater_) {
                const double pct = (static_cast<double>(cur_highwater) / static_cast<double>(nslabs_)) * 100.0;
                if (pct > 75.0) {
                    const auto msg = std::format("Попередження: Новий пік утилізації: {} слотів ({:.1f}%)", cur_highwater, pct);
                    syslog(LOG_WARNING, "%s", msg.c_str());
                }
                last_highwater_ = cur_highwater;
            }

            std::this_thread::sleep_for(interval);
        }
    }
};

int main() {
    SwiotlbWatcher watcher;
    if (!watcher.init()) {
        std::cerr << "Не вдалося ініціалізувати SwiotlbWatcher. Перевірте debugfs.\n";
        return 1;
    }

    watcher.run(std::chrono::seconds(5));
    return 0;
}
