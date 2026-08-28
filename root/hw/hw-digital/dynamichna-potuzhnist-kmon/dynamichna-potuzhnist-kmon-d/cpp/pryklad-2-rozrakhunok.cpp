#include <cstdint>
#include <cstddef>
#include <bit>
#include <span>
#include <vector>

struct BusPhysicalConfig {
    double cap_per_line_pf{8.0}; // 8 пФ
    double vdd{1.2};             // 1.2 В
    double freq_hz{400.0e6};     // 400 МГц
    size_t data_lanes{32};
};

struct BusEnergyBudget {
    double raw_power_mw{0.0};
    double encoded_power_mw{0.0};
    double power_reduction_pct{0.0};
    double raw_activity{0.0};
    double encoded_activity{0.0};
};

class BusPowerAnalyzer {
public:
    explicit BusPowerAnalyzer(BusPhysicalConfig cfg) noexcept : cfg_{cfg} {}

    [[nodiscard]] BusEnergyBudget evaluate_stream(std::span<const uint32_t> stream) const noexcept {
        if (stream.size() < 2) return {};

        uint64_t raw_transitions = 0;
        uint64_t enc_transitions = 0;

        uint32_t prev_raw = stream.front();
        uint32_t prev_bus = stream.front();
        uint8_t prev_inv = 0;

        for (size_t i = 1; i < stream.size(); ++i) {
            const uint32_t current = stream[i];

            // Сирий розрахунок
            raw_transitions += std::popcount(current ^ prev_raw);
            prev_raw = current;

            // Закодований розрахунок (побайтний Bus Invert)
            uint8_t cur_inv_flags = 0;
            for (size_t b = 0; b < 4; ++b) {
                const auto cur_byte = static_cast<uint8_t>((current >> (b * 8)) & 0xFF);
                const auto prev_byte = static_cast<uint8_t>((prev_bus >> (b * 8)) & 0xFF);
                const auto h = static_cast<size_t>(std::popcount(static_cast<uint8_t>(cur_byte ^ prev_byte)));

                uint8_t bus_out_byte = cur_byte;
                if (h > 4) {
                    bus_out_byte = static_cast<uint8_t>(~cur_byte);
                    cur_inv_flags |= static_cast<uint8_t>(1 << b);
                }

                enc_transitions += std::popcount(static_cast<uint8_t>(bus_out_byte ^ prev_byte));
                prev_bus = (prev_bus & ~(0xFF << (b * 8))) | (static_cast<uint32_t>(bus_out_byte) << (b * 8));
            }

            enc_transitions += std::popcount(static_cast<uint8_t>(cur_inv_flags ^ prev_inv));
            prev_inv = cur_inv_flags;
        }

        const auto cycles = static_cast<double>(stream.size() - 1);
        const double trans_energy = 0.5 * (cfg_.cap_per_line_pf * 1e-12) * (cfg_.vdd * cfg_.vdd);

        BusEnergyBudget budget{};
        budget.raw_activity = static_cast<double>(raw_transitions) / (cycles * static_cast<double>(cfg_.data_lanes));
        budget.encoded_activity = static_cast<double>(enc_transitions) / (cycles * static_cast<double>(cfg_.data_lanes + 4));

        budget.raw_power_mw = (static_cast<double>(raw_transitions) / cycles) * trans_energy * cfg_.freq_hz * 1e3;
        budget.encoded_power_mw = (static_cast<double>(enc_transitions) / cycles) * trans_energy * cfg_.freq_hz * 1e3;
        budget.power_reduction_pct = (1.0 - budget.encoded_power_mw / budget.raw_power_mw) * 100.0;

        return budget;
    }

private:
    BusPhysicalConfig cfg_;
};
