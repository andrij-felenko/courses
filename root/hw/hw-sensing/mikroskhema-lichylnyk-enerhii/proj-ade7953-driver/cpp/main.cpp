#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <expected>
#include <chrono>

namespace metrology {

/* Типізовані 16-бітні адреси регістрів ADE7953 */
enum class Register : uint16_t {
    Config2      = 0x00FE,
    PgaIa        = 0x0080,
    PgaIb        = 0x0081,
    PgaV         = 0x0082,
    Config       = 0x0102,
    AccMode      = 0x0103,
    Cf1Den       = 0x0105,
    ApHCAL       = 0x0108,
    PfA          = 0x010A,
    AWatt        = 0x0212,
    AVar         = 0x0214,
    AVa          = 0x0216,
    ISumLvl      = 0x0218,
    AIrms        = 0x021A,
    BIrms        = 0x0219,
    VRms         = 0x021B,
    AIGain       = 0x021C,
    AVGain       = 0x021E,
    AIrmsOs      = 0x0223,
    AVRmsOs      = 0x0225,
    IrqEnA       = 0x022C,
    IrqStatA     = 0x022D,
    RstIrqStatA  = 0x032D,
    AEnergyA     = 0x031E,
    AEnergyB     = 0x031F
};

/* Коди помилок драйвера */
enum class MeterError {
    BusFailure,
    Timeout,
    InvalidParameter
};

/* Концепт апаратної шини SPI */
template <typename T>
concept SpiBus = requires(T bus, std::span<const uint8_t> tx, std::span<uint8_t> rx) {
    { bus.select() } -> std::same_as<void>;
    { bus.deselect() } -> std::same_as<void>;
    { bus.transfer(tx, rx) } -> std::same_as<bool>;
    { bus.delay_ms(uint32_t{}) } -> std::same_as<void>;
};

/* Налаштування коефіцієнтів та масштабів */
struct CalibrationData {
    uint8_t pga_ia{4};       // 16x для струмового шунта
    uint8_t pga_ib{4};
    uint8_t pga_v{0};        // 1x для високовольтного дільника
    int32_t aigain{0};
    int32_t avgain{0};
    int32_t airmsos{0};
    int16_t aphcal{0};
    uint16_t cf1den{63};
    float v_scale{0.000254f}; // Вольт / LSB
    float i_scale{0.000012f}; // Ампер / LSB
    float p_scale{0.003050f}; // Ват / LSB
};

/* Структура комплексних показів лічильника */
struct MeterReading {
    float voltage_rms{0.0f};
    float current_phase_rms{0.0f};
    float current_neutral_rms{0.0f};
    float active_power{0.0f};
    float reactive_power{0.0f};
    float apparent_power{0.0f};
    float power_factor{1.0f};
    int32_t energy_raw{0};
    bool tamper_alert{false};
};

/* RAII-обгортка вибору чіпа Chip Select */
template <SpiBus Spi>
class SpiGuard {
public:
    explicit SpiGuard(Spi& bus) : bus_(bus) { bus_.select(); }
    ~SpiGuard() { bus_.deselect(); }
    SpiGuard(const SpiGuard&) = delete;
    SpiGuard& operator=(const SpiGuard&) = delete;
private:
    Spi& bus_;
};

/* Шаблонний клас драйвера ADE7953 */
template <SpiBus Spi>
class Ade7953Driver {
public:
    explicit Ade7953Driver(Spi& bus, CalibrationData calib)
        : bus_(bus), calib_(calib) {}

    std::expected<void, MeterError> init() {
        // Програмне скидання мікросхеми
        if (!write_register(Register::Config, 0x0080, 2)) return std::unexpected(MeterError::BusFailure);
        bus_.delay_ms(15);

        // Блокування режиму SPI: запис 0xAD у регістр 0x00FE
        if (!write_register(Register::Config2, 0xAD, 1)) return std::unexpected(MeterError::BusFailure);

        // Конфігурація вхідних PGA
        write_register(Register::PgaIa, calib_.pga_ia, 1);
        write_register(Register::PgaIb, calib_.pga_ib, 1);
        write_register(Register::PgaV, calib_.pga_v, 1);

        // Завантаження калібрувальних регістрів
        write_register(Register::AIGain, static_cast<uint32_t>(calib_.aigain), 3);
        write_register(Register::AVGain, static_cast<uint32_t>(calib_.avgain), 3);
        write_register(Register::AIrmsOs, static_cast<uint32_t>(calib_.airmsos), 3);
        write_register(Register::ApHCAL, static_cast<uint32_t>(calib_.aphcal), 2);
        write_register(Register::Cf1Den, calib_.cf1den, 2);

        // Увімкнення режиму захисту від розкрадання: облік за max(IA, IB)
        write_register(Register::AccMode, 0x0008, 2);

        // Дозвіл переривання на вивід IRQ_A при фіксації дисбалансу
        write_register(Register::IrqEnA, (1UL << 14), 3);

        return {};
    }

