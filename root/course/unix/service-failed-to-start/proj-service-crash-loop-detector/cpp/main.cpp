#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <systemd/sd-bus.h>
#include <csignal>
#include <format>
#include <expected>

namespace systemd_probe {

struct UnitDiagnostics {
    std::string active_state;
    std::string sub_state;
    std::string result;
    uint32_t n_restarts{0};
    uint64_t restart_usec{0};
    uint32_t main_pid{0};
    int32_t main_code{0};
    int32_t main_status{0};
};

struct BusDeleter {
    void operator()(sd_bus* b) const noexcept {
        if (b) ::sd_bus_unref(b);
    }
};

struct PathDeleter {
    void operator()(char* p) const noexcept {
        if (p) ::free(p);
    }
};

using ScopedBus = std::unique_ptr<sd_bus, BusDeleter>;
using ScopedPath = std::unique_ptr<char, PathDeleter>;

class Inspector {
public:
    static std::expected<Inspector, std::string> create() {
        sd_bus* raw_bus = nullptr;
        int r = ::sd_bus_open_system(&raw_bus);
        if (r < 0) {
            return std::unexpected(std::string("Не вдалося відкрити D-Bus: ") + ::strerror(-r));
        }
        return Inspector(ScopedBus(raw_bus));
    }

    std::expected<UnitDiagnostics, std::string> probe(std::string_view unit_name) const {
        char* raw_path = nullptr;
        int r = ::sd_bus_path_encode("/org/freedesktop/systemd1/unit", unit_name.data(), &raw_path);
        if (r < 0) {
            return std::unexpected(std::string("Помилка кодування шляху: ") + ::strerror(-r));
        }
        ScopedPath path(raw_path);

        UnitDiagnostics diag;

        diag.active_state = getStringProperty(path.get(), "org.freedesktop.systemd1.Unit", "ActiveState");
        diag.sub_state = getStringProperty(path.get(), "org.freedesktop.systemd1.Unit", "SubState");
        diag.result = getStringProperty(path.get(), "org.freedesktop.systemd1.Unit", "Result");

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "NRestarts",
                                      nullptr, 'u', &diag.n_restarts);

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "RestartUSec",
                                      nullptr, 't', &diag.restart_usec);

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "ExecMainPID",
                                      nullptr, 'u', &diag.main_pid);

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "ExecMainCode",
                                      nullptr, 'i', &diag.main_code);

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "ExecMainStatus",
                                      nullptr, 'i', &diag.main_status);

        return diag;
    }

private:
    explicit Inspector(ScopedBus bus) : bus_(std::move(bus)) {}

    std::string getStringProperty(const char* path, const char* iface, const char* prop) const {
        char* val = nullptr;
        int r = ::sd_bus_get_property_string(bus_.get(), "org.freedesktop.systemd1", path,
                                             iface, prop, nullptr, &val);
        if (r >= 0 && val) {
            std::string res(val);
            ::free(val);
            return res;
        }
        return {};
    }

    ScopedBus bus_;
};

