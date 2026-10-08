#include "ad2s1210_driver.hpp"
#include <cmath>
#include <array>
#include <algorithm>

namespace resolver {

namespace {
// Регістри AD2S1210 в режимі конфігурації (A0=1, A1=1)
constexpr std::uint8_t REG_POSITION_MSB   = 0x80;
constexpr std::uint8_t REG_POSITION_LSB   = 0x81;
constexpr std::uint8_t REG_VELOCITY_MSB   = 0x82;
constexpr std::uint8_t REG_VELOCITY_LSB   = 0x83;
constexpr std::uint8_t REG_LOS_THRES      = 0x84;
constexpr std::uint8_t REG_DOS_OVER_THRES = 0x85;
constexpr std::uint8_t REG_DOS_MIS_THRES  = 0x86;
constexpr std::uint8_t REG_LOT_HIGH_THRES = 0x87;
constexpr std::uint8_t REG_LOT_LOW_THRES  = 0x88;
constexpr std::uint8_t REG_EXCIT_FREQ     = 0x89;
constexpr std::uint8_t REG_CONTROL        = 0x92;
constexpr std::uint8_t REG_FAULT          = 0xFF;

constexpr double PI_VAL = 3.14159265358979323846;
} // namespace

Ad2s1210Driver::Ad2s1210Driver(ISpiDriver& spi, ISpiGpio& gpio)
    : spi_(spi), gpio_(gpio) {}

void Ad2s1210Driver::reset_hardware() {
    gpio_.write_pin(ISpiGpio::Pin::RESET, ISpiGpio::Level::Low);
    gpio_.delay_us(10);
    gpio_.write_pin(ISpiGpio::Pin::RESET, ISpiGpio::Level::High);
    gpio_.delay_us(500);
}

void Ad2s1210Driver::set_mode(Mode mode) {
    auto val = static_cast<std::uint8_t>(mode);
    // A0 відповідає біту 0, A1 відповідає біту 1
    gpio_.write_pin(ISpiGpio::Pin::A0, (val & 0x01) ? ISpiGpio::Level::High : ISpiGpio::Level::Low);
    gpio_.write_pin(ISpiGpio::Pin::A1, (val & 0x02) ? ISpiGpio::Level::High : ISpiGpio::Level::Low);
    current_mode_ = mode;
    gpio_.delay_us(2);
}

bool Ad2s1210Driver::write_register(std::uint8_t reg_addr, std::uint8_t data) {
    Mode saved_mode = current_mode_;
    set_mode(Mode::Configuration);

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::Low);
    gpio_.delay_us(1);

    std::uint8_t dummy_rx = 0;
    bool ok1 = spi_.transfer_byte(reg_addr, dummy_rx);
    bool ok2 = spi_.transfer_byte(data, dummy_rx);

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::High);
    gpio_.delay_us(1);

    set_mode(saved_mode);
    return ok1 && ok2;
}

std::optional<std::uint8_t> Ad2s1210Driver::read_register(std::uint8_t reg_addr) {
    Mode saved_mode = current_mode_;
    set_mode(Mode::Configuration);

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::Low);
    gpio_.delay_us(1);

    std::uint8_t rx_dummy = 0;
    if (!spi_.transfer_byte(reg_addr, rx_dummy)) {
        gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::High);
        set_mode(saved_mode);
        return std::nullopt;
    }

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::High);
    gpio_.delay_us(1);

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::Low);
    std::uint8_t reg_val = 0;
    bool ok = spi_.transfer_byte(0x00, reg_val);

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::High);
    gpio_.delay_us(1);

    set_mode(saved_mode);

    if (!ok) return std::nullopt;
    return reg_val;
}

