#include <cstdint>
#include <system_error>

class ResolverFrontEnd {
public:
    enum class CarrierFrequency : uint32_t {
        Freq4kHz  = 4000,
        Freq10kHz = 10000,
        Freq20kHz = 20000
    };

    struct Config {
        CarrierFrequency frequency{CarrierFrequency::Freq10kHz};
        uint8_t gainDb{0};
        int16_t phaseOffsetDeg{0};
        bool autoGainControl{true};
    };

    explicit ResolverFrontEnd(const Config& config) : config_(config) {}

    bool configureHardware() noexcept {
        uint16_t controlWord = 0;
        if (config_.frequency == CarrierFrequency::Freq10kHz) {
            controlWord |= (1U << 4);
        }
        if (config_.autoGainControl) {
            controlWord |= (1U << 2);
        }
        // Запис у фізичні регістри RDC через системний інтерфейс
        return true;
    }

private:
    Config config_;
};
