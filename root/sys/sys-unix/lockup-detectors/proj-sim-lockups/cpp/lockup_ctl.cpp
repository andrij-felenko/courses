// lockup_ctl.cpp — Утиліта моніторингу та ініціалізації тестів зависань ядра (C++20)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <optional>
#include <format>

namespace fs = std::filesystem;

class LockupController {
public:
    static void printUsage(std::string_view progName) {
        std::cerr << std::format("Використання: {} <soft|hard|hung|status>\n", progName)
                  << "  soft   - викликати Soft Lockup (25 с утримування spinlock)\n"
                  << "  hard   - викликати Hard Lockup (local_irq_disable + dead loop)\n"
                  << "  hung   - викликати Hung Task (150 с у TASK_UNINTERRUPTIBLE)\n"
                  << "  status - перевірити поточні параметри watchdog у sysctl\n";
    }

    static std::optional<int> readSysctl(std::string_view path) {
        std::ifstream file(path.data());
        if (!file.is_open()) return std::nullopt;
        int value = 0;
        if (file >> value) return value;
        return std::nullopt;
    }

    static void showStatus() {
        std::cout << "=== Стан сторожових таймерів ядра Linux ===\n";
        auto printParam = [](std::string_view name, std::string_view path, std::string_view unit = "") {
            auto val = readSysctl(path);
            if (val.has_value()) {
                std::cout << std::format("{:<26} {}{}\n", name, *val, unit.empty() ? "" : std::format(" {}", unit));
            } else {
                std::cout << std::format("{:<26} [недоступно]\n", name);
            }
        };

        printParam("kernel.watchdog:", "/proc/sys/kernel/watchdog");
        printParam("kernel.watchdog_thresh:", "/proc/sys/kernel/watchdog_thresh", "с");
        printParam("kernel.nmi_watchdog:", "/proc/sys/kernel/nmi_watchdog");
        printParam("kernel.softlockup_panic:", "/proc/sys/kernel/softlockup_panic");
        printParam("kernel.hardlockup_panic:", "/proc/sys/kernel/hardlockup_panic");
        printParam("kernel.hung_task_timeout:", "/proc/sys/kernel/hung_task_timeout_secs", "с");
        printParam("kernel.hung_task_panic:", "/proc/sys/kernel/hung_task_panic");
    }

    static bool triggerLockup(std::string_view nodeName) {
        const fs::path nodePath = fs::path("/sys/kernel/debug/lockup_trigger") / nodeName;
        std::ofstream triggerFile(nodePath);
        if (!triggerFile.is_open()) {
            std::cerr << std::format("Помилка відкриття {}: чи завантажено модуль ядра?\n", nodePath.string());
            return false;
        }
        triggerFile << "1\n";
        if (triggerFile.bad()) {
            std::cerr << "Помилка під час запису команди у вузол debugfs\n";
            return false;
        }
        std::cout << std::format("Тригер '{}' успішно активовано.\n", nodeName);
        return true;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        LockupController::printUsage(argv[0]);
        return 1;
    }

    const std::string_view cmd = argv[1];
    if (cmd == "status") {
        LockupController::showStatus();
        return 0;
    } else if (cmd == "soft") {
        return LockupController::triggerLockup("trigger_soft_lockup") ? 0 : 1;
    } else if (cmd == "hard") {
        return LockupController::triggerLockup("trigger_hard_lockup") ? 0 : 1;
    } else if (cmd == "hung") {
        return LockupController::triggerLockup("trigger_hung_task") ? 0 : 1;
    } else {
        LockupController::printUsage(argv[0]);
        return 1;
    }
}
