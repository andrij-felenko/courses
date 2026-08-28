#include <iostream>
#include <filesystem>
#include <vector>
#include <string>
#include <string_view>
#include <map>
#include <algorithm>
#include <system_error>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>

namespace fs = std::filesystem;

enum class ConfigTier {
    Admin,    // /etc     (Найвищий пріоритет)
    Runtime,  // /run     (Середній пріоритет)
    Vendor    // /usr/lib (Найнижчий пріоритет)
};

struct ConfigEntry {
    std::string filename;
    fs::path full_path;
    ConfigTier tier;
    bool is_masked{false};
};

class DropinHierarchyScanner {
public:
    explicit DropinHierarchyScanner(std::string subsystem_name)
        : subsystem_(std::move(subsystem_name)) {}

    [[nodiscard]] std::vector<ConfigEntry> collect_effective_configs() {
        std::map<std::string, ConfigEntry> registry;

        // Послідовне сканування у порядку спадання пріоритету (/etc -> /run -> /usr/lib)
        scan_tier_directory("/etc/" + subsystem_ + ".d", ConfigTier::Admin, registry);
        scan_tier_directory("/run/" + subsystem_ + ".d", ConfigTier::Runtime, registry);
        scan_tier_directory("/usr/lib/" + subsystem_ + ".d", ConfigTier::Vendor, registry);

        // Перетворюємо асоціативний масив у відсортований вектор
        std::vector<ConfigEntry> result;
        result.reserve(registry.size());
        for (auto& [name, entry] : registry) {
            result.push_back(entry);
        }

        // Лексикографічне сортування за базовим іменем файлу згідно з ASCII
        std::sort(result.begin(), result.end(), [](const auto& a, const auto& b) {
            return a.filename < b.filename;
        });

        return result;
    }

private:
    std::string subsystem_;

    static bool is_masked(const fs::path& path) {
        std::error_code ec;
        if (fs::is_symlink(path, ec)) {
            auto target = fs::read_symlink(path, ec);
            if (!ec && (target == "/dev/null" || target == "dev/null")) {
                return true;
            }
        }

        struct stat st{};
        if (stat(path.c_str(), &st) == 0) {
            if (S_ISCHR(st.st_mode) && major(st.st_rdev) == 1 && minor(st.st_rdev) == 3) {
                return true;
            }
        }

        return false;
    }

    void scan_tier_directory(const fs::path& dir_path, ConfigTier tier,
                             std::map<std::string, ConfigEntry>& registry) {
        std::error_code ec;
        if (!fs::exists(dir_path, ec) || !fs::is_directory(dir_path, ec)) {
            return;
        }

        for (const auto& dir_entry : fs::directory_iterator(dir_path, ec)) {
            if (ec) break;

            const auto& path = dir_entry.path();
            if (path.filename().string().starts_with('.')) {
                continue; // Пропуск прихованих файлів і службових записів
            }

            if (path.extension() != ".conf") {
                continue; // Фільтрація файлів без суфікса .conf
            }

            std::string filename = path.filename().string();

            // Затінення: якщо запис із цим іменем уже зареєстровано з вищого рівня, пропускаємо
            if (registry.find(filename) == registry.end()) {
                registry.emplace(filename, ConfigEntry{
                    .filename = filename,
                    .full_path = path,
                    .tier = tier,
                    .is_masked = is_masked(path)
                });
            }
        }
    }
};

int main(int argc, char* argv[]) {
    std::string subsystem = (argc > 1) ? argv[1] : "sysctl";
    DropinHierarchyScanner scanner(subsystem);

    auto entries = scanner.collect_effective_configs();

    std::cout << "=== ПЛАН ЗАВАНТАЖЕННЯ КОНФІГУРАЦІЇ ДЛЯ [" << subsystem << ".d] ===\n";
    for (const auto& e : entries) {
        std::string_view tier_name = (e.tier == ConfigTier::Admin) ? "[ADMIN /etc]" :
                                     (e.tier == ConfigTier::Runtime) ? "[RUN /run]" : "[VENDOR /usr]";

        if (e.is_masked) {
            std::cout << "  [-] " << e.filename << " -> " << e.full_path
                      << " " << tier_name << " (ЗАМАСКОВАНО /dev/null)\n";
        } else {
            std::cout << "  [+] " << e.filename << " -> " << e.full_path
                      << " " << tier_name << "\n";
        }
    }

    return 0;
}
