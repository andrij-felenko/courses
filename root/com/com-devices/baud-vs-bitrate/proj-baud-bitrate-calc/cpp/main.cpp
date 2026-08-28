#include <iostream>
#include <string_view>
#include <vector>
#include <cmath>
#include <expected>
#include <format>
#include <iomanip>

enum class LinkError {
    InvalidSymbolRate,
    InvalidModulation,
    ZeroLanes,
    InvalidRatio,
    ZeroPayload
};

/* Конфігурація лінії зв'язку */
struct LinkConfig {
    std::string_view name;
    double symbol_rate_baud;
    uint32_t modulation_states_m;
    uint32_t num_lanes{1};
    uint32_t line_code_k{1};
    uint32_t line_code_n{1};
    uint32_t fec_k{1};
    uint32_t fec_n{1};
    uint32_t payload_bytes{1500};
    uint32_t header_bytes{0};
    uint32_t overhead_bytes{0};
    double analog_bandwidth_hz{0.0};
};

/* Результати детального аналізу каналу */
struct LinkMetrics {
    double bits_per_symbol{0.0};
    double raw_bitrate_bps{0.0};
    double gross_bitrate_bps{0.0};
    double net_bitrate_bps{0.0};
    double goodput_bps{0.0};
    double protocol_efficiency{0.0};
    double spectral_efficiency{0.0};
};

class LinkCapacityCalculator {
public:
    [[nodiscard]] static std::expected<LinkMetrics, LinkError>
    calculate(const LinkConfig& cfg) noexcept {
        if (cfg.symbol_rate_baud <= 0.0) {
            return std::unexpected(LinkError::InvalidSymbolRate);
        }
        if (cfg.modulation_states_m < 2) {
            return std::unexpected(LinkError::InvalidModulation);
        }
        if (cfg.num_lanes == 0) {
            return std::unexpected(LinkError::ZeroLanes);
        }
        if (cfg.line_code_n == 0 || cfg.fec_n == 0) {
            return std::unexpected(LinkError::InvalidRatio);
        }

        uint32_t total_bytes = cfg.payload_bytes + cfg.header_bytes + cfg.overhead_bytes;
        if (total_bytes == 0 || cfg.payload_bytes == 0) {
            return std::unexpected(LinkError::ZeroPayload);
        }

        LinkMetrics m;
        m.bits_per_symbol = std::log2(static_cast<double>(cfg.modulation_states_m));
        m.raw_bitrate_bps = cfg.symbol_rate_baud * m.bits_per_symbol * cfg.num_lanes;

        const double line_ratio = static_cast<double>(cfg.line_code_k) / cfg.line_code_n;
        m.gross_bitrate_bps = m.raw_bitrate_bps * line_ratio;

        const double fec_ratio = static_cast<double>(cfg.fec_k) / cfg.fec_n;
        m.net_bitrate_bps = m.gross_bitrate_bps * fec_ratio;

        const double packet_efficiency = static_cast<double>(cfg.payload_bytes) / total_bytes;
        m.goodput_bps = m.net_bitrate_bps * packet_efficiency;
        m.protocol_efficiency = (m.goodput_bps / m.raw_bitrate_bps) * 100.0;

        if (cfg.analog_bandwidth_hz > 0.0) {
            m.spectral_efficiency = m.goodput_bps / cfg.analog_bandwidth_hz;
        }

        return m;
    }

