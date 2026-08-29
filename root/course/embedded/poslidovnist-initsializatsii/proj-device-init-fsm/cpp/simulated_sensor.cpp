#include "simulated_sensor.hpp"

namespace bringup {

SimulatedSensor::SimulatedSensor(Faults faults)
    : faults_(faults), por_ready_(faults.por_ramp)
{
    load_defaults();
}

void SimulatedSensor::load_defaults() noexcept
{
    regs_.fill(0);
    regs_[reg::ChipId] = kExpectedChipId;
    regs_[reg::ResetCtrl] = bit::DeviceReady;
}

void SimulatedSensor::power_down() noexcept
{
    powered_ = false;
    // Живлення зникло посеред байта: ведений так і лишив SDA притиснутою.
    sda_stuck_ = true;
    stuck_bits_ = kStuckBits;
}

void SimulatedSensor::power_up() noexcept
{
    powered_ = true;
    por_ready_ = now_ + faults_.por_ramp;
    reset_pending_ = false;
    load_defaults();
}

void SimulatedSensor::advance_to(Millis now)
{
    now_ = now;

    if (!cut_done_ && faults_.power_off_at && now_ >= *faults_.power_off_at) {
        cut_done_ = true;
        power_down();
    }
    if (cut_done_ && !restore_done_ && faults_.power_on_at && now_ >= *faults_.power_on_at) {
        restore_done_ = true;
        power_up();
    }
    // Внутрішній цикл перезавантаження добіг кінця: біт SW_RESET самоочистився.
    if (powered_ && reset_pending_ && now_ >= core_up_) {
        reset_pending_ = false;
        load_defaults();
    }
}

std::optional<BusError> SimulatedSensor::precheck(std::uint8_t dev_addr)
{
    if (sda_stuck_) {
        return BusError::Timeout;  // SDA в нулі — START не сформується
    }
    if (!powered_) {
        power_down();  // звернення до знеструмленого веденого валить шину
        return BusError::Nack;
    }
    if (dev_addr != reg::Address) {
        return BusError::Nack;
    }
    if (now_ < por_ready_) {
        return BusError::Nack;  // V_DD ще наростає
    }
    if (reset_pending_ && now_ < core_up_) {
        return BusError::Nack;  // генератор зупинено на час перезавантаження
    }
    return std::nullopt;
}

WriteResult SimulatedSensor::write(std::uint8_t dev_addr, std::uint8_t reg_addr,
                                   std::uint8_t value)
{
    if (const auto err = precheck(dev_addr)) {
        return std::unexpected(*err);
    }
    if (reg_addr >= kRegCount || reg_addr == reg::ChipId) {
        return std::unexpected(BusError::Nack);  // немає такого або тільки читання
    }

    if (reg_addr == reg::ResetCtrl && (value & bit::SwReset) != 0) {
        reset_pending_ = true;
        core_up_ = now_ + kResetCore;
        regs_[reg::ResetCtrl] = bit::SwReset;  // біт тримається до кінця циклу
        return {};
    }

    if (reg_addr == reg::OdrFilter && (value & 0x7F) > kOdrMax) {
        // Заборонена комбінація ODR/DLPF: кремній її мовчки ігнорує.
        // Транзакція успішна, регістр лишається нульовим — рівно той випадок,
        // заради якого й існує Read-Back.
        regs_[reg::OdrFilter] = 0x00;
        return {};
    }

    regs_[reg_addr] = value;
    return {};
}

ReadResult SimulatedSensor::read(std::uint8_t dev_addr, std::uint8_t reg_addr)
{
    if (const auto err = precheck(dev_addr)) {
        return std::unexpected(*err);
    }
    if (reg_addr >= kRegCount) {
        return std::unexpected(BusError::Nack);
    }

    std::uint8_t value = regs_[reg_addr];
    if (reg_addr == reg::OdrFilter) {
        // Біт 7 цього регістра — статус DRDY: читається одиницею незалежно від
        // записаної конфігурації. Побайтове порівняння тут завжди програє.
        value |= bit::DataReady;
    }
    return value;
}

void SimulatedSensor::recover()
{
    // На залізі SCL переводять у GPIO open-drain і женуть до дев'яти тактів,
    // поки ведений не дотактує зависле слово й не відпустить SDA.
    for (unsigned i = 0; i < 9; ++i) {
        ++scl_edges_;
        if (stuck_bits_ > 0) {
            --stuck_bits_;
        }
    }
    if (stuck_bits_ == 0) {
        sda_stuck_ = false;
    }
    ++recoveries_;
}

}  // namespace bringup
