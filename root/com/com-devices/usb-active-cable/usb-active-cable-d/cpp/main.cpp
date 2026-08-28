#include <cstdint>
#include <optional>
#include <span>

enum class CableType : uint8_t {
    Passive,
    ActiveRetimer,
    ActiveOptical
};

struct CableCapabilities {
    CableType type{CableType::Passive};
    uint8_t   speed_gbps{5};
    uint16_t  vconn_power_mw{0};
    uint8_t   latency_ns{0};
    bool      is_active{false};
};

// Інтерфейс контролера фізичного рівня PD
class IPdPhyController {
public:
    virtual ~IPdPhyController() = default;
    virtual bool send_vdm_discover_identity(uint8_t sop_target, std::span<uint32_t> out_vdos, uint8_t& out_count) = 0;
    virtual void set_vconn_limit_mw(uint16_t milliwatts) noexcept = 0;
    virtual void notify_retimer_topology(uint8_t count, uint8_t latency_ns) noexcept = 0;
};

class CableDiscoveryManager {
public:
    explicit CableDiscoveryManager(IPdPhyController& phy) noexcept : phy_(phy) {}

    [[nodiscard]] CableCapabilities discover_cable() {
        CableCapabilities caps{};
        uint32_t vdo_buf[7]{};
        uint8_t count = 0;

        constexpr uint8_t SopPrime = 1;
        constexpr uint8_t VdoIndexCableType2 = 4;

        if (!phy_.send_vdm_discover_identity(SopPrime, vdo_buf, count)) {
            // Немає відповіді на SOP' -> простий пасивний кабель
            caps.is_active = false;
            caps.type = CableType::Passive;
            caps.speed_gbps = 5;
            return caps;
        }

        const uint32_t id_header = vdo_buf[0];
        const uint8_t product_type = (id_header >> 27) & 0x07;

        if (product_type == 3) { // 3 = Active Cable
            caps.is_active = true;

            if (count > VdoIndexCableType2) {
                const uint32_t cable_vdo2 = vdo_buf[VdoIndexCableType2];
                const uint8_t medium = (cable_vdo2 >> 21) & 0x07;
                const uint8_t speed_code = (cable_vdo2 >> 24) & 0xFF;

                caps.type = (medium == 1 || medium == 2) ? CableType::ActiveOptical : CableType::ActiveRetimer;
                caps.speed_gbps = (speed_code == 2) ? 40 : ((speed_code == 3) ? 80 : 20);
                caps.vconn_power_mw = 1500;
                caps.latency_ns = 35;

                phy_.set_vconn_limit_mw(caps.vconn_power_mw);
                phy_.notify_retimer_topology(2, caps.latency_ns);
                return caps;
            }
        }

        caps.is_active = false;
        caps.type = CableType::Passive;
        return caps;
    }

private:
    IPdPhyController& phy_;
};