bool Ad2s1210Driver::set_resolution(Resolution res) {
    auto reg_opt = read_register(REG_CONTROL);
    std::uint8_t ctrl_val = reg_opt.value_or(0x00);

    // Маскуємо біти 7:6 для роздільної здатності
    ctrl_val &= 0x3F;
    switch (res) {
        case Resolution::Res10Bit: ctrl_val |= (0b00 << 6); break;
        case Resolution::Res12Bit: ctrl_val |= (0b01 << 6); break;
        case Resolution::Res14Bit: ctrl_val |= (0b10 << 6); break;
        case Resolution::Res16Bit: ctrl_val |= (0b11 << 6); break;
    }

    if (config_.hysteresis_enable) {
        ctrl_val |= (1 << 4);
    }
    if (config_.phase_lock_enable) {
        ctrl_val |= (1 << 5);
    }

    bool status = write_register(REG_CONTROL, ctrl_val);
    if (status) {
        config_.resolution = res;
    }
    return status;
}

std::uint8_t Ad2s1210Driver::calculate_excitation_val(std::uint32_t freq_hz, std::uint32_t clk_hz) noexcept {
    if (clk_hz == 0) return 0x01;
    // FCW = (f_exc * 32768) / clk_hz
    double val = (static_cast<double>(freq_hz) * 32768.0) / static_cast<double>(clk_hz);
    long rounded = std::lround(val);
    rounded = std::clamp(rounded, 1L, 255L);
    return static_cast<std::uint8_t>(rounded);
}

bool Ad2s1210Driver::set_excitation_frequency(std::uint32_t freq_hz, std::uint32_t clk_hz) {
    std::uint8_t fcw = calculate_excitation_val(freq_hz, clk_hz);
    bool status = write_register(REG_EXCIT_FREQ, fcw);
    if (status) {
        config_.excitation_freq_hz = freq_hz;
        config_.clk_in_hz = clk_hz;
    }
    return status;
}

bool Ad2s1210Driver::init(const Config& config) {
    config_ = config;

    reset_hardware();

    // Запис порогів виявлення несправностей
    if (!write_register(REG_LOS_THRES, config_.los_threshold)) return false;
    if (!write_register(REG_DOS_OVER_THRES, config_.dos_overrange_threshold)) return false;
    if (!write_register(REG_DOS_MIS_THRES, config_.dos_mismatch_threshold)) return false;
    if (!write_register(REG_LOT_HIGH_THRES, config_.lot_high_threshold)) return false;
    if (!write_register(REG_LOT_LOW_THRES, config_.lot_low_threshold)) return false;

    // Встановлення частоти збудження та роздільної здатності
    if (!set_excitation_frequency(config_.excitation_freq_hz, config_.clk_in_hz)) return false;
    if (!set_resolution(config_.resolution)) return false;

    // Початковий режим — зчитування кутового положення
    set_mode(Mode::Position);
    return true;
}

void Ad2s1210Driver::sample_strobe() {
    gpio_.write_pin(ISpiGpio::Pin::SAMPLE, ISpiGpio::Level::Low);
    gpio_.delay_us(2);
    gpio_.write_pin(ISpiGpio::Pin::SAMPLE, ISpiGpio::Level::High);
    gpio_.delay_us(2);
}

std::optional<std::uint16_t> Ad2s1210Driver::read_raw_position() {
    set_mode(Mode::Position);

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::Low);
    gpio_.delay_us(1);

    std::uint8_t msb = 0;
    std::uint8_t lsb = 0;
    bool ok1 = spi_.transfer_byte(0x00, msb);
    bool ok2 = spi_.transfer_byte(0x00, lsb);

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::High);

    if (!ok1 || !ok2) return std::nullopt;

    std::uint16_t raw16 = (static_cast<std::uint16_t>(msb) << 8) | lsb;

    // Для роздільної здатності менше 16 біт зсуваємо вправо
    int bit_count = static_cast<int>(config_.resolution);
    std::uint16_t pos = raw16 >> (16 - bit_count);

    return pos;
}

std::optional<std::int16_t> Ad2s1210Driver::read_raw_velocity() {
    set_mode(Mode::Velocity);

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::Low);
    gpio_.delay_us(1);

    std::uint8_t msb = 0;
    std::uint8_t lsb = 0;
    bool ok1 = spi_.transfer_byte(0x00, msb);
    bool ok2 = spi_.transfer_byte(0x00, lsb);

    gpio_.write_pin(ISpiGpio::Pin::CS, ISpiGpio::Level::High);

    if (!ok1 || !ok2) return std::nullopt;

    std::uint16_t raw16 = (static_cast<std::uint16_t>(msb) << 8) | lsb;
    return static_cast<std::int16_t>(raw16);
}

