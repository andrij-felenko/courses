# envelope_calc.py - Python implementation of DH Capacity Calculator
from dataclasses import dataclass

@dataclass
class FleetConfig:
    fleet_size: int = 200_000
    telemetry_interval_s: float = 30.0
    payload_bytes: int = 500
    peak_multiplier: float = 3.0
    reconnect_window_s: float = 60.0
    reconnect_fraction: float = 0.50
    tls_resumption_rate: float = 0.80

def calculate_capacity(cfg: FleetConfig) -> dict:
    steady_rate = cfg.fleet_size / cfg.telemetry_interval_s
    peak_rate = steady_rate * cfg.peak_multiplier

    # RAM: 48 KB per session
    ram_gb = (cfg.fleet_size * 48 * 1024) / (1024 ** 3)

    # Net bandwidth
    frame_bytes = cfg.payload_bytes + 107
    net_mbps = (peak_rate * frame_bytes * 8) / 1e6

    # TLS crypto CPU
    reconnect_hps = (cfg.fleet_size * cfg.reconnect_fraction) / cfg.reconnect_window_s
    crypto_ms = (reconnect_hps * (1 - cfg.tls_resumption_rate) * 0.60) + \
                (reconnect_hps * cfg.tls_resumption_rate * 0.05)
    crypto_cores = crypto_ms / 1000.0

    parse_cores = peak_rate * 0.000005
    storage_gb_day = (steady_rate * 86400 * cfg.payload_bytes) / (1024 ** 3)

    return {
        "msg_rate_steady": steady_rate,
        "msg_rate_peak": peak_rate,
        "ram_sockets_gb": ram_gb,
        "net_bandwidth_mbps": net_mbps,
        "cpu_crypto_cores": crypto_cores,
        "cpu_parse_cores": parse_cores,
        "iops_raw": int(peak_rate),
        "iops_batched": 10,
        "storage_gb_per_day": storage_gb_day
    }

if __name__ == "__main__":
    rep = calculate_capacity(FleetConfig())
    print("=== DH Fleet Capacity Report (200k devices) ===")
    for k, v in rep.items():
        print(f"{k:20s}: {v:.2f}")
