#include <systemd/sd-daemon.h>
#include <string_view>

// Сповіщення менеджера systemd засобами C++
void notify_systemd_ready() noexcept {
    ::sd_notify(0, "READY=1\nSTATUS=C++ Сервер готовий до роботи");
}

// Надсилання пульсу працездатності сторожовому таймеру
void notify_systemd_watchdog() noexcept {
    ::sd_notify(0, "WATCHDOG=1");
}
