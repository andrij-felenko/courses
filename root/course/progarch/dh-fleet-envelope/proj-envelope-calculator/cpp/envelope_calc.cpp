// envelope_calc.cpp - Idiomatic C++20 implementation of DH Capacity Calculator
#include <iostream>
#include <iomanip>
#include <cstdint>
#include <cmath>

struct FleetConfig {
    std::uint64_t fleet_size{200000};
    double        telemetry_interval_s{30.0};
    std::uint32_t payload_bytes{500};
    double        peak_multiplier{3.0};
    double        reconnect_window_s{60.0};
    double        reconnect_fraction{0.50};
    double        tls_resumption_rate{0.80};
};

struct CapacityReport {
    double        msg_rate_steady{0.0};
    double        msg_rate_peak{0.0};
    double        ram_sockets_gb{0.0};
    double        net_bandwidth_mbps{0.0};
    double        cpu_crypto_cores{0.0};
    double        cpu_parse_cores{0.0};
    std::uint32_t iops_raw{0};
    std::uint32_t iops_batched{0};
    double        storage_gb_per_day{0.0};

    static constexpr CapacityReport compute(const FleetConfig& cfg) noexcept {
        CapacityReport rep{};

        rep.msg_rate_steady = static_cast<double>(cfg.fleet_size) / cfg.telemetry_interval_s;
        rep.msg_rate_peak   = rep.msg_rate_steady * cfg.peak_multiplier;

        // 48 KB per session: 16K kernel rx/tx + 16K TLS + 16K app state
        constexpr double bytes_per_session = 48.0 * 1024.0;
        rep.ram_sockets_gb = (static_cast<double>(cfg.fleet_size) * bytes_per_session) / (1024.0 * 1024.0 * 1024.0);

        constexpr double frame_overhead = 107.0; // TLS/TCP/IP/Ethernet framing
        const double frame_bytes = static_cast<double>(cfg.payload_bytes) + frame_overhead;
        rep.net_bandwidth_mbps = (rep.msg_rate_peak * frame_bytes * 8.0) / 1'000'000.0;

        const double reconnect_events = static_cast<double>(cfg.fleet_size) * cfg.reconnect_fraction;
        const double handshakes_per_sec = reconnect_events / cfg.reconnect_window_s;

        constexpr double full_handshake_ms   = 0.60;
        constexpr double resume_handshake_ms = 0.05;

        const double total_handshake_ms = (handshakes_per_sec * (1.0 - cfg.tls_resumption_rate) * full_handshake_ms) +
                                           (handshakes_per_sec * cfg.tls_resumption_rate * resume_handshake_ms);
        rep.cpu_crypto_cores = total_handshake_ms / 1000.0;

        rep.cpu_parse_cores = rep.msg_rate_peak * 0.000005; // 5 microseconds per Protobuf event

        rep.iops_raw = static_cast<std::uint32_t>(rep.msg_rate_peak);
        rep.iops_batched = 10; // 100 ms flush window

        const double daily_bytes = rep.msg_rate_steady * 86400.0 * static_cast<double>(cfg.payload_bytes);
        rep.storage_gb_per_day = daily_bytes / (1024.0 * 1024.0 * 1024.0);

        return rep;
    }

    void print() const {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== DH Fleet Capacity Report (200k devices) ===\n";
        std::cout << "Steady Msg Rate:   " << msg_rate_steady << " msg/s\n";
        std::cout << "Peak Msg Rate:     " << msg_rate_peak << " msg/s\n";
        std::cout << "RAM Sockets State: " << ram_sockets_gb << " GB\n";
        std::cout << "Peak Bandwidth:    " << net_bandwidth_mbps << " Mbps\n";
        std::cout << "TLS Crypto Cores:  " << cpu_crypto_cores << " cores\n";
        std::cout << "Event Parse Cores: " << cpu_parse_cores << " cores\n";
        std::cout << "Raw Disk IOPS:     " << iops_raw << " IOPS\n";
        std::cout << "Batched Disk IOPS: " << iops_batched << " IOPS\n";
        std::cout << "Storage Growth:    " << storage_gb_per_day << " GB/day\n";
    }
};

int main() {
    constexpr FleetConfig config{};
    constexpr auto report = CapacityReport::compute(config);
    report.print();
    return 0;
}
