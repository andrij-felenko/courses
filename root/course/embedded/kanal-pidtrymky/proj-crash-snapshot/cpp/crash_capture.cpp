// crash_capture.hpp / crash_capture.cpp — ідіоматичний аварійний супервізор C++20
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

namespace diagnostic {

inline constexpr uint32_t BundleMagic   = 0x4442554E; // 'DBUN'
inline constexpr uint16_t BundleVersion = 0x0200;     // v2.0
inline constexpr uintptr_t FlashDiagAddr = 0x080E0000;

struct [[gnu::packed]] CrashHeader {
    uint32_t magic{BundleMagic};
    uint16_t version{BundleVersion};
    uint16_t header_size{sizeof(CrashHeader)};
    uint32_t payload_size{0};
    uint32_t serial_number{0};
    uint16_t hw_revision{0};
    uint16_t reset_reason{0};
    uint32_t fw_git_hash{0};
    uint64_t uptime_ms{0};
};

struct [[gnu::packed]] CpuRegisters {
    uint32_t r0{}, r1{}, r2{}, r3{}, r12{}, lr{}, pc{}, xpsr{};
    uint32_t cfsr{}, hfsr{}, mmfar{}, bfar{};
};

struct [[gnu::packed]] PowerTelemetry {
    uint16_t v_in_mv{0};
    uint16_t v_3v3_mv{0};
    int16_t  mcu_temp_c10{0};
    uint16_t reserved{0};
};

struct [[gnu::packed]] CrashSnapshot {
    CrashHeader     header;
    CpuRegisters    cpu;
    PowerTelemetry  power;
    uint32_t        crc32{0};
};

class SnapshotCollector {
public:
    static constexpr uint32_t CalculateCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (const auto byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
            }
        }
        return ~crc;
    }

    static void CaptureAndReboot(std::span<const uint32_t, 8> stack_frame) noexcept {
        auto& snap = GetStorage();

        // Заповнення регістрів ядра
        snap.cpu.r0   = stack_frame[0];
        snap.cpu.r1   = stack_frame[1];
        snap.cpu.r2   = stack_frame[2];
        snap.cpu.r3   = stack_frame[3];
        snap.cpu.r12  = stack_frame[4];
        snap.cpu.lr   = stack_frame[5];
        snap.cpu.pc   = stack_frame[6];
        snap.cpu.xpsr = stack_frame[7];

        // Читання апаратних регістрів винятків SCB
        const auto* scb_base = reinterpret_cast<const volatile uint32_t*>(0xE000ED28);
        snap.cpu.cfsr  = scb_base[0]; // 0xE000ED28
        snap.cpu.hfsr  = scb_base[1]; // 0xE000ED2C
        snap.cpu.mmfar = scb_base[3]; // 0xE000ED34
        snap.cpu.bfar  = scb_base[4]; // 0xE000ED38

        // Заповнення заголовка
        snap.header.payload_size  = sizeof(CrashSnapshot) - sizeof(CrashHeader);
        snap.header.serial_number = 20260042;
        snap.header.hw_revision   = 0x0043;
        snap.header.reset_reason  = 0x0001;
        snap.header.fw_git_hash   = 0x7F89BC20;
        snap.header.uptime_ms     = 3693600000ULL;

        snap.power.v_in_mv      = 23850;
        snap.power.v_3v3_mv     = 3290;
        snap.power.mcu_temp_c10 = 485;

        // Контрольна сума
        auto raw_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&snap),
                                                 sizeof(CrashSnapshot) - sizeof(uint32_t));
        snap.crc32 = CalculateCrc32(raw_bytes);

        // Прямий запис у Flash
        WriteToFlash(FlashDiagAddr, std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&snap), sizeof(CrashSnapshot)));

        // Перезавантаження системи
        TriggerSystemReset();
    }

private:
    static CrashSnapshot& GetStorage() noexcept {
        [[gnu::section(".noinit")]] static CrashSnapshot s_instance;
        return s_instance;
    }

    static void WriteToFlash(uintptr_t dest, std::span<const uint8_t> src) noexcept {
        auto* flash_words = reinterpret_cast<volatile uint32_t*>(dest);
        const auto* src_words = reinterpret_cast<const uint32_t*>(src.data());
        const size_t word_count = (src.size() + 3) / 4;

        for (size_t i = 0; i < word_count; ++i) {
            flash_words[i] = src_words[i];
        }
    }

    [[noreturn]] static void TriggerSystemReset() noexcept {
        auto* aircr = reinterpret_cast<volatile uint32_t*>(0xE000ED0C);
        *aircr = (0x5FA << 16) | (1 << 2);
        while (true) {
            asm volatile("nop");
        }
    }
};

} // namespace diagnostic

extern "C" void HardFault_Handler_C(uint32_t* hardfault_args) {
    auto frame_span = std::span<const uint32_t, 8>(hardfault_args, 8);
    diagnostic::SnapshotCollector::CaptureAndReboot(frame_span);
}
