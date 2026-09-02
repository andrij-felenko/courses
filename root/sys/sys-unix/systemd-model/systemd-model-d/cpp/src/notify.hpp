#pragma once

#include <systemd/sd-daemon.h>

#include <chrono>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>
#include <system_error>

// Тонка обгортка над протоколом sd_notify: текст протоколу зібрано тут, щоб
// решта коду оперувала намірами — «готовий», «живий», «зупиняюсь».
namespace notify {

inline void send(const std::string& message) {
    const int r = sd_notify(0, message.c_str());
    // r == 0 означає лише, що NOTIFY_SOCKET не заданий: юніт не Type=notify
    // або програму запустили руками. Це нормальний режим, а не помилка.
    if (r < 0) {
        throw std::system_error{-r, std::generic_category(), "sd_notify"};
    }
}

inline void ready(std::string_view status) {
    send("READY=1\nSTATUS=" + std::string{status} + "\n");
}

inline void watchdog() { send("WATCHDOG=1"); }

inline void stopping(std::string_view status) {
    send("STOPPING=1\nSTATUS=" + std::string{status} + "\n");
}

// Інтервал із директиви WatchdogSec=; nullopt — нагляду за службою немає.
inline std::optional<std::chrono::microseconds> watchdog_interval() {
    std::uint64_t usec = 0;
    const int r = sd_watchdog_enabled(0, &usec);
    if (r < 0) {
        throw std::system_error{-r, std::generic_category(), "sd_watchdog_enabled"};
    }
    if (r == 0 || usec == 0) {
        return std::nullopt;
    }
    return std::chrono::microseconds{usec};
}

}  // namespace notify