    static void print_report(const LinkConfig& cfg, const LinkMetrics& m) {
        std::cout << std::string(66, '=') << '\n';
        std::cout << " ЗВІТ ШВИДКОСТЕЙ КАНАЛУ: " << cfg.name << '\n';
        std::cout << std::string(66, '=') << '\n';
        std::cout << std::fixed << std::setprecision(2);
        std::cout << " Бодова швидкість (на лінію) : " << std::setw(12) << cfg.symbol_rate_baud
                  << " бод (" << (cfg.symbol_rate_baud / 1e6) << " Мбод)\n";
        std::cout << " Модуляція (M станів)        : " << std::setw(12) << cfg.modulation_states_m
                  << " (k = " << m.bits_per_symbol << " біт/символ)\n";
        std::cout << " Кількість ліній / потоків   : " << std::setw(12) << cfg.num_lanes << '\n';
        std::cout << std::string(66, '-') << '\n';
        std::cout << " 1. Сирий бітрейт (Raw Rate) : " << std::setw(12) << (m.raw_bitrate_bps / 1e6)
                  << " Мбіт/с (" << (m.raw_bitrate_bps / 8e6) << " Мбайт/с)\n";
        std::cout << " 2. Брутто бітрейт (Gross)   : " << std::setw(12) << (m.gross_bitrate_bps / 1e6)
                  << " Мбіт/с (код " << cfg.line_code_k << "/" << cfg.line_code_n << ")\n";
        std::cout << " 3. Нетто бітрейт (Net FEC)  : " << std::setw(12) << (m.net_bitrate_bps / 1e6)
                  << " Мбіт/с (FEC " << cfg.fec_k << "/" << cfg.fec_n << ")\n";
        std::cout << " 4. Корисний Goodput         : " << std::setw(12) << (m.goodput_bps / 1e6)
                  << " Мбіт/с (" << (m.goodput_bps / 8e6) << " Мбайт/с)\n";
        std::cout << std::string(66, '-') << '\n';
        std::cout << " Підсумковий ККД лінії       : " << std::setw(11) << m.protocol_efficiency << " %\n";
        if (m.spectral_efficiency > 0.0) {
            std::cout << " Спектральна ефективність    : " << std::setw(11) << m.spectral_efficiency
                      << " біт/с/Гц\n";
        }
        std::cout << std::string(66, '=') << "\n\n";
    }
};

int main() {
    const std::vector<LinkConfig> configs = {
        LinkConfig{
            .name = "UART RS-232 (115200 8N1)",
            .symbol_rate_baud = 115200.0,
            .modulation_states_m = 2,
            .num_lanes = 1,
            .line_code_k = 1, .line_code_n = 1,
            .fec_k = 1, .fec_n = 1,
            .payload_bytes = 8,
            .header_bytes = 1,
            .overhead_bytes = 1,
            .analog_bandwidth_hz = 57600.0
        },
        LinkConfig{
            .name = "Ethernet 1000BASE-T (Cat5e, MTU 1500)",
            .symbol_rate_baud = 125000000.0,
            .modulation_states_m = 4,
            .num_lanes = 4,
            .line_code_k = 1, .line_code_n = 1,
            .fec_k = 1, .fec_n = 1,
            .payload_bytes = 1500,
            .header_bytes = 14 + 20 + 20,
            .overhead_bytes = 8 + 4 + 12,
            .analog_bandwidth_hz = 62500000.0 * 4.0
        },
        LinkConfig{
            .name = "PCIe 6.0 x4 (32 Гбод PAM-4 FLIT)",
            .symbol_rate_baud = 32000000000.0,
            .modulation_states_m = 4,
            .num_lanes = 4,
            .line_code_k = 1, .line_code_n = 1,
            .fec_k = 242, .fec_n = 256,
            .payload_bytes = 216,
            .header_bytes = 16,
            .overhead_bytes = 10,
            .analog_bandwidth_hz = 16000000000.0 * 4.0
        },
        LinkConfig{
            .name = "Wi-Fi 6 (802.11ax, 80 МГц, 1024-QAM, 1 SS)",
            .symbol_rate_baud = 72058823.5,
            .modulation_states_m = 1024,
            .num_lanes = 1,
            .line_code_k = 1, .line_code_n = 1,
            .fec_k = 5, .fec_n = 6,
            .payload_bytes = 1460,
            .header_bytes = 24 + 20 + 20,
            .overhead_bytes = 4 + 40,
            .analog_bandwidth_hz = 80000000.0
        }
    };

    for (const auto& cfg : configs) {
        auto result = LinkCapacityCalculator::calculate(cfg);
        if (result) {
            LinkCapacityCalculator::print_report(cfg, *result);
        } else {
            std::cerr << "Помилка розрахунку для " << cfg.name << '\n';
        }
    }

    return 0;
}
