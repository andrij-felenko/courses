#include <cstdint>
#include <expected>
#include <concepts>
#include <chrono>
#include <thread>
#include <optional>

namespace net::phy {

enum class Register : uint8_t {
    Bmcr   = 0x00,
    Bmsr   = 0x01,
    PhyId1 = 0x02,
    PhyId2 = 0x03,
    Anar   = 0x04,
    Anlpar = 0x05,
    Gbcr   = 0x09,
    Gbsr   = 0x0A
};

namespace bmcr_bits {
    constexpr uint16_t Reset         = 1U << 15;
    constexpr uint16_t Speed100      = 1U << 13;
    constexpr uint16_t AutoNegEnable = 1U << 12;
    constexpr uint16_t RestartAutoNeg= 1U << 9;
    constexpr uint16_t FullDuplex    = 1U << 8;
    constexpr uint16_t Speed1000     = 1U << 6;
}

namespace bmsr_bits {
    constexpr uint16_t AutoNegDone   = 1U << 5;
    constexpr uint16_t LinkStatus    = 1U << 2;
}

namespace anar_bits {
    constexpr uint16_t PauseAsym     = 1U << 11;
    constexpr uint16_t PauseSym      = 1U << 10;
    constexpr uint16_t Adv100Full    = 1U << 8;
    constexpr uint16_t Adv100Half    = 1U << 7;
    constexpr uint16_t Adv10Full     = 1U << 6;
    constexpr uint16_t Adv10Half     = 1U << 5;
    constexpr uint16_t Selector802_3 = 0x0001;
}

namespace gb_bits {
    constexpr uint16_t Adv1000Full   = 1U << 9;
    constexpr uint16_t Adv1000Half   = 1U << 8;
    constexpr uint16_t Lp1000Full    = 1U << 11;
    constexpr uint16_t Lp1000Half    = 1U << 10;
}

enum class Speed : uint16_t { Unknown = 0, Mbps10 = 10, Mbps100 = 100, Mbps1000 = 1000 };
enum class Duplex : uint8_t { Half, Full };
enum class DriverError { BusError, Timeout, DeviceNotFound, ResetFailed };

struct LinkState {
    bool link_up{false};
    Speed speed{Speed::Unknown};
    Duplex duplex{Duplex::Half};
    bool pause_rx{false};
    bool pause_tx{false};
};

/* Концепт апаратного інтерфейсу GPIO для переносимості */
template <typename T>
concept GpioInterface = requires(T g, bool level) {
    { g.set_mdc(level) };
    { g.set_mdio_direction_out(level) };
    { g.set_mdio_data(level) };
    { g.get_mdio_data() } -> std::same_as<bool>;
    { g.delay_half_period() };
};

template <GpioInterface Gpio>
class MdioDriver {
public:
    explicit MdioDriver(Gpio gpio, uint8_t phy_addr)
        : gpio_(gpio), phy_addr_(phy_addr) {}

    std::expected<uint16_t, DriverError> read_register(Register reg) {
        send_preamble();
        send_bits(0x01, 2); // ST = 01b
        send_bits(0x02, 2); // OP = 10b (Read)
        send_bits(phy_addr_, 5);
        send_bits(static_cast<uint8_t>(reg), 5);

        gpio_.set_mdio_direction_out(false); // Вхід

        // TA такт 1
        clock_cycle();

        // TA такт 2 (перевірка підтвердження)
        gpio_.set_mdc(false);
        gpio_.delay_half_period();
        bool ack = !gpio_.get_mdio_data();
        gpio_.set_mdc(true);
        gpio_.delay_half_period();

        if (!ack) {
            return std::unexpected(DriverError::DeviceNotFound);
        }

        uint16_t data = 0;
        for (int i = 0; i < 16; ++i) {
            gpio_.set_mdc(false);
            gpio_.delay_half_period();
            data = (data << 1) | (gpio_.get_mdio_data() ? 1U : 0U);
            gpio_.set_mdc(true);
            gpio_.delay_half_period();
        }

        clock_cycle();
        return data;
    }

    std::expected<void, DriverError> write_register(Register reg, uint16_t value) {
        send_preamble();
        send_bits(0x01, 2); // ST = 01b
        send_bits(0x01, 2); // OP = 01b (Write)
        send_bits(phy_addr_, 5);
        send_bits(static_cast<uint8_t>(reg), 5);
        send_bits(0x02, 2); // TA = 10b
        send_bits(value, 16);

        gpio_.set_mdio_direction_out(false);
        clock_cycle();
        return {};
    }

