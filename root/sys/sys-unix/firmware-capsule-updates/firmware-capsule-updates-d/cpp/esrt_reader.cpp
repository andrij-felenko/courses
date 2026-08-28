// esrt_reader.cpp — Ідіоматичний C++20 варіант парсера ESRT
#include <iostream>
#include <fstream>
#include <filesystem>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <format>

namespace fs = std::filesystem;

struct EsrtEntry {
    std::string fw_class;
    uint32_t fw_version{0};
    uint32_t last_attempt_version{0};
    uint32_t last_attempt_status{0};

    [[nodiscard]] std::string_view status_description() const noexcept {
        switch (last_attempt_status) {
            case 0: return "Успішно (Success)";
            case 1: return "Помилка (Unsuccessful)";
            case 2: return "Недостатньо ресурсів (Insufficient Resources)";
            case 3: return "Некоректна версія / Anti-Rollback (Incorrect Version)";
            case 4: return "Невірний формат капсули (Invalid Format)";
            case 5: return "Помилка автентифікації підпису (Auth Error)";
            case 6: return "Відсутнє живлення від мережі AC (Power Event)";
            default: return "Невідомий код помилки";
        }
    }
};

class EsrtScanner {
    static constexpr std::string_view kEsrtSysfsPath = "/sys/firmware/efi/esrt/entries";

    static std::optional<std::string> read_file_string(const fs::path& path) {
        if (!fs::exists(path)) return std::nullopt;
        std::ifstream file(path);
        if (!file.is_open()) return std::nullopt;
        std::string line;
        if (std::getline(file, line)) {
            return line;
        }
        return std::nullopt;
    }

    static uint32_t read_file_uint(const fs::path& path) {
        auto str = read_file_string(path);
        if (!str) return 0;
        try {
            return static_cast<uint32_t>(std::stoul(*str, nullptr, 0));
        } catch (...) {
            return 0;
        }
    }

public:
    [[nodiscard]] static std::vector<EsrtEntry> scan() {
        std::vector<EsrtEntry> result;
        const fs::path base_path{kEsrtSysfsPath};

        if (!fs::exists(base_path) || !fs::is_directory(base_path)) {
            return result;
        }

        for (const auto& entry : fs::directory_iterator(base_path)) {
            if (!entry.is_directory()) continue;

            const auto p = entry.path();
            EsrtEntry item;
            item.fw_class = read_file_string(p / "fw_class").value_or("N/A");
            item.fw_version = read_file_uint(p / "fw_version");
            item.last_attempt_version = read_file_uint(p / "last_attempt_version");
            item.last_attempt_status = read_file_uint(p / "last_attempt_status");

            result.push_back(std::move(item));
        }
        return result;
    }
};

int main() {
    const auto entries = EsrtScanner::scan();

    if (entries.empty()) {
        std::cerr << "Записи ESRT не знайдено (перевірте наявність UEFI системи та монтирування sysfs).\n";
        return 1;
    }

    std::cout << std::format("{:<38} | {:<10} | {:<10} | {}\n", 
                             "GUID пристрою (FwClass)", "Версія", "Остання", "Статус останньої спроби");
    std::cout << std::string(104, '-') << '\n';

    for (const auto& entry : entries) {
        std::cout << std::format("{:<38} | {:#010x} | {:#010x} | {}\n",
                                 entry.fw_class, entry.fw_version,
                                 entry.last_attempt_version, entry.status_description());
    }

    return 0;
}
