#include <cstdint>
#include <optional>
#include <array>
#include <string_view>

namespace hal::i2c {

enum class SpeedMode : uint8_t {
    Standard = 0, // 100 kHz
    Fast     = 1, // 400 kHz
    FastPlus = 2  // 1 MHz
};

struct BusParameters {
    uint32_t pclkHz{48'000'000};       // Тактова частота модуля
    uint32_t targetSclHz{400'000};     // Цільова частота
    uint32_t riseTimeNs{200};          // Фактичний час наростання tr
    uint32_t fallTimeNs{40};           // Фактичний час спадання tf
    uint8_t  dnfCycles{0};             // Цифровий фільтр (0..15)
    bool     analogFilter{true};       // Аналоговий фільтр (50 нс)
};

struct TimingRegisters {
    uint8_t  prescaler{0};
    uint8_t  sclLow{0};
    uint8_t  sclHigh{0};
    uint8_t  sdaDelay{0};
    uint8_t  sclDelay{0};
    uint32_t packedRegister{0};
    uint32_t actualFrequencyHz{0};

    [[nodiscard]] constexpr uint32_t raw() const noexcept {
        return packedRegister;
    }
};

struct ModeSpecification {
    uint32_t tLowMinNs;
    uint32_t tHighMinNs;
    uint32_t tSuDatMinNs;
    uint32_t tHdDatMaxNs;
    uint32_t tRiseMaxNs;
    uint32_t tFallMaxNs;
};

inline constexpr std::array<ModeSpecification, 3> Specs{{
    {4700, 4000, 250, 3450, 1000, 300}, // Standard
    {1300,  600, 100,  900,  300, 300}, // Fast
    { 500,  260,  50,  450,  120, 120}  // FastPlus
}};

class TimingCalculator {
public:
    [[nodiscard]] static std::optional<TimingRegisters> compute(
        const BusParameters& params,
        SpeedMode mode) noexcept
    {
        if (params.pclkHz == 0 || params.targetSclHz == 0) {
            return std::nullopt;
        }

        const auto& spec = Specs[static_cast<size_t>(mode)];
        const uint32_t tAfNs = params.analogFilter ? 50 : 0;
        const uint32_t tr = params.riseTimeNs > 0 ? params.riseTimeNs : spec.tRiseMaxNs;
        const uint32_t tf = params.fallTimeNs > 0 ? params.fallTimeNs : spec.tFallMaxNs;

        const double tPclkNs = 1e9 / static_cast<double>(params.pclkHz);
        const uint32_t targetPeriodNs = 1'000'000'000U / params.targetSclHz;

        for (uint32_t presc = 0; presc <= 15; ++presc) {
            const double tPrescNs = static_cast<double>(presc + 1) * tPclkNs;
            const double tFilterNs = static_cast<double>(tAfNs) + 
                                     (static_cast<double>(params.dnfCycles) * tPclkNs);

            const double scllMin = (spec.tLowMinNs + tf - tFilterNs) / tPrescNs - 1.0;
            const double sclhMin = (spec.tHighMinNs + tr - tFilterNs) / tPrescNs - 1.0;

            uint32_t scllVal = scllMin > 0.0 ? static_cast<uint32_t>(scllMin + 0.999) : 0;
            uint32_t sclhVal = sclhMin > 0.0 ? static_cast<uint32_t>(sclhMin + 0.999) : 0;

            const double currentPeriodNs = (static_cast<double>(scllVal + 1) + 
                                            static_cast<double>(sclhVal + 1)) * tPrescNs + tr + tf;

            if (currentPeriodNs < static_cast<double>(targetPeriodNs)) {
                const double extraNs = static_cast<double>(targetPeriodNs) - currentPeriodNs;
                const uint32_t extraTicks = static_cast<uint32_t>(extraNs / tPrescNs);
                scllVal += (extraTicks + 1) / 2;
                sclhVal += extraTicks / 2;
            }

            if (scllVal > 255 || sclhVal > 255) {
                continue;
            }

            const double scldelMin = (spec.tSuDatMinNs + tr - tFilterNs) / tPrescNs - 1.0;
            const double sdadelMin = (tf - tFilterNs) / tPrescNs - 1.0;

            const uint32_t scldelVal = scldelMin > 0.0 ? static_cast<uint32_t>(scldelMin + 0.999) : 0;
            const uint32_t sdadelVal = sdadelMin > 0.0 ? static_cast<uint32_t>(sdadelMin + 0.999) : 0;

            if (scldelVal > 15 || sdadelVal > 15) {
                continue;
            }

            TimingRegisters reg{};
            reg.prescaler = static_cast<uint8_t>(presc);
            reg.sclLow    = static_cast<uint8_t>(scllVal);
            reg.sclHigh   = static_cast<uint8_t>(sclhVal);
            reg.sdaDelay  = static_cast<uint8_t>(sdadelVal);
            reg.sclDelay  = static_cast<uint8_t>(scldelVal);

            reg.packedRegister = (static_cast<uint32_t>(reg.prescaler) << 28) |
                                 (static_cast<uint32_t>(reg.sclDelay)  << 20) |
                                 (static_cast<uint32_t>(reg.sdaDelay)  << 16) |
                                 (static_cast<uint32_t>(reg.sclHigh)   << 8)  |
                                 (static_cast<uint32_t>(reg.sclLow)    << 0);

            const double actualPeriod = (static_cast<double>(reg.sclLow + 1) + 
                                         static_cast<double>(reg.sclHigh + 1)) * tPrescNs + tr + tf;
            reg.actualFrequencyHz = static_cast<uint32_t>(1e9 / actualPeriod);

            return reg;
        }

        return std::nullopt;
    }
};

} // namespace hal::i2c
