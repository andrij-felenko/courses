// controller.cpp — Програмна ізоляція станів через sd-bus RAII (C++)
#include <iostream>
#include <memory>
#include <string_view>
#include <system_error>
#include <systemd/sd-bus.h>

namespace systemd {

// Кастомний делітер для RAII обгортки шини sd_bus
struct BusDeleter {
    void operator()(sd_bus* b) const noexcept {
        if (b) {
            sd_bus_unref(b);
        }
    }
};
using BusPtr = std::unique_ptr<sd_bus, BusDeleter>;

// Кастомний делітер для RAII обгортки D-Bus повідомлення
struct MessageDeleter {
    void operator()(sd_bus_message* m) const noexcept {
        if (m) {
            sd_bus_message_unref(m);
        }
    }
};
using MessagePtr = std::unique_ptr<sd_bus_message, MessageDeleter>;

class TargetController {
public:
    /**
     * Виконує програмну ізоляцію вказаного target-юніта.
     * @param target_name Назва target-юніта
     * @throws std::system_error або std::runtime_error при помилках D-Bus
     */
    static void isolate(std::string_view target_name) {
        sd_bus* raw_bus = nullptr;
        int r = sd_bus_open_system(&raw_bus);
        if (r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося відкрити системну шину D-Bus");
        }
        BusPtr bus(raw_bus);

        std::cout << "Надсилання запиту на ізоляцію для: " << target_name << "...\n";

        sd_bus_error error = SD_BUS_ERROR_NULL;
        sd_bus_message* raw_reply = nullptr;

        r = sd_bus_call_method(
            bus.get(),
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1",
            "org.freedesktop.systemd1.Manager",
            "StartUnit",
            &error,
            &raw_reply,
            "ss",
            target_name.data(),
            "isolate"
        );

        MessagePtr reply(raw_reply);

        if (r < 0) {
            std::string err_msg = error.message ? error.message : "Невідома помилка D-Bus";
            sd_bus_error_free(&error);
            throw std::runtime_error("Збій ізоляції станів: " + err_msg);
        }

        const char* job_path = nullptr;
        r = sd_bus_message_read(reply.get(), "o", &job_path);
        if (r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося зчитати ObjectPath роботи");
        }

        std::cout << "Транзакційну роботу ізоляції успішно створено: " << job_path << '\n';
    }
};

} // namespace systemd

int main(int argc, char* argv[]) {
    try {
        std::string_view target = (argc > 1) ? argv[1] : "kiosk.target";
        systemd::TargetController::isolate(target);
        return EXIT_SUCCESS;
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
}
