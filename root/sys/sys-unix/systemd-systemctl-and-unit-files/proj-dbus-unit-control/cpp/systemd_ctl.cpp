// systemd_ctl.cpp — Програмне управління юнітами C++17 RAII обгорткою над sd-bus
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <system_error>
#include <systemd/sd-bus.h>

namespace sysd {

// RAII функтор для автоматичного вивантаження шини D-Bus
struct bus_deleter {
    void operator()(sd_bus* b) const noexcept {
        if (b) sd_bus_unref(b);
    }
};

// RAII функтор для вивантаження повідомлень D-Bus
struct message_deleter {
    void operator()(sd_bus_message* m) const noexcept {
        if (m) sd_bus_message_unref(m);
    }
};

using bus_ptr = std::unique_ptr<sd_bus, bus_deleter>;
using message_ptr = std::unique_ptr<sd_bus_message, message_deleter>;

class manager {
public:
    static manager connect_system() {
        sd_bus* b = nullptr;
        int r = sd_bus_open_system(&b);
        if (r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося відкрити системну шину D-Bus");
        }
        return manager(bus_ptr(b));
    }

    std::string get_unit_path(std::string_view unit_name) const {
        sd_bus_error error = SD_BUS_ERROR_NULL;
        sd_bus_message* reply_raw = nullptr;

        int r = sd_bus_call_method(bus_.get(),
                                   "org.freedesktop.systemd1",
                                   "/org/freedesktop/systemd1",
                                   "org.freedesktop.systemd1.Manager",
                                   "GetUnit",
                                   &error,
                                   &reply_raw,
                                   "s",
                                   std::string(unit_name).c_str());
        
        message_ptr reply(reply_raw);
        if (r < 0) {
            std::string msg = error.message ? error.message : "Помилка D-Bus виклику";
            sd_bus_error_free(&error);
            throw std::runtime_error(msg);
        }

        char* path = nullptr;
        r = sd_bus_message_read(reply.get(), "o", &path);
        if (r < 0 || !path) {
            throw std::runtime_error("Не вдалося розпарсити об'єктний шлях юніта з відповіді");
        }

        return std::string(path);
    }

    std::string get_active_state(std::string_view unit_path) const {
        sd_bus_error error = SD_BUS_ERROR_NULL;
        char* state_str = nullptr;

        int r = sd_bus_get_property_string(bus_.get(),
                                           "org.freedesktop.systemd1",
                                           std::string(unit_path).c_str(),
                                           "org.freedesktop.systemd1.Unit",
                                           "ActiveState",
                                           &error,
                                           &state_str);
        if (r < 0) {
            std::string msg = error.message ? error.message : "Помилка читання ActiveState";
            sd_bus_error_free(&error);
            throw std::runtime_error(msg);
        }

        std::string result(state_str);
        free(state_str);
        return result;
    }

    std::string start_unit(std::string_view unit_name, std::string_view mode = "replace") const {
        sd_bus_error error = SD_BUS_ERROR_NULL;
        sd_bus_message* reply_raw = nullptr;

        int r = sd_bus_call_method(bus_.get(),
                                   "org.freedesktop.systemd1",
                                   "/org/freedesktop/systemd1",
                                   "org.freedesktop.systemd1.Manager",
                                   "StartUnit",
                                   &error,
                                   &reply_raw,
                                   "ss",
                                   std::string(unit_name).c_str(),
                                   std::string(mode).c_str());

        message_ptr reply(reply_raw);
        if (r < 0) {
            std::string msg = error.message ? error.message : "Не вдалося запустити юніт";
            sd_bus_error_free(&error);
            throw std::runtime_error(msg);
        }

        char* job_path = nullptr;
        r = sd_bus_message_read(reply.get(), "o", &job_path);
        return job_path ? std::string(job_path) : std::string();
    }

private:
    explicit manager(bus_ptr b) : bus_(std::move(b)) {}
    bus_ptr bus_;
};

} // namespace sysd

int main(int argc, char* argv[]) {
    try {
        const std::string unit_name = (argc > 1) ? argv[1] : "app@worker1.service";
        auto sysd_mgr = sysd::manager::connect_system();
        std::cout << "Успішне підключення до D-Bus systemd (C++ RAII).\n";

        std::string path = sysd_mgr.get_unit_path(unit_name);
        std::cout << "Об'єктний шлях: " << path << '\n';

        std::string state = sysd_mgr.get_active_state(path);
        std::cout << "Поточний ActiveState: " << state << '\n';

        std::cout << "Запуск юніта " << unit_name << "...\n";
        std::string job = sysd_mgr.start_unit(unit_name);
        std::cout << "Створено транзакційну роботу Job: " << job << '\n';
    }
    catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
