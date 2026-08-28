// Inspector.cpp — Ідіоматична реалізація мовою C++20 із використанням RAII та std::expected
#include <iostream>
#include <memory>
#include <string_view>
#include <system_error>
#include <expected>
#include <systemd/sd-bus.h>

namespace nspawn {

struct SDBusDeleter {
    void operator()(sd_bus* bus) const noexcept {
        if (bus) sd_bus_unref(bus);
    }
};

struct SDMessageDeleter {
    void operator()(sd_bus_message* msg) const noexcept {
        if (msg) sd_bus_message_unref(msg);
    }
};

using BusPtr = std::unique_ptr<sd_bus, SDBusDeleter>;
using MessagePtr = std::unique_ptr<sd_bus_message, SDMessageDeleter>;

class MachineInspector {
public:
    static std::expected<MachineInspector, std::error_code> create() {
        sd_bus* raw_bus = nullptr;
        int r = sd_bus_open_system(&raw_bus);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }
        return MachineInspector(BusPtr(raw_bus));
    }

    std::expected<std::string, std::error_code> get_machine_path(std::string_view machine_name) const {
        sd_bus_error error = SD_BUS_ERROR_NULL;
        sd_bus_message* raw_msg = nullptr;

        int r = sd_bus_call_method(
            bus_.get(),
            "org.freedesktop.machine1",
            "/org/freedesktop/machine1",
            "org.freedesktop.machine1.Manager",
            "GetMachine",
            &error,
            &raw_msg,
            "s",
            machine_name.data()
        );

        sd_bus_error_free(&error);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }

        MessagePtr msg(raw_msg);
        const char* path_str = nullptr;
        r = sd_bus_message_read(msg.get(), "o", &path_str);
        if (r < 0 || !path_str) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }

        return std::string(path_str);
    }

private:
    explicit MachineInspector(BusPtr bus) : bus_(std::move(bus)) {}
    BusPtr bus_;
};

} // namespace nspawn

int main(int argc, char* argv[]) {
    const std::string_view target_machine = (argc > 1) ? argv[1] : "web-node1";

    auto inspector_res = nspawn::MachineInspector::create();
    if (!inspector_res) {
        std::cerr << "Помилка ініціалізації D-Bus: " << inspector_res.error().message() << '\n';
        return 1;
    }

    auto path_res = inspector_res->get_machine_path(target_machine);
    if (!path_res) {
        std::cerr << "Контейнер '" << target_machine << "' не знайдено або він зупинений.\n";
        return 1;
    }

    std::cout << "Успішно знайдено контейнер '" << target_machine << "'\n";
    std::cout << "Об'єктний шлях D-Bus: " << *path_res << '\n';
    return 0;
}