void printReport(std::string_view unit_name, const UnitDiagnostics& diag) {
    std::cout << "=================================================================\n";
    std::cout << "ДІАГНОСТИЧНИЙ ПАСПОРТ ЮНІТА: " << unit_name << "\n";
    std::cout << "=================================================================\n";
    std::cout << "Стан (Active/Sub):    " << diag.active_state << " / " << diag.sub_state << "\n";
    std::cout << "Результат менеджера:  " << diag.result << "\n";
    std::cout << "Кількість перезапусків: " << diag.n_restarts
              << " (інтервал: " << (static_cast<double>(diag.restart_usec) / 1'000'000.0) << " c)\n";
    std::cout << "Останній PID:          " << diag.main_pid
              << " (код: " << diag.main_code << ", статус: " << diag.main_status << ")\n";
    std::cout << "-----------------------------------------------------------------\n";

    std::cout << "АНАЛІЗ ТА РЕКОМЕНДАЦІЇ:\n";

    if (diag.result == "start-limit-hit") {
        std::cout << "⚠️  КРИТИЧНО: Служба потрапила в CrashLoop і заблокована менеджером!\n"
                  << "    Перевищено ліміт StartLimitBurst у межах StartLimitIntervalSec.\n"
                  << "    Щоб відновити спроби запуску після виправлення причини, виконайте:\n"
                  << "    --> systemctl reset-failed " << unit_name << "\n";
    } else if (diag.sub_state == "auto-restart") {
        std::cout << "⚠️  УВАГА: Служба перебуває в активній рестарт-петлі (стан очікування).\n"
                  << "    Зафіксовано вже " << diag.n_restarts << " невдалих перезапусків.\n"
                  << "    Зупиніть службу для запобігання спаму в логах:\n"
                  << "    --> systemctl stop " << unit_name << "\n";
    }

    if (diag.main_code == CLD_EXITED) {
        if (diag.main_status == 203) {
            std::cout << "❌ ПОМИЛКА 203/EXEC: Ядро не змогло виконати бінарник.\n"
                      << "   1. Перевірте існування файлу ExecStart= та права chmod +x.\n"
                      << "   2. Якщо це скрипт — перевірте шлях до інтерпретатора у шебангу (#!).\n"
                      << "   3. Перевірте наявність динамічного лінкера (ldd <binary>).\n";
        } else if (diag.main_status == 217) {
            std::cout << "❌ ПОМИЛКА 217/USER: Неможливо перемкнутися на користувача в User=.\n"
                      << "   Користувач відсутній у /etc/passwd або мережевий NSS (SSSD/LDAP) ще не готовий.\n";
        } else if (diag.main_status == 226) {
            std::cout << "❌ ПОМИЛКА 226/NAMESPACE: Збій налаштування пісочниці монтування.\n"
                      << "   Перевірте сумісність директив ProtectSystem=, PrivateTmp= з файловою системою.\n";
        } else if (diag.main_status != 0) {
            std::cout << "❌ ПРИКЛАДНИЙ ЗБІЙ (код " << diag.main_status << "): Застосунок вийшов із власною помилкою.\n"
                      << "   Перегляньте точний лог падіння:\n"
                      << "   --> journalctl -u " << unit_name << " -b -e --no-pager\n";
        }
    } else if (diag.main_code == CLD_KILLED) {
        if (diag.main_status == SIGKILL) {
            std::cout << "❌ ЗНИЩЕНО СИГНАЛОМ SIGKILL (9):\n"
                      << "   1. Спрацював ядерний cgroup OOM-killer через перевищення MemoryMax=.\n"
                      << "   2. Вичерпано таймаут запуску TimeoutStartSec= (Type=notify не надіслав READY=1).\n"
                      << "   Перевірте dmesg: dmesg -T | grep -i oom\n";
        } else if (diag.main_status == SIGABRT) {
            std::cout << "❌ ЗНИЩЕНО СИГНАЛОМ SIGABRT (6): Програма викликала abort() або впав assert.\n";
        } else if (diag.main_status == SIGSEGV) {
            std::cout << "❌ ЗНИЩЕНО СИГНАЛОМ SIGSEGV (11): Порушення адресації пам'яті (Segfault).\n";
        }
    }

    std::cout << "=================================================================\n";
}

} // namespace systemd_probe

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <назва_юніта.service>\n";
        return 1;
    }

    auto inspector = systemd_probe::Inspector::create();
    if (!inspector) {
        std::cerr << "Помилка ініціалізації: " << inspector.error() << "\n";
        return 1;
    }

    auto diag = inspector->probe(argv[1]);
    if (!diag) {
        std::cerr << "Помилка опитування юніта: " << diag.error() << "\n";
        return 1;
    }

    systemd_probe::printReport(argv[1], *diag);
    return 0;
}
