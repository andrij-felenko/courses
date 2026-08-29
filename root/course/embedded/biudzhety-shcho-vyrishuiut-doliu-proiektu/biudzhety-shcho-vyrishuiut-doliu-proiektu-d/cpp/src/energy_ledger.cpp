#include "budget/energy_ledger.hpp"

namespace budget {
namespace {

constexpr double kMicrosecondsPerHour = 3.6e9;

} // namespace

void EnergyLedger::account(Phase phase, std::chrono::microseconds duration) noexcept
{
    if (duration.count() <= 0) {
        return;
    }

    const auto ticks  = static_cast<std::uint64_t>(duration.count());
    const auto charge = static_cast<std::uint64_t>(profile_[index(phase)]) * ticks;

    time_[index(phase)]   += duration;
    charge_[index(phase)] += charge;
    total_time_           += duration;
    total_charge_         += charge;
}

void EnergyLedger::enter(Phase phase) noexcept
{
    const auto now = Clock::now();
    if (running_) {
        account(active_,
                std::chrono::duration_cast<std::chrono::microseconds>(now - started_));
    }
    active_  = phase;
    started_ = now;
    running_ = true;
}

void EnergyLedger::stop() noexcept
{
    if (!running_) {
        return;
    }
    account(active_, std::chrono::duration_cast<std::chrono::microseconds>(
                         Clock::now() - started_));
    running_ = false;
}

Microamps EnergyLedger::average_current() const noexcept
{
    if (total_time_.count() <= 0) {
        return 0;
    }
    return static_cast<Microamps>(total_charge_ /
                                  static_cast<std::uint64_t>(total_time_.count()));
}

double EnergyLedger::charge_uah() const noexcept
{
    return static_cast<double>(total_charge_) / kMicrosecondsPerHour;
}

double EnergyLedger::charge_share(Phase phase) const noexcept
{
    if (total_charge_ == 0) {
        return 0.0;
    }
    return static_cast<double>(charge_[index(phase)]) /
           static_cast<double>(total_charge_);
}

double EnergyLedger::time_share(Phase phase) const noexcept
{
    if (total_time_.count() <= 0) {
        return 0.0;
    }
    return static_cast<double>(time_[index(phase)].count()) /
           static_cast<double>(total_time_.count());
}

std::chrono::hours EnergyLedger::predicted_life(double battery_mah) const noexcept
{
    const Microamps average = average_current();
    if (average == 0) {
        // Витрати нижчі за роздільність обліку — ресурс не обмежений струмом.
        return std::chrono::hours::max();
    }
    const double hours = battery_mah * 1000.0 / static_cast<double>(average);
    return std::chrono::hours{static_cast<std::chrono::hours::rep>(hours)};
}

Budget EnergyLedger::audit(double battery_mah,
                           std::chrono::hours required) const noexcept
{
    if (total_time_.count() <= 0) {
        return Budget::None; // поки нічого не виміряно, судити нема про що
    }
    return (predicted_life(battery_mah) < required) ? Budget::EnergyOver
                                                    : Budget::None;
}

std::string_view EnergyLedger::name(Phase phase) noexcept
{
    switch (phase) {
    case Phase::Sleep:    return "глибокий сон";
    case Phase::Sense:    return "опитування сенсорів";
    case Phase::Process:  return "обробка та шифрування";
    case Phase::Transmit: return "радіопередача";
    }
    return "?";
}

} // namespace budget
