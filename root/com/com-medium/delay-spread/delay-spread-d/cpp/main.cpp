#include <iostream>
#include <string_view>

struct ChannelAnalysis {
    double bc_50_khz{0.0};
    double t_symbol_us{0.0};
    bool has_isi_risk{false};
};

[[nodiscard]] constexpr ChannelAnalysis analyze_channel(double rms_delay_spread_ns, double symbol_rate_ksps) noexcept {
    const double sigma_sec = rms_delay_spread_ns * 1e-9;
    const double bc_50_khz = (1.0 / (5.0 * sigma_sec)) / 1000.0;
    const double t_symbol_us = 1000.0 / symbol_rate_ksps;
    const double rms_us = rms_delay_spread_ns / 1000.0;
    
    return ChannelAnalysis{
        .bc_50_khz = bc_50_khz,
        .t_symbol_us = t_symbol_us,
        .has_isi_risk = (t_symbol_us < 10.0 * rms_us)
    };
}

int main() {
    auto print_analysis = [](std::string_view name, double rms_ns, double ksps) {
        const auto res = analyze_channel(rms_ns, ksps);
        std::cout << "--- " << name << " ---\n"
                  << "RMS Delay Spread: " << rms_ns << " нс\n"
                  << "Смуга когерентності B_c (50%): " << res.bc_50_khz << " кГц\n"
                  << "Період символу T_s: " << res.t_symbol_us << " мкс\n"
                  << "Статус ISI: " << (res.has_isi_risk ? "НЕБЕЗПЕКА (потрібен еквалайзер/OFDM)" : "БЕЗПЕЧНО") << "\n\n";
    };

    print_analysis("Кімнатний Wi-Fi канал", 40.0, 1000.0);
    print_analysis("Міський стільниковий канал", 1500.0, 1000.0);
    return 0;
}
