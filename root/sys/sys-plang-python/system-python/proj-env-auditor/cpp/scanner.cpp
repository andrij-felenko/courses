// scanner.cpp — Ідіоматичний C++20 аудит середовища CPython
#include <iostream>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>
#include <string_view>
#include <expected>

namespace fs = std::filesystem;

class EnvironmentAuditor {
public:
    struct MarkerInfo {
        fs::path path;
        std::string content;
    };

    static std::expected<MarkerInfo, std::string> find_pep668_marker() {
        const std::vector<fs::path> candidate_paths = {
            "/usr/lib/python3.12/EXTERNALLY-MANAGED",
            "/usr/lib64/python3.12/EXTERNALLY-MANAGED",
            "/usr/lib/python3.11/EXTERNALLY-MANAGED",
            "/usr/lib64/python3.11/EXTERNALLY-MANAGED",
            "/usr/lib/python3/EXTERNALLY-MANAGED"
        };

        for (const auto& path : candidate_paths) {
            std::error_code ec;
            if (fs::is_regular_file(path, ec)) {
                std::ifstream file(path);
                if (!file.is_open()) {
                    return std::unexpected("Не вдалося відкрити знайдений файл: " + path.string());
                }
                std::string content((std::istreambuf_iterator<char>(file)),
                                     std::istreambuf_iterator<char>());
                return MarkerInfo{path, std::move(content)};
            }
        }

        return std::unexpected("Маркер EXTERNALLY-MANAGED не знайдено");
    }

    static void report_status() {
        std::cout << "=== C++20 АУДИТОР СИСТЕМНОГО PYTHON ===\n";
        auto marker_result = find_pep668_marker();
        if (marker_result.has_value()) {
            const auto& [path, content] = marker_result.value();
            std::cout << "[ЗНАЙДЕНО] Маркер захисту PEP 668: " << path << "\n";
            std::cout << "--- Повідомлення дистрибутива ---\n"
                      << content
                      << "---------------------------------\n";
        } else {
            std::cout << "[УВАГА] " << marker_result.error() << "\n";
        }
    }
};

int main() {
    EnvironmentAuditor::report_status();
    return 0;
}
