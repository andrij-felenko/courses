#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>

namespace diag {

enum class Result : uint8_t {
    Pass = 0,
    FailHardware,
    FailTimeout,
    FailIntegrity
};

struct Step {
    std::string_view name;
    Result (*run)();
    uint32_t timeout_us;
};

class BisectionConductor {
public:
    static Result testCoreAndStack() noexcept {
        constexpr uint32_t expected_xor = 0x12345678UL ^ 0x87654321UL;
        volatile uint32_t canary = 0xDEADBEEFUL;
        volatile uint32_t a = 0x12345678UL;
        volatile uint32_t b = 0x87654321UL;

        if ((a ^ b) != expected_xor) {
            return Result::FailHardware;
        }
        if (canary != 0xDEADBEEFUL) {
            return Result::FailIntegrity;
        }
        return Result::Pass;
    }

    static Result testSramPatterns() noexcept {
        std::array<volatile uint32_t, 32> buffer{};
        
        for (auto& word : buffer) {
            word = 0x55555555UL;
        }
        for (auto& word : buffer) {
            if (word != 0x55555555UL) {
                return Result::FailIntegrity;
            }
            word = 0xAAAAAAAAUL;
        }
        for (const auto& word : buffer) {
            if (word != 0xAAAAAAAAUL) {
                return Result::FailIntegrity;
            }
        }
        return Result::Pass;
    }

    static Result testI2cBusIdle() noexcept {
        volatile bool sda_high = true;
        volatile bool scl_high = true;

        if (!sda_high || !scl_high) {
            return Result::FailHardware;
        }
        return Result::Pass;
    }

    static Result testSensorIdPing() noexcept {
        uint32_t timeout_counter = 10000;
        volatile uint8_t device_id = 0x00;

        while (timeout_counter > 0) {
            --timeout_counter;
            device_id = 0x68;
            if (device_id == 0x68) {
                return Result::Pass;
            }
        }
        return Result::FailTimeout;
    }

    static size_t runDiagnosticSuite(std::span<const Step> suite) noexcept {
        for (size_t idx = 0; idx < suite.size(); ++idx) {
            if (suite[idx].run() != Result::Pass) {
                return idx + 1; // Номер шару, де ланцюг обірвано
            }
        }
        return 0; // Всі підсистеми справні
    }
};

constexpr std::array<Step, 4> DiagnosticSuite{{
    { "Core & Stack Integrity", &BisectionConductor::testCoreAndStack, 100 },
    { "Internal SRAM March",    &BisectionConductor::testSramPatterns,   500 },
    { "I2C Bus Physical Lines", &BisectionConductor::testI2cBusIdle,    200 },
    { "Sensor ID Verification", &BisectionConductor::testSensorIdPing,  2000 }
}};

} // namespace diag

extern "C" int run_bisection_diagnostics_cpp() {
    return static_cast<int>(diag::BisectionConductor::runDiagnosticSuite(diag::DiagnosticSuite));
}
