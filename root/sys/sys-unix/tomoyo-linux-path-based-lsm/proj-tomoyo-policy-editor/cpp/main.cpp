#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <system_error>
#include <expected>

namespace fs = std::filesystem;

class TomoyoSecurityFS {
public:
    static constexpr std::string_view SecurityFSRoot = "/sys/kernel/security/tomoyo";

    TomoyoSecurityFS() {
        if (!fs::exists(SecurityFSRoot)) {
            throw std::runtime_error("TOMOYO SecurityFS не знайдено за шляхом: " + 
                                     std::string(SecurityFSRoot));
        }
    }

    // Зчитування статистики ядра у формі рядка
    [[nodiscard]] std::expected<std::string, std::string> readStatistics() const {
        const fs::path statPath = fs::path(SecurityFSRoot) / "stat";
        std::ifstream statFile(statPath);

        if (!statFile.is_open()) {
            return std::unexpected("Не вдалося відкрити файл статистики: " + statPath.string());
        }

        std::string content((std::istreambuf_iterator<char>(statFile)),
                             std::istreambuf_iterator<char>());
        return content;
    }

    // Динамічний запис правила доменів через RAII файловий потік
    [[nodiscard]] std::expected<void, std::string> appendRule(std::string_view domain, 
                                                             std::string_view rule) const {
        const fs::path policyPath = fs::path(SecurityFSRoot) / "domain_policy";
        std::ofstream policyFile(policyPath, std::ios::app);

        if (!policyFile.is_open()) {
            return std::unexpected("Не вдалося відкрити domain_policy для запису. "
                                   "Перевірте привілеї та вміст manager.conf.");
        }

        policyFile << domain << "\n" << rule << "\n";
        if (!policyFile.good()) {
            return std::unexpected("Помилка запису в domain_policy.");
        }

        return {};
    }
};

int main(int argc, char* argv[]) {
    try {
        TomoyoSecurityFS tomoyo;

        std::cout << "=== Системний монітор TOMOYO Linux (C++20) ===\n";
        auto statResult = tomoyo.readStatistics();
        if (statResult) {
            std::cout << *statResult << '\n';
        } else {
            std::cerr << "Помилка: " << statResult.error() << '\n';
            return EXIT_FAILURE;
        }

        if (argc == 3) {
            const std::string_view domain = argv[1];
            const std::string_view rule = argv[2];

            auto writeResult = tomoyo.appendRule(domain, rule);
            if (writeResult) {
                std::cout << "Успішно додано правило:\n  Домен: " << domain 
                          << "\n  Правило: " << rule << '\n';
            } else {
                std::cerr << "Помилка запису: " << writeResult.error() << '\n';
                return EXIT_FAILURE;
            }
        }

    } catch (const std::exception& ex) {
        std::cerr << "Критичний збій: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
