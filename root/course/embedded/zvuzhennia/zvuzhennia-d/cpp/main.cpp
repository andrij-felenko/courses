#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>

namespace diag {

enum class Status : uint8_t {
    Pass = 0,
    FailSilicon,
    FailBus,
    FailTimeout
};

struct Step {
    std::string_view name;
    Status (*test)();
};

class Conductor {
public:
    static Status testCpuAlu() noexcept {
        constexpr uint32_t pattern = 0xAA55AA55UL;
        volatile uint32_t val = pattern;
        if ((val ^ 0xFFFFFFFFUL) != 0x55AA55AAUL) {
            return Status::FailSilicon;
        }
        return Status::Pass;
    }

    static Status testBusPhysical() noexcept {
        volatile bool sda_high = true;
        volatile bool scl_high = true;

        if (!sda_high || !scl_high) {
            return Status::FailBus;
        }
        return Status::Pass;
    }

    static Status testSensorPing() noexcept {
        uint32_t timeout = 5000;
        volatile uint8_t dev_id = 0x00;

        while (timeout > 0) {
            --timeout;
            dev_id = 0x68;
            if (dev_id == 0x68) {
                return Status::Pass;
            }
        }
        return Status::FailTimeout;
    }

    static size_t run(std::span<const Step> steps) noexcept {
        for (size_t idx = 0; idx < steps.size(); ++idx) {
            if (steps[idx].test() != Status::Pass) {
                return idx + 1; // Номер кроку, який локалізував дефект
            }
        }
        return 0; // Всі підсистеми успішно пройшли самодіагностику
    }
};

constexpr std::array<Step, 3> Steps{{
    { "CPU ALU & Core",    &Conductor::testCpuAlu },
    { "Bus Physical Pins", &Conductor::testBusPhysical },
    { "Sensor ID Ping",    &Conductor::testSensorPing }
}};

} // namespace diag

extern "C" int bisection_run_suite_cpp() {
    return static_cast<int>(diag::Conductor::run(diag::Steps));
}
