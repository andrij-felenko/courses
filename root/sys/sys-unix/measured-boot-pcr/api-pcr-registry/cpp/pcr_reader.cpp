// pcr_reader.cpp — Ідіоматична програма зчитування PCR мовою C++20
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <system_error>

namespace fs = std::filesystem;

enum class PcrReadError {
    InvalidIndex,
    FileNotFound,
    ReadFailure,
    InvalidFormat
};

struct PcrErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override { return "PcrReadError"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<PcrReadError>(ev)) {
            case PcrReadError::InvalidIndex: return "Недійсний індекс PCR (допустимо 0-23)";
            case PcrReadError::FileNotFound: return "Файл PCR не знайдено у sysfs";
            case PcrReadError::ReadFailure: return "Помилка читання даних з sysfs";
            case PcrReadError::InvalidFormat: return "Недійсний шістнадцятковий формат PCR";
            default: return "Невідома помилка";
        }
    }
};

inline const PcrErrorCategory g_pcr_error_category;

inline std::error_code make_error_code(PcrReadError e) {
    return {static_cast<int>(e), g_pcr_error_category};
}

class PcrSysfsReader {
public:
    explicit PcrSysfsReader(fs::path base_path = "/sys/class/tpm/tpm0/pcr-sha256")
        : base_path_(std::move(base_path)) {}

    [[nodiscard]] std::expected<std::string, std::error_code> read_pcr(uint32_t index) const {
        if (index > 23) {
            return std::unexpected(make_error_code(PcrReadError::InvalidIndex));
        }

        const fs::path pcr_path = base_path_ / std::to_string(index);
        if (!fs::exists(pcr_path)) {
            return std::unexpected(make_error_code(PcrReadError::FileNotFound));
        }

        std::ifstream file(pcr_path);
        if (!file.is_open()) {
            return std::unexpected(make_error_code(PcrReadError::ReadFailure));
        }

        std::string hex_val;
        if (!(file >> hex_val)) {
            return std::unexpected(make_error_code(PcrReadError::ReadFailure));
        }

        if (hex_val.length() != 64) {
            return std::unexpected(make_error_code(PcrReadError::InvalidFormat));
        }

        return hex_val;
    }

private:
    fs::path base_path_;
};

int main() {
    std::cout << "--- Зчитання банків PCR-SHA256 через sysfs (C++20) ---\n";
    PcrSysfsReader reader;

    for (uint32_t i = 0; i <= 7; ++i) {
        auto result = reader.read_pcr(i);
        if (result) {
            std::cout << "PCR-" << (i < 10 ? "0" : "") << i << ": " << *result << "\n";
        } else {
            std::cerr << "Помилка читання PCR-" << i << ": " << result.error().message() << "\n";
        }
    }

    return 0;
}