    std::expected<MeterReading, MeterError> read_metrics() {
        auto v_raw = read_register(Register::VRms, 3);
        auto ia_raw = read_register(Register::AIrms, 3);
        auto ib_raw = read_register(Register::BIrms, 3);
        auto p_raw = read_signed_register(Register::AWatt, 3);
        auto q_raw = read_signed_register(Register::AVar, 3);
        auto s_raw = read_signed_register(Register::AVa, 3);
        auto pf_raw = read_signed_register(Register::PfA, 2);
        auto energy_raw = read_signed_register(Register::AEnergyA, 4);
        auto irq_stat = read_register(Register::RstIrqStatA, 3);

        if (!v_raw || !ia_raw || !p_raw || !irq_stat) {
            return std::unexpected(MeterError::BusFailure);
        }

        MeterReading reading{};
        reading.voltage_rms = static_cast<float>(*v_raw) * calib_.v_scale;
        reading.current_phase_rms = static_cast<float>(*ia_raw) * calib_.i_scale;
        reading.current_neutral_rms = static_cast<float>(*ib_raw) * calib_.i_scale;
        reading.active_power = static_cast<float>(*p_raw) * calib_.p_scale;
        reading.reactive_power = static_cast<float>(*q_raw) * calib_.p_scale;
        reading.apparent_power = static_cast<float>(*s_raw) * calib_.p_scale;
        reading.power_factor = static_cast<float>(*pf_raw) / 32768.0f;
        reading.energy_raw = *energy_raw;
        reading.tamper_alert = (*irq_stat & (1UL << 14)) != 0;

        return reading;
    }

private:
    bool write_register(Register reg, uint32_t value, size_t bytes) {
        uint8_t buffer[7];
        const uint16_t addr = static_cast<uint16_t>(reg);
        buffer[0] = static_cast<uint8_t>(addr >> 8);
        buffer[1] = static_cast<uint8_t>(addr & 0xFF);
        buffer[2] = 0x00; // Write command

        for (size_t i = 0; i < bytes; ++i) {
            buffer[3 + i] = static_cast<uint8_t>(value >> ((bytes - 1 - i) * 8));
        }

        SpiGuard<Spi> guard(bus_);
        return bus_.transfer(std::span<const uint8_t>(buffer, 3 + bytes), {});
    }

    std::expected<uint32_t, MeterError> read_register(Register reg, size_t bytes) {
        uint8_t tx[7]{};
        uint8_t rx[7]{};
        const uint16_t addr = static_cast<uint16_t>(reg);
        tx[0] = static_cast<uint8_t>(addr >> 8);
        tx[1] = static_cast<uint8_t>(addr & 0xFF);
        tx[2] = 0x80; // Read command

        {
            SpiGuard<Spi> guard(bus_);
            if (!bus_.transfer(std::span<const uint8_t>(tx, 3 + bytes), std::span<uint8_t>(rx, 3 + bytes))) {
                return std::unexpected(MeterError::BusFailure);
            }
        }

        uint32_t result = 0;
        for (size_t i = 0; i < bytes; ++i) {
            result = (result << 8) | rx[3 + i];
        }
        return result;
    }

    std::expected<int32_t, MeterError> read_signed_register(Register reg, size_t bytes) {
        auto val = read_register(reg, bytes);
        if (!val) return std::unexpected(val.error());

        uint32_t raw = *val;
        if (bytes == 3 && (raw & 0x800000)) raw |= 0xFF000000;
        else if (bytes == 2 && (raw & 0x8000)) raw |= 0xFFFF0000;

        return static_cast<int32_t>(raw);
    }

    Spi& bus_;
    CalibrationData calib_;
};

} // namespace metrology
