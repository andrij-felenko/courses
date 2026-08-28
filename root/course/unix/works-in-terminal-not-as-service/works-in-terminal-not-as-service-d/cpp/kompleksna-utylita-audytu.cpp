#include <iostream>
#include <cstdlib>
#include <filesystem>
#include <unistd.h>
#include <sys/resource.h>
#include <fstream>

namespace fs = std::filesystem;

void perform_full_system_audit() {
    std::cout << "=== ДІАГНОСТИКА СЕРЕДОВИЩА ПРОЦЕСУ ===\n";

    // 1. Перевірка TTY
    bool tty_in = isatty(fileno(stdin));
    bool tty_out = isatty(fileno(stdout));
    std::cout << "[TTY] stdin: " << (tty_in ? "TTY (interactive)" : "PIPE/SOCKET (service)")
              << ", stdout: " << (tty_out ? "TTY (_IOLBF)" : "PIPE/SOCKET (_IOFBF)") << "\n";

    // 2. Перевірка CWD
    std::error_code ec;
    fs::path cwd = fs::current_path(ec);
    if (!ec) {
        std::cout << "[CWD] Поточний каталог: " << cwd.string() << "\n";
        if (cwd == "/") {
            std::cout << "  [УВАГА] Процес запущено в корені /! Відносні шляхи будуть хибними.\n";
        }
    }

    // 3. Перевірка критичних змінних
    const char* path = std::getenv("PATH");
    const char* home = std::getenv("HOME");
    std::cout << "[ENV] PATH: " << (path ? path : "(NULL)") << "\n"
              << "[ENV] HOME: " << (home ? home : "(NULL)") << "\n";

    // 4. Ліміти дескрипторів
    struct rlimit rl{};
    if (getrlimit(RLIMIT_NOFILE, &rl) == 0) {
        std::cout << "[LIMITS] NOFILE soft: " << rl.rlim_cur
                  << ", hard: " << rl.rlim_max << "\n";
    }

    // 5. Тестовий запис у /tmp
    std::ofstream tmp_test("/tmp/.audit_service_probe");
    if (tmp_test.is_open()) {
        std::cout << "[FS] Запис у /tmp: УСПІХ\n";
        tmp_test.close();
        std::filesystem::remove("/tmp/.audit_service_probe");
    } else {
        std::cout << "[FS] Помилка запису у /tmp (можливо увімкнено ProtectSystem/PrivateTmp)\n";
    }
    std::cout << "=========================================\n";
}
