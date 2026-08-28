#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <sstream>
#include <iomanip>

namespace fs = std::filesystem;

// Структура заблокованого вузла графа
struct LockedPackage {
    std::string name;
    std::string version;
    std::string expected_sha256;
    bool is_exact_version;
};

// Перевірка, чи не містить версія небезпечних операторів діапазонів
constexpr bool is_strictly_pinned(std::string_view ver) noexcept {
    if (ver.empty()) return false;
    for (char c : ver) {
        if (c == '^' || c == '~' || c == '>' || c == '<' || c == '*' || c == '=') {
            return false;
        }
    }
    return true;
}

// Парсер формату key=value для замкового файлу
class LockfileValidator {
public:
    explicit LockfileValidator(fs::path lockfile_path) 
        : path_(std::move(lockfile_path)) {}

    std::expected<std::vector<LockedPackage>, std::string> parse_and_validate() const {
        if (!fs::exists(path_)) {
            return std::unexpected("Помилка: Замковий файл не знайдено: " + path_.string());
        }

        std::ifstream file(path_);
        if (!file.is_open()) {
            return std::unexpected("Помилка відкриття файлу для читання.");
        }

        std::vector<LockedPackage> packages;
        std::string line;
        size_t line_num = 0;

        while (std::getline(file, line)) {
            ++line_num;
            if (line.empty() || line.starts_with('#')) {
                continue; // Пропуск коментарів і порожніх рядків
            }

            std::istringstream iss(line);
            std::string name, version, sha256;
            
            // Формат рядка: <package_name> <exact_version> <sha256_hash>
            if (!(iss >> name >> version >> sha256)) {
                return std::unexpected("Синтаксична помилка в рядку " + std::to_string(line_num));
            }

            if (!is_strictly_pinned(version)) {
                return std::unexpected("Порушення детермінізму: версія для '" + name + 
                                       "' містить плаваючий діапазон: " + version);
            }

            if (sha256.length() != 64) {
                return std::unexpected("Недійсний SHA-256 хеш для '" + name + "': " + sha256);
            }

            packages.push_back(LockedPackage{
                .name = std::move(name),
                .version = std::move(version),
                .expected_sha256 = std::move(sha256),
                .is_exact_version = true
            });
        }

        return packages;
    }

    bool verify_file_immutability(const fs::file_time_type& original_time) const {
        std::error_code ec;
        auto current_time = fs::last_write_time(path_, ec);
        if (ec) return false;
        return current_time == original_time;
    }

    fs::path path() const noexcept { return path_; }

private:
    fs::path path_;
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: ci_lock_checker <шлях_до_lockfile>\n";
        return 1;
    }

    const fs::path lock_path = argv[1];
    LockfileValidator validator(lock_path);

    std::cout << "[CI-SECURITY] Перевірка замкового файлу: " << lock_path << "\n";

    auto result = validator.parse_and_validate();
    if (!result) {
        std::cerr << "[FAIL] Валідація провалена: " << result.error() << "\n";
        return 2;
    }

    const auto& pkgs = *result;
    std::cout << "[OK] Успішно перевірено " << pkgs.size() << " заблокованих залежностей.\n";
    for (const auto& pkg : pkgs) {
        std::cout << "  ✓ " << std::left << std::setw(20) << pkg.name 
                  << " версія: " << std::setw(10) << pkg.version 
                  << " [SHA256: " << pkg.expected_sha256.substr(0, 12) << "...]\n";
    }

    std::cout << "[CI-SECURITY] Усі версії закріплено суворо. Збірку дозволено.\n";
    return 0;
}
