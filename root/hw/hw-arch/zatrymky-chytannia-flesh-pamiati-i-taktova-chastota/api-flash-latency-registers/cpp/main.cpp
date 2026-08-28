#include <cstdint>
#include <span>

namespace mcu::flash {

enum class Latency : uint32_t {
    Ws0 = 0,
    Ws1 = 1,
    Ws2 = 2,
    Ws3 = 3,
    Ws4 = 4,
    Ws5 = 5,
    Ws6 = 6,
    Ws7 = 7
};

enum class VoltageRange {
    High_2V7_3V6,
    Medium_2V4_2V7,
    Low_2V1_2V4,
    VeryLow_1V8_2V1
};

struct FlashRegisters {
    volatile uint32_t ACR;
    volatile uint32_t KEYR;
    volatile uint32_t OPTKEYR;
    volatile uint32_t SR;
    volatile uint32_t CR;
    volatile uint32_t OPTCR;
};

class FlashController {
private:
    static constexpr uintptr_t BaseAddress = 0x40023C00U;
    static constexpr uint32_t LatencyMask = 0x0FU;
    static constexpr uint32_t PrftenBit   = 1U << 8;
    static constexpr uint32_t IcenBit     = 1U << 9;
    static constexpr uint32_t DcenBit     = 1U << 10;
    static constexpr uint32_t IcrstBit    = 1U << 11;
    static constexpr uint32_t DcrstBit    = 1U << 12;

    static auto& regs() noexcept {
        return *reinterpret_cast<FlashRegisters*>(BaseAddress);
    }

public:
    /* Обчислення мінімальної затримки під час компіляції */
    static constexpr Latency calculate_latency(uint32_t hclk_hz, VoltageRange vrange) noexcept {
        switch (vrange) {
            case VoltageRange::High_2V7_3V6:
                if (hclk_hz <= 30'000'000U)  return Latency::Ws0;
                if (hclk_hz <= 60'000'000U)  return Latency::Ws1;
                if (hclk_hz <= 90'000'000U)  return Latency::Ws2;
                if (hclk_hz <= 120'000'000U) return Latency::Ws3;
                if (hclk_hz <= 150'000'000U) return Latency::Ws4;
                if (hclk_hz <= 168'000'000U) return Latency::Ws5;
                if (hclk_hz <= 180'000'000U) return Latency::Ws6;
                return Latency::Ws7;

            case VoltageRange::Medium_2V4_2V7:
                if (hclk_hz <= 24'000'000U)  return Latency::Ws0;
                if (hclk_hz <= 48'000'000U)  return Latency::Ws1;
                if (hclk_hz <= 72'000'000U)  return Latency::Ws2;
                if (hclk_hz <= 96'000'000U)  return Latency::Ws3;
                if (hclk_hz <= 120'000'000U) return Latency::Ws4;
                if (hclk_hz <= 144'000'000U) return Latency::Ws5;
                return Latency::Ws6;

            case VoltageRange::Low_2V1_2V4:
                if (hclk_hz <= 18'000'000U)  return Latency::Ws0;
                if (hclk_hz <= 36'000'000U)  return Latency::Ws1;
                if (hclk_hz <= 54'000'000U)  return Latency::Ws2;
                if (hclk_hz <= 72'000'000U)  return Latency::Ws3;
                if (hclk_hz <= 90'000'000U)  return Latency::Ws4;
                if (hclk_hz <= 108'000'000U) return Latency::Ws5;
                return Latency::Ws6;

            case VoltageRange::VeryLow_1V8_2V1:
                if (hclk_hz <= 16'000'000U)  return Latency::Ws0;
                if (hclk_hz <= 32'000'000U)  return Latency::Ws1;
                if (hclk_hz <= 48'000'000U)  return Latency::Ws2;
                if (hclk_hz <= 64'000'000U)  return Latency::Ws3;
                if (hclk_hz <= 80'000'000U)  return Latency::Ws4;
                if (hclk_hz <= 96'000'000U)  return Latency::Ws5;
                if (hclk_hz <= 112'000'000U) return Latency::Ws6;
                return Latency::Ws7;
        }
        return Latency::Ws7;
    }

    static bool set_latency(Latency lat) noexcept {
        auto val = regs().ACR;
        val &= ~LatencyMask;
        val |= static_cast<uint32_t>(lat);
        regs().ACR = val;

        uint32_t timeout = 1000U;
        while ((regs().ACR & LatencyMask) != static_cast<uint32_t>(lat)) {
            if (--timeout == 0U) return false;
        }
        return true;
    }

    static void configure_accelerator(bool prefetch, bool icache, bool dcache) noexcept {
        auto val = regs().ACR;
        if (prefetch) val |= PrftenBit; else val &= ~PrftenBit;
        if (icache)   val |= IcenBit;   else val &= ~IcenBit;
        if (dcache)   val |= DcenBit;   else val &= ~DcenBit;
        regs().ACR = val;
    }

    /* Безпечне скидання та інвалідація кешів */
    static void flush_caches() noexcept {
        regs().ACR &= ~(IcenBit | DcenBit);
        regs().ACR |= (IcrstBit | DcrstBit);
        regs().ACR &= ~(IcrstBit | DcrstBit);
        regs().ACR |= (IcenBit | DcenBit);
    }
};

} // namespace mcu::flash
