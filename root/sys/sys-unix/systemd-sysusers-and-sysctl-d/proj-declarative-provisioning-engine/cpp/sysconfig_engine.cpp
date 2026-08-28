// sysconfig_engine.cpp — Ідіоматична C++20 реалізація
#include <iostream>
#include <fstream>
#include <filesystem>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <expected>
#include <shadow.h>
#include <pwd.h>

namespace fs = std::filesystem;

// RAII-обгортка для безпечного блокування бази даних користувачів
class UserDbLock {
public:
    UserDbLock() {
        locked_ = (lckpwdf() == 0);
    }
    ~UserDbLock() {
        if (locked_) ulckpwdf();
    }
    UserDbLock(const UserDbLock&) = delete;
    UserDbLock& operator=(const UserDbLock&) = delete;

    [[nodiscard]] bool is_locked() const noexcept { return locked_; }
private:
    bool locked_{false};
};

struct ConfigEntry {
    std::string name;
    fs::path full_path;
    int priority{0};
    bool is_masked{false};
};

class SysConfigEngine {
public:
    // Сканування каталогів .d з використанням std::filesystem
    static std::vector<ConfigEntry> scan_dot_d(std::string_view subdir) {
        std::vector<ConfigEntry> entries;
        const std::pair<fs::path, int> search_dirs[] = {
            {"/etc", 3}, {"/run", 2}, {"/usr/lib", 1}
        };

        for (const auto& [base, prio] : search_dirs) {
            fs::path p = base / subdir;
            if (!fs::exists(p) || !fs::is_directory(p)) continue;

            for (const auto& dir_entry : fs::directory_iterator(p)) {
                if (dir_entry.path().extension() != ".conf") continue;
                
                std::string fname = dir_entry.path().filename().string();
                auto it = std::find_if(entries.begin(), entries.end(),
                    [&fname](const ConfigEntry& e) { return e.name == fname; });
                
                if (it != entries.end()) continue; // Файл затінено вищим пріоритетом

                bool masked = dir_entry.is_symlink() && 
                              fs::read_symlink(dir_entry.path()).string().find("/dev/null") != std::string::npos;

                entries.push_back({fname, dir_entry.path(), prio, masked});
            }
        }

        std::sort(entries.begin(), entries.end(),
            [](const ConfigEntry& a, const ConfigEntry& b) { return a.name < b.name; });

        return entries;
    }

    // Застосування параметра sysctl через запис у std::ofstream
    static std::expected<void, std::string> apply_sysctl(std::string_view key, std::string_view value) {
        bool ignore_error = false;
        if (key.starts_with('-')) {
            ignore_error = true;
            key.remove_prefix(1);
        }

        std::string rel_path;
        rel_path.reserve(key.size());
        for (char ch : key) {
            rel_path.push_back(ch == '.' ? '/' : ch);
        }

        fs::path target = fs::path("/proc/sys") / rel_path;
        std::ofstream sysctl_file(target);
        if (!sysctl_file.is_open()) {
            if (ignore_error) return {};
            return std::unexpected("Помилка відкриття вузла sysctl: " + target.string());
        }

        sysctl_file << value << "\n";
        return {};
    }

    // Створення системного користувача з безпечним блокуванням бази даних
    static std::expected<void, std::string> apply_sysuser(std::string_view username, uid_t uid,
                                                         std::string_view comment,
                                                         std::string_view home,
                                                         std::string_view shell) {
        UserDbLock lock;
        if (!lock.is_locked()) {
            return std::unexpected("Не вдалося отримати lckpwdf() замок бази даних");
        }

        if (getpwnam(username.data()) != nullptr) {
            return {}; // Обліковий запис вже існує, ідемпотентний успіх
        }

        std::ofstream passwd_file("/etc/passwd", std::ios::app);
        if (!passwd_file.is_open()) {
            return std::unexpected("Не вдалося відкрити /etc/passwd для запису");
        }

        passwd_file << username << ":x:" << uid << ":" << uid << ":"
                    << comment << ":" << home << ":" << shell << "\n";

        return {};
    }
};
