// C++: Ідіоматична реалізація тестового демона з RAII та обробкою помилок через std::system_error
#include <iostream>
#include <fstream>
#include <string>
#include <system_error>
#include <cerrno>

class daemon_tester {
public:
    static void test_log_access(const std::string& log_path) {
        std::ofstream log_stream(log_path, std::ios::app);
        if (!log_stream.is_open()) {
            std::cerr << "[ПОМИЛКА] Не вдалося відкрити лог " << log_path << ": "
                      << std::system_error(errno, std::generic_category()).what() << "\n";
            return;
        }
        log_stream << "C++ Демон успішно записав рядок у лог під доменом mydaemon_t.\n";
        std::cout << "[ОК] Запис у власний лог-файл пройшов успішно.\n";
    }

    static void test_unauthorized_access(const std::string& secret_path) {
        std::ifstream secret_stream(secret_path);
        if (!secret_stream.is_open()) {
            std::cout << "[ОК] Спробу читання " << secret_path 
                      << " заблоковано SELinux! Причина: "
                      << std::system_error(errno, std::generic_category()).what() 
                      << " (errno=" << errno << ")\n";
        } else {
            std::cerr << "[УВАГА] Помилка безпеки: відкрити " << secret_path << " вдалося!\n";
        }
    }
};

int main() {
    std::cout << "=== Запуск C++ перевірки доступу демона mydaemon ===\n";

    daemon_tester::test_log_access("/var/log/mydaemon.log");
    daemon_tester::test_unauthorized_access("/etc/shadow");

    return 0;
}