    std::expected<void, DriverError> init() {
        auto id = read_register(Register::PhyId1);
        if (!id || *id == 0xFFFF || *id == 0x0000) {
            return std::unexpected(DriverError::DeviceNotFound);
        }

        if (!write_register(Register::Bmcr, bmcr_bits::Reset)) {
            return std::unexpected(DriverError::BusError);
        }

        // Очікуємо завершення програмного скидання
        bool reset_ok = false;
        for (int i = 0; i < 50; ++i) {
            auto bmcr = read_register(Register::Bmcr);
            if (bmcr && !(*bmcr & bmcr_bits::Reset)) {
                reset_ok = true;
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }

        if (!reset_ok) {
            return std::unexpected(DriverError::ResetFailed);
        }

        // Оголошуємо підтримувані швидкості
        uint16_t anar = anar_bits::Selector802_3 | anar_bits::Adv10Half | anar_bits::Adv10Full |
                        anar_bits::Adv100Half | anar_bits::Adv100Full |
                        anar_bits::PauseSym | anar_bits::PauseAsym;
        write_register(Register::Anar, anar);

        uint16_t gbcr = gb_bits::Adv1000Full | gb_bits::Adv1000Half;
        write_register(Register::Gbcr, gbcr);

        // Перезапускаємо автопогодження
        write_register(Register::Bmcr, bmcr_bits::AutoNegEnable | bmcr_bits::RestartAutoNeg);
        return {};
    }

    std::expected<LinkState, DriverError> poll_link() {
        LinkState state{};

        // Подвійне читання для очищення засувки Latching Low
        read_register(Register::Bmsr);
        auto bmsr = read_register(Register::Bmsr);
        if (!bmsr) {
            return std::unexpected(DriverError::BusError);
        }

        if (!(*bmsr & bmsr_bits::LinkStatus)) {
            state.link_up = false;
            return state;
        }

        state.link_up = true;
        if (!(*bmsr & bmsr_bits::AutoNegDone)) {
            state.speed = Speed::Unknown;
            return state;
        }

        auto gbcr = read_register(Register::Gbcr).value_or(0);
        auto gbsr = read_register(Register::Gbsr).value_or(0);
        auto anar = read_register(Register::Anar).value_or(0);
        auto anlpar = read_register(Register::Anlpar).value_or(0);

        // Вибір за пріоритетом IEEE 802.3
        if ((gbcr & gb_bits::Adv1000Full) && (gbsr & gb_bits::Lp1000Full)) {
            state.speed = Speed::Mbps1000;
            state.duplex = Duplex::Full;
        } else if ((gbcr & gb_bits::Adv1000Half) && (gbsr & gb_bits::Lp1000Half)) {
            state.speed = Speed::Mbps1000;
            state.duplex = Duplex::Half;
        } else if ((anar & anar_bits::Adv100Full) && (anlpar & anar_bits::Adv100Full)) {
            state.speed = Speed::Mbps100;
            state.duplex = Duplex::Full;
        } else if ((anar & anar_bits::Adv100Half) && (anlpar & anar_bits::Adv100Half)) {
            state.speed = Speed::Mbps100;
            state.duplex = Duplex::Half;
        } else if ((anar & anar_bits::Adv10Full) && (anlpar & anar_bits::Adv10Full)) {
            state.speed = Speed::Mbps10;
            state.duplex = Duplex::Full;
        } else if ((anar & anar_bits::Adv10Half) && (anlpar & anar_bits::Adv10Half)) {
            state.speed = Speed::Mbps10;
            state.duplex = Duplex::Half;
        }

        bool loc_sym  = (anar & anar_bits::PauseSym) != 0;
        bool loc_asym = (anar & anar_bits::PauseAsym) != 0;
        bool lp_sym   = (anlpar & anar_bits::PauseSym) != 0;
        bool lp_asym  = (anlpar & anar_bits::PauseAsym) != 0;

        if (loc_sym && lp_sym) {
            state.pause_rx = true;
            state.pause_tx = true;
        } else if (loc_asym && lp_sym && lp_asym) {
            state.pause_rx = true;
            state.pause_tx = false;
        } else if (loc_sym && loc_asym && lp_asym) {
            state.pause_rx = false;
            state.pause_tx = true;
        }

        return state;
    }

    /* Непрямий доступ до регістрів Clause 45 (MMD) */
    std::expected<uint16_t, DriverError> read_mmd(uint8_t dev_addr, uint16_t reg_addr) {
        // Крок 1: вибір адреси пристрою
        if (!write_register(Register::MmdAcr, dev_addr & 0x1F)) return std::unexpected(DriverError::BusError);
        // Крок 2: встановлення цільової адреси
        if (!write_register(Register::MmdAadr, reg_addr)) return std::unexpected(DriverError::BusError);
        // Крок 3: перехід у режим читання даних без автоінкременту (біти 15:14 = 01b)
        if (!write_register(Register::MmdAcr, (1U << 14) | (dev_addr & 0x1F))) return std::unexpected(DriverError::BusError);
        // Крок 4: безпосереднє читання даних
        return read_register(Register::MmdAadr);
    }

    std::expected<void, DriverError> write_mmd(uint8_t dev_addr, uint16_t reg_addr, uint16_t val) {
        if (!write_register(Register::MmdAcr, dev_addr & 0x1F)) return std::unexpected(DriverError::BusError);
        if (!write_register(Register::MmdAadr, reg_addr)) return std::unexpected(DriverError::BusError);
        if (!write_register(Register::MmdAcr, (1U << 14) | (dev_addr & 0x1F))) return std::unexpected(DriverError::BusError);
        return write_register(Register::MmdAadr, val);
    }

private:
    void clock_cycle() {
        gpio_.set_mdc(false);
        gpio_.delay_half_period();
        gpio_.set_mdc(true);
        gpio_.delay_half_period();
    }

    void send_bits(uint32_t val, uint8_t count) {
        for (int8_t i = count - 1; i >= 0; --i) {
            gpio_.set_mdc(false);
            gpio_.set_mdio_data((val >> i) & 1U);
            gpio_.delay_half_period();
            gpio_.set_mdc(true);
            gpio_.delay_half_period();
        }
    }

    void send_preamble() {
        gpio_.set_mdio_direction_out(true);
        gpio_.set_mdio_data(true);
        for (int i = 0; i < 32; ++i) {
            clock_cycle();
        }
    }

    Gpio gpio_;
    uint8_t phy_addr_;
};

} // namespace net::phy
