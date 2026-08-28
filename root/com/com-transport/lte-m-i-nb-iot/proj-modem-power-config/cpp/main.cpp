#include <string>
#include <string_view>
#include <array>
#include <chrono>
#include <expected>
#include <span>
#include <format>
#include <cstdint>

namespace cellular {

using namespace std::chrono_literals;

enum class ModemError {
    Timeout,
    InvalidResponse,
    RegistrationFailed,
    InvalidParameter
};

struct PsmConfig {
    std::chrono::seconds periodic_tau{86400s}; // 24 години
    std::chrono::seconds active_time{10s};      // 10 секунд
};

class TimerEncoder {
public:
    static std::expected<std::string, ModemError> encode_t3412(std::chrono::seconds sec) noexcept {
        const auto total = sec.count();
        uint8_t unit_bits = 0;
        int64_t val = 0;

        if (total <= 62) {
            unit_bits = 0b011; // 2 с
            val = total / 2;
        } else if (total <= 31 * 60) {
            unit_bits = 0b101; // 1 хв
            val = total / 60;
        } else if (total <= 31 * 600) {
            unit_bits = 0b000; // 10 хв
            val = total / 600;
        } else if (total <= 31 * 3600) {
            unit_bits = 0b001; // 1 год
            val = total / 3600;
        } else if (total <= 31 * 36000) {
            unit_bits = 0b010; // 10 год
            val = total / 36000;
        } else if (total <= 31 * 320 * 3600) {
            unit_bits = 0b110; // 320 год
            val = total / (320 * 3600);
        } else {
            return std::unexpected(ModemError::InvalidParameter);
        }

        val = std::clamp<int64_t>(val, 1, 31);
        return format_bitmask(unit_bits, static_cast<uint8_t>(val));
    }

    static std::expected<std::string, ModemError> encode_t3324(std::chrono::seconds sec) noexcept {
        const auto total = sec.count();
        if (total == 0) {
            return std::string("11100000"); // Миттєвий перехід у PSM
        }
        uint8_t unit_bits = 0;
        int64_t val = 0;

        if (total <= 62) {
            unit_bits = 0b000; // 2 с
            val = total / 2;
        } else if (total <= 31 * 60) {
            unit_bits = 0b001; // 1 хв
            val = total / 60;
        } else if (total <= 31 * 360) {
            unit_bits = 0b010; // 6 хв
            val = total / 360;
        } else {
            return std::unexpected(ModemError::InvalidParameter);
        }

        val = std::clamp<int64_t>(val, 1, 31);
        return format_bitmask(unit_bits, static_cast<uint8_t>(val));
    }

private:
    static std::string format_bitmask(uint8_t unit, uint8_t val) {
        std::string res;
        res.reserve(8);
        for (int i = 2; i >= 0; --i) res.push_back(((unit >> i) & 1) ? '1' : '0');
        for (int i = 4; i >= 0; --i) res.push_back(((val >> i) & 1) ? '1' : '0');
        return res;
    }
};

/* Апаратний контролер низькорівневих інтерфейсів з RAII керуванням DTR */
class HardwareUartBus {
public:
    void send(std::string_view data);
    std::string receive_line(std::chrono::milliseconds timeout);
    void set_dtr(bool high);
    void sleep_ms(std::chrono::milliseconds ms);
};

/* Керівний клас стільникового модема */
class CellularModemManager {
public:
    explicit CellularModemManager(HardwareUartBus& bus) : bus_(bus) {}

    std::expected<void, ModemError> send_command(std::string_view cmd,
                                                 std::chrono::milliseconds timeout = 3000ms) {
        bus_.send(cmd);
        bus_.send("\r\n");

        auto start = std::chrono::steady_clock::now();
        while (std::chrono::steady_clock::now() - start < timeout) {
            auto line = bus_.receive_line(500ms);
            if (line.find("OK") != std::string::npos) return {};
            if (line.find("ERROR") != std::string::npos || line.find("+CME ERROR") != std::string::npos) {
                return std::unexpected(ModemError::InvalidResponse);
            }
        }
        return std::unexpected(ModemError::Timeout);
    }

    std::expected<void, ModemError> configure_psm_and_edrx(const PsmConfig& cfg) {
        auto t3412_str = TimerEncoder::encode_t3412(cfg.periodic_tau);
        auto t3324_str = TimerEncoder::encode_t3324(cfg.active_time);

        if (!t3412_str || !t3324_str) return std::unexpected(ModemError::InvalidParameter);

        auto cpsms_cmd = std::format("AT+CPSMS=1,,,\"{}\",\"{}\"", *t3412_str, *t3324_str);
        if (auto res = send_command(cpsms_cmd); !res) return res;

        // Конфігурація eDRX для NB-IoT (AcT=5, 40.96 с)
        return send_command("AT+CEDRXS=1,5,\"0010\"");
    }

    std::expected<void, ModemError> wait_registration(std::chrono::seconds timeout = 60s) {
        auto start = std::chrono::steady_clock::now();
        while (std::chrono::steady_clock::now() - start < timeout) {
            bus_.send("AT+CEREG?\r\n");
            auto line = bus_.receive_line(1000ms);
            if (line.find("+CEREG: 4,1") != std::string::npos ||
                line.find("+CEREG: 4,5") != std::string::npos ||
                line.find("+CEREG: 1") != std::string::npos ||
                line.find("+CEREG: 5") != std::string::npos) {
                return {};
            }
            bus_.sleep_ms(1000ms);
        }
        return std::unexpected(ModemError::RegistrationFailed);
    }

    std::expected<void, ModemError> send_udp(std::string_view host, uint16_t port,
                                             std::span<const uint8_t> payload) {
        auto open_cmd = std::format("AT+QIOPEN=1,0,\"UDP\",\"{}\",{},0,0", host, port);
        if (auto res = send_command(open_cmd); !res) return res;

        auto send_cmd = std::format("AT+QISEND=0,{}", payload.size());
        bus_.send(send_cmd);
        bus_.send("\r\n");
        bus_.sleep_ms(100ms);

        std::string_view payload_view(reinterpret_cast<const char*>(payload.data()), payload.size());
        bus_.send(payload_view);
        bus_.sleep_ms(200ms);

        return send_command("AT+QICLOSE=0");
    }

private:
    HardwareUartBus& bus_;
};

/* RAII-сесія роботи вузла зв'язку */
class ModemSessionScope {
public:
    explicit ModemSessionScope(HardwareUartBus& bus) : bus_(bus) {
        bus_.set_dtr(false); // Пробудження модема
        bus_.sleep_ms(50ms);
    }

    ~ModemSessionScope() {
        bus_.set_dtr(true); // Дозвіл модему перейти в PSM Deep Sleep
    }

private:
    HardwareUartBus& bus_;
};

void run_telemetry_cycle(HardwareUartBus& bus) {
    ModemSessionScope session(bus);
    CellularModemManager modem(bus);

    if (!modem.send_command("AT")) return;
    if (!modem.send_command("AT+CEREG=4")) return;

    PsmConfig psm{.periodic_tau = 86400s, .active_time = 10s};
    if (!modem.configure_psm_and_edrx(psm)) return;

    if (modem.wait_registration(60s)) {
        constexpr std::array<uint8_t, 8> payload = {0xAA, 0x01, 0x18, 0x2A, 0x0C, 0x55, 0x00, 0xFF};
        (void)modem.send_udp("198.51.100.42", 5683, payload);
    }
}

} // namespace cellular