FaultStatus Ad2s1210Driver::read_fault_register() {
    FaultStatus status{};
    auto val_opt = read_register(REG_FAULT);
    if (!val_opt.has_value()) {
        return status;
    }

    std::uint8_t val = val_opt.value();
    status.raw_value = val;
    status.configuration_parity_error = (val & (1 << 7)) != 0;
    status.phase_error                = (val & (1 << 6)) != 0;
    status.velocity_overflow          = (val & (1 << 5)) != 0;
    status.loss_of_tracking           = (val & (1 << 4)) != 0;
    status.degradation_of_signal      = (val & (1 << 3)) != 0;
    status.loss_of_signal             = (val & (1 << 2)) != 0;
    status.parity_error               = (val & (1 << 1)) != 0;
    status.reference_loss             = (val & (1 << 0)) != 0;

    return status;
}

std::optional<ResolverData> Ad2s1210Driver::read_resolver_data() {
    sample_strobe();

    auto raw_pos_opt = read_raw_position();
    auto raw_vel_opt = read_raw_velocity();

    FaultStatus fault = read_fault_register();

    if (!raw_pos_opt.has_value() || !raw_vel_opt.has_value()) {
        return std::nullopt;
    }

    ResolverData data{};
    data.raw_position = raw_pos_opt.value();
    data.raw_velocity = raw_vel_opt.value();
    data.fault = fault;
    data.is_valid = !fault.has_fault();

    data.position_degrees = raw_to_degrees(data.raw_position, config_.resolution);
    data.position_radians = raw_to_radians(data.raw_position, config_.resolution);
    data.velocity_rpm = raw_to_rpm(data.raw_velocity, config_.resolution, config_.clk_in_hz);
    data.velocity_rad_per_sec = raw_to_rad_per_sec(data.raw_velocity, config_.resolution, config_.clk_in_hz);

    return data;
}

double Ad2s1210Driver::raw_to_degrees(std::uint16_t raw_pos, Resolution res) noexcept {
    double total_counts = static_cast<double>(1ULL << static_cast<std::uint8_t>(res));
    return (static_cast<double>(raw_pos) * 360.0) / total_counts;
}

double Ad2s1210Driver::raw_to_radians(std::uint16_t raw_pos, Resolution res) noexcept {
    double total_counts = static_cast<double>(1ULL << static_cast<std::uint8_t>(res));
    return (static_cast<double>(raw_pos) * 2.0 * PI_VAL) / total_counts;
}

double Ad2s1210Driver::get_max_rpm_for_resolution(Resolution res, std::uint32_t clk_hz) noexcept {
    double base_max_rpm = 7500.0;
    switch (res) {
        case Resolution::Res10Bit: base_max_rpm = 150000.0; break;
        case Resolution::Res12Bit: base_max_rpm = 60000.0;  break;
        case Resolution::Res14Bit: base_max_rpm = 30000.0;  break;
        case Resolution::Res16Bit: base_max_rpm = 7500.0;   break;
    }
    double scale = static_cast<double>(clk_hz) / 8192000.0;
    return base_max_rpm * scale;
}

double Ad2s1210Driver::raw_to_rpm(std::int16_t raw_vel, Resolution res, std::uint32_t clk_hz) noexcept {
    double max_rpm = get_max_rpm_for_resolution(res, clk_hz);
    return (static_cast<double>(raw_vel) * max_rpm) / 32767.0;
}

double Ad2s1210Driver::raw_to_rad_per_sec(std::int16_t raw_vel, Resolution res, std::uint32_t clk_hz) noexcept {
    double rpm = raw_to_rpm(raw_vel, res, clk_hz);
    return (rpm * PI_VAL) / 30.0;
}

} // namespace resolver
