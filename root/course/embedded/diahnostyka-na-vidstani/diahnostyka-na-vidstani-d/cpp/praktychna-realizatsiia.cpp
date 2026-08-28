#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <string_view>
#include <optional>
#include <format>

namespace Diag {

constexpr uint32_t CrashMagicFlag = 0xDEADBEEFU;
constexpr size_t StackDumpWordsCount = 32;

struct alignas(4) CrashRecord {
    uint32_t magic{0};
    uint32_t uptime_sec{0};
    uint32_t reset_flags{0};
    
    uint32_t r0{0}, r1{0}, r2{0}, r3{0};
    uint32_t r12{0}, lr{0}, pc{0}, xpsr{0};
    
    uint32_t hfsr{0};
    uint32_t cfsr{0};
    uint32_t mmfar{0};
    uint32_t bfar{0};
    
    uint32_t stack_len{0};
    std::array<uint32_t, StackDumpWordsCount> stack_words{};
    
    uint32_t checksum{0};
};

// Розміщення у виділеній секції .noinit
__attribute__((section(".noinit"))) static volatile CrashRecord g_raw_record;

class CrashReportManager {
public:
    static constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1)));
            }
        }
        return ~crc;
    }

    static std::optional<CrashRecord> fetch_and_clear_report() noexcept {
        if (g_raw_record.magic != CrashMagicFlag) {
            return std::nullopt;
        }

        auto raw_bytes = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&g_raw_record),
            sizeof(CrashRecord) - sizeof(uint32_t)
        );

        if (calculate_crc32(raw_bytes) != g_raw_record.checksum) {
            g_raw_record.magic = 0;
            return std::nullopt;
        }

        CrashRecord result{};
        // Копіювання з volatile пам'яті
        const uint8_t* src = reinterpret_cast<const uint8_t*>(&g_raw_record);
        uint8_t* dst = reinterpret_cast<uint8_t*>(&result);
        for (size_t i = 0; i < sizeof(CrashRecord); ++i) {
            dst[i] = src[i];
        }

        g_raw_record.magic = 0; // Позначаємо як прочитано
        return result;
    }

    static bool serialize_json(const CrashRecord& rec, std::span<char> out_buf) noexcept {
        // Формування компактного JSON без динамічного виділення пам'яті
        const char* fmt = 
            "{{\"type\":\"crash\",\"uptime\":{},\"pc\":\"0x{:08X}\",\"lr\":\"0x{:08X}\","
            "\"cfsr\":\"0x{:08X}\",\"hfsr\":\"0x{:08X}\",\"bfar\":\"0x{:08X}\",\"mmfar\":\"0x{:08X}\"}}";
        
        auto res = std::format_to_n(out_buf.data(), out_buf.size() - 1, fmt,
                                    rec.uptime_sec, rec.pc, rec.lr,
                                    rec.cfsr, rec.hfsr, rec.bfar, rec.mmfar);
        if (res.size >= out_buf.size() - 1) {
            return false;
        }
        out_buf[res.size] = '\0';
        return true;
    }
};

} // namespace Diag
