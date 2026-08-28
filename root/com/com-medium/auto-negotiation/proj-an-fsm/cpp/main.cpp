#include <cstdint>
#include <chrono>
#include <thread>
#include <expected>
#include <span>

namespace net::phy {

enum class Speed : std::uint16_t {
    Unknown = 0,
    Speed10M = 10,
    Speed100M = 100,
    Speed1000M = 1000
};

enum class Duplex : std::uint8_t {
    Half = 0,
    Full = 1
};

enum class ClockRole : std::uint8_t {
    Slave = 0,
    Master = 1
};

enum class NegotiationError : std::uint8_t {
    HardwareTimeout,
    MasterSlaveFault,
    NoCommonTechnology,
    LinkDown
};

struct LinkProperties {
    Speed speed{Speed::Unknown};
    Duplex duplex{Duplex::Half};
    ClockRole clock_role{ClockRole::Slave};
    bool pause_tx{false};
    bool pause_rx{false};
    bool parallel_detection_used{false};
    bool duplex_mismatch_warning{false};
};

/* Абстрактний апаратний інтерфейс шини керування MDIO */
class IMdioBus {
public:
    virtual ~IMdioBus() = default;
    [[nodiscard]] virtual auto read(std::uint8_t phy_addr, std::uint8_t reg_addr) -> std::uint16_t = 0;
    virtual void write(std::uint8_t phy_addr, std::uint8_t reg_addr, std::uint16_t value) = 0;
};

class AutoNegotiationEngine {
public:
    explicit constexpr AutoNegotiationEngine(IMdioBus& bus, std::uint8_t phy_addr) noexcept
        : bus_{bus}, phy_addr_{phy_addr} {}

    auto restart() -> void {
        constexpr std::uint16_t anar_val = 0x0DE1; // 10/100 Full/Half + PAUSE + IEEE 802.3
        bus_.write(phy_addr_, 0x04, anar_val);

        constexpr std::uint16_t gcr_val = 0x0200;  // 1000BASE-T Full-Duplex
        bus_.write(phy_addr_, 0x09, gcr_val);

        std::uint16_t bmcr = bus_.read(phy_addr_, 0x00);
        bmcr |= (1u << 12) | (1u << 9); // AN Enable | Restart AN
        bus_.write(phy_addr_, 0x00, bmcr);
    }

    [[nodiscard]] auto poll_and_resolve(std::chrono::milliseconds timeout)
        -> std::expected<LinkProperties, NegotiationError> {
        
        const auto deadline = std::chrono::steady_clock::now() + timeout;
        bool ready = false;

        while (std::chrono::steady_clock::now() < deadline) {
            std::uint16_t bmsr = bus_.read(phy_addr_, 0x01);
            if (bmsr & (1u << 2)) { // Link status
                bmsr = bus_.read(phy_addr_, 0x01); // Скидання Latching Low
                if ((bmsr & (1u << 2)) && (bmsr & (1u << 5))) { // Link Up + AN Complete
                    ready = true;
                    break;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }

        if (!ready) {
            return std::unexpected(NegotiationError::HardwareTimeout);
        }

        const auto anlpar = bus_.read(phy_addr_, 0x05);
        const auto aner   = bus_.read(phy_addr_, 0x06);
        const auto gsr    = bus_.read(phy_addr_, 0x0A);
        const auto gcr    = bus_.read(phy_addr_, 0x09);
        const auto anar   = bus_.read(phy_addr_, 0x04);

        if (gsr & (1u << 15)) { // Master/Slave Configuration Fault
            return std::unexpected(NegotiationError::MasterSlaveFault);
        }

        LinkProperties result{};
        result.parallel_detection_used = !(aner & 0x0001);

        // Арбітраж пріоритетів IEEE 802.3
        if ((gcr & (1u << 9)) && (gsr & (1u << 11))) {
            result.speed = Speed::Speed1000M;
            result.duplex = Duplex::Full;
            result.clock_role = (gsr & (1u << 14)) ? ClockRole::Master : ClockRole::Slave;
        } else if ((gcr & (1u << 8)) && (gsr & (1u << 10))) {
            result.speed = Speed::Speed1000M;
            result.duplex = Duplex::Half;
            result.clock_role = (gsr & (1u << 14)) ? ClockRole::Master : ClockRole::Slave;
        } else if ((anar & (1u << 8)) && (anlpar & (1u << 8))) {
            result.speed = Speed::Speed100M;
            result.duplex = Duplex::Full;
        } else if ((anar & (1u << 7)) && (anlpar & (1u << 7))) {
            result.speed = Speed::Speed100M;
            result.duplex = Duplex::Half;
            result.duplex_mismatch_warning = result.parallel_detection_used;
        } else if ((anar & (1u << 6)) && (anlpar & (1u << 6))) {
            result.speed = Speed::Speed10M;
            result.duplex = Duplex::Full;
        } else if ((anar & (1u << 5)) && (anlpar & (1u << 5))) {
            result.speed = Speed::Speed10M;
            result.duplex = Duplex::Half;
            result.duplex_mismatch_warning = result.parallel_detection_used;
        } else {
            return std::unexpected(NegotiationError::NoCommonTechnology);
        }

        const bool loc_p  = (anar & (1u << 10)) != 0;
        const bool loc_ap = (anar & (1u << 11)) != 0;
        const bool rem_p  = (anlpar & (1u << 10)) != 0;
        const bool rem_ap = (anlpar & (1u << 11)) != 0;

        result.pause_tx = (loc_p && rem_pause) || (loc_asym && rem_pause && rem_asym);
        result.pause_rx = (loc_p && rem_pause) || (loc_p && loc_asym && rem_asym);

        return result;
    }

private:
    IMdioBus& bus_;
    std::uint8_t phy_addr_;
};

} // namespace net::phy
