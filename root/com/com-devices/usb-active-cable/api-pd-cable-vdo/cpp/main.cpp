#include <cstdint>
#include <optional>

enum class CableMedium : uint8_t {
    CopperActive    = 0,
    OpticalAoc      = 1,
    OpticalIsolated = 2
};

struct ActiveCableInfo {
    uint16_t vbus_max_current_ma{0};
    uint16_t vconn_req_power_mw{1000};
    uint8_t latency_ns_code{0};
    uint8_t usb4_max_speed_gbps{0};
    CableMedium medium{CableMedium::CopperActive};
    uint8_t retimer_count{0};
    bool sop_double_prime_present{false};
};

class CableVdoParser {
public:
    [[nodiscard]] static std::optional<ActiveCableInfo> decode(uint32_t vdo1, uint32_t vdo2) noexcept {
        ActiveCableInfo info{};

        // Розбір Active Cable VDO 1: струм VBUS (біти 21..20)
        const uint8_t cur_code = (vdo1 >> 20) & 0x03;
        if (cur_code == 0x01) {
            info.vbus_max_current_ma = 3000;
        } else if (cur_code == 0x02) {
            info.vbus_max_current_ma = 5000;
        } else {
            return std::nullopt; // Некоректний або заборонений номінал струму
        }

        info.sop_double_prime_present = ((vdo1 & (1U << 17)) != 0);

        // Потужність VCONN (біти 15..13)
        const uint8_t vconn_code = (vdo1 >> 13) & 0x07;
        switch (vconn_code) {
            case 0: info.vconn_req_power_mw = 1000; break;
            case 1: info.vconn_req_power_mw = 1500; break;
            case 2: info.vconn_req_power_mw = 2000; break;
            case 3: info.vconn_req_power_mw = 3000; break;
            default: info.vconn_req_power_mw = 1000; break;
        }

        info.latency_ns_code = (vdo1 >> 10) & 0x07;

        // Розбір Active Cable VDO 2: швидкість USB4 (біти 31..24)
        const uint8_t speed_code = (vdo2 >> 24) & 0xFF;
        switch (speed_code) {
            case 0x01: info.usb4_max_speed_gbps = 20; break;
            case 0x02: info.usb4_max_speed_gbps = 40; break;
            case 0x03: info.usb4_max_speed_gbps = 80; break;
            default:   info.usb4_max_speed_gbps = 10; break;
        }

        const uint8_t med_code = (vdo2 >> 21) & 0x07;
        info.medium = (med_code <= 2) ? static_cast<CableMedium>(med_code) : CableMedium::CopperActive;

        const uint8_t retimer_code = (vdo2 >> 19) & 0x03;
        info.retimer_count = (retimer_code <= 2) ? retimer_code : 0;

        return info;
    }
};
