// tpm2_log_parser.cpp — Ідіоматичний аналізатор TCG Event Log мовою C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <filesystem>
#include <iomanip>
#include <cstdint>
#include <expected>
#include <system_error>
#include <openssl/sha.h>

namespace fs = std::filesystem;

constexpr uint16_t ALG_SHA1   = 0x0004;
constexpr uint16_t ALG_SHA256 = 0x000B;
constexpr uint16_t ALG_SHA384 = 0x000C;

constexpr size_t SHA256_SIZE = 32;
constexpr uint32_t EV_NO_ACTION = 0x0003;

using Digest256 = std::array<uint8_t, SHA256_SIZE>;
using PcrBankArray = std::array<Digest256, 8>;

enum class LogParseError {
    FileNotFound,
    HeaderReadError,
    InvalidSpecId,
    CorruptedStream
};

struct LogErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override { return "TcgLogParser"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<LogParseError>(ev)) {
            case LogParseError::FileNotFound: return "Неможливо відкрити файл логу";
            case LogParseError::HeaderReadError: return "Помилка читання заголовка SpecID";
            case LogParseError::InvalidSpecId: return "Невідома сигнатура SpecID Event";
            case LogParseError::CorruptedStream: return "Пошкодження бінарного потоку подій";
            default: return "Невідома помилка";
        }
    }
};

inline const LogErrorCategory g_log_error_category;

inline std::error_code make_error_code(LogParseError e) {
    return {static_cast<int>(e), g_log_error_category};
}

class TpmPcrAccumulator {
public:
    TpmPcrAccumulator() {
        for (auto& pcr : pcrs_) {
            pcr.fill(0x00);
        }
    }

    void extend_sha256(uint32_t pcr_index, uint32_t event_type, std::span<const uint8_t, SHA256_SIZE> event_digest) {
        if (pcr_index >= pcrs_.size() || event_type == EV_NO_ACTION) {
            return;
        }

        std::array<uint8_t, SHA256_SIZE * 2> buffer{};
        std::copy(pcrs_[pcr_index].begin(), pcrs_[pcr_index].end(), buffer.begin());
        std::copy(event_digest.begin(), event_digest.end(), buffer.begin() + SHA256_SIZE);

        SHA256(buffer.data(), buffer.size(), pcrs_[pcr_index].data());
    }

    [[nodiscard]] const Digest256& get_pcr(size_t index) const {
        return pcrs_.at(index);
    }

    [[nodiscard]] const PcrBankArray& get_all_pcrs() const noexcept {
        return pcrs_;
    }

private:
    PcrBankArray pcrs_{};
};

class EventLogParser {
public:
    explicit EventLogParser(fs::path log_path) : log_path_(std::move(log_path)) {}

    [[nodiscard]] std::expected<PcrBankArray, std::error_code> parse_and_replay() {
        std::ifstream file(log_path_, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected(make_error_code(LogParseError::FileNotFound));
        }

        // Читання TCG 1.2 Header
        uint32_t pcr_index{}, event_type{}, event_size{};
        std::array<uint8_t, 20> header_digest{};

        if (!file.read(reinterpret_cast<char*>(&pcr_index), sizeof(pcr_index)) ||
            !file.read(reinterpret_cast<char*>(&event_type), sizeof(event_type)) ||
            !file.read(reinterpret_cast<char*>(header_digest.data()), header_digest.size()) ||
            !file.read(reinterpret_cast<char*>(&event_size), sizeof(event_size))) {
            return std::unexpected(make_error_code(LogParseError::HeaderReadError));
        }

        std::vector<uint8_t> spec_id_data(event_size);
        if (!file.read(reinterpret_cast<char*>(spec_id_data.data()), spec_id_data.size())) {
            return std::unexpected(make_error_code(LogParseError::HeaderReadError));
        }

        TpmPcrAccumulator accumulator;

        // Парсинг TCG 2.0 Agile потік
        while (file.peek() != EOF) {
            uint32_t idx{}, evt_type{}, count{};
            if (!file.read(reinterpret_cast<char*>(&idx), sizeof(idx))) break;
            if (!file.read(reinterpret_cast<char*>(&evt_type), sizeof(evt_type))) break;
            if (!file.read(reinterpret_cast<char*>(&count), sizeof(count))) break;

            for (uint32_t i = 0; i < count; ++i) {
                uint16_t alg_id{};
                if (!file.read(reinterpret_cast<char*>(&alg_id), sizeof(alg_id))) break;

                if (alg_id == ALG_SHA256) {
                    Digest256 digest{};
                    if (!file.read(reinterpret_cast<char*>(digest.data()), digest.size())) break;
                    accumulator.extend_sha256(idx, evt_type, digest);
                } else if (alg_id == ALG_SHA1) {
                    file.ignore(20);
                } else if (alg_id == ALG_SHA384) {
                    file.ignore(48);
                } else {
                    return std::unexpected(make_error_code(LogParseError::CorruptedStream));
                }
            }

            uint32_t evt_sz{};
            if (!file.read(reinterpret_cast<char*>(&evt_sz), sizeof(evt_sz))) break;
            file.ignore(evt_sz);
        }

        return accumulator.get_all_pcrs();
    }

private:
    fs::path log_path_;
};

int main(int argc, char* argv[]) {
    const fs::path path = (argc > 1) ? argv[1] : "/sys/kernel/security/tpm0/binary_bios_measurements";

    std::cout << "Аналіз TCG Event Log (C++20): " << path << std::endl;

    EventLogParser parser(path);
    auto result = parser.parse_and_replay();

    if (!result) {
        std::cerr << "Помилка розбору логу: " << result.error().message() << std::endl;
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < result->size(); ++i) {
        std::cout << "Відтворений PCR " << i << " (SHA-256): ";
        for (uint8_t byte : (*result)[i]) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        std::cout << std::dec << std::endl;
    }

    return EXIT_SUCCESS;
}
