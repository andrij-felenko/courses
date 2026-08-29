#include "shadow_agent.hpp"

#include <cmath>

namespace iot {

std::string_view describe(DeltaError error) noexcept
{
    switch (error) {
        case DeltaError::Stale:      return "застаріла версія — відкинуто";
        case DeltaError::Empty:      return "порожня дельта";
        case DeltaError::OutOfRange: return "поза фізичними межами — відкинуто";
    }
    return "невідомо";
}

ConfigDelta difference(const NodeConfig& desired, const NodeConfig& active) noexcept
{
    ConfigDelta diff{};
    diff.sequenceId = desired.sequenceId;

    if (std::fabs(desired.targetTemperature - active.targetTemperature) > kTempEpsilonC) {
        diff.targetTemperature = desired.targetTemperature;
    }
    if (desired.fanSpeedRpm != active.fanSpeedRpm) {
        diff.fanSpeedRpm = desired.fanSpeedRpm;
    }
    if (desired.heatingEnabled != active.heatingEnabled) {
        diff.heatingEnabled = desired.heatingEnabled;
    }
    return diff;
}

ShadowAgent::ShadowAgent(const NodeConfig& boot) noexcept
    : desired_{boot}, active_{boot}, reported_{boot}
{
    /* На старті всі три погляди збігаються: іншої думки про залізо ще ніхто не має. */
}

std::expected<void, DeltaError> ShadowAgent::applyDelta(const ConfigDelta& delta) noexcept
{
    if (delta.empty()) {
        return std::unexpected(DeltaError::Empty);
    }

    /* Захист від гонок: у радіоканалі пакети дублюються й обганяють одне одного.
       Порівнюємо з версією ОСТАННЬОЇ ПРИЙНЯТОЇ дельти, а не з тією, що в залізі:
       інакше застарілий пакет проліз би у вікні між прийомом і застосуванням. */
    if (delta.sequenceId <= desired_.sequenceId) {
        ++staleRejected_;
        return std::unexpected(DeltaError::Stale);
    }

    if (auto checked = validate(delta); !checked) {
        /* Версію НЕ підвищуємо: дельта в хмарі лишиться ненульовою,
           і оператор побачить, що вузол уставку не прийняв. */
        ++rangeRejected_;
        return std::unexpected(checked.error());
    }

    if (delta.targetTemperature) {
        desired_.targetTemperature = *delta.targetTemperature;
    }
    if (delta.fanSpeedRpm) {
        desired_.fanSpeedRpm = *delta.fanSpeedRpm;
    }
    if (delta.heatingEnabled) {
        desired_.heatingEnabled = *delta.heatingEnabled;
    }
    desired_.sequenceId = delta.sequenceId;

    return {};
}

ConfigDelta ShadowAgent::pending() const noexcept
{
    return difference(desired_, active_);
}

ConfigDelta ShadowAgent::reconcileHardware() noexcept
{
    const ConfigDelta written = pending();

    if (written.empty() && active_.sequenceId == desired_.sequenceId) {
        return written;
    }

    /* Тут у справжньому виробі йде запис у драйвери: шпаруватість ШІМ клапана,
       уставка ПІД-регулятора, реле котла. Пишемо лише те, що справді змінилося. */
    if (written.targetTemperature) {
        active_.targetTemperature = *written.targetTemperature;
    }
    if (written.fanSpeedRpm) {
        active_.fanSpeedRpm = *written.fanSpeedRpm;
    }
    if (written.heatingEnabled) {
        active_.heatingEnabled = *written.heatingEnabled;
    }
    active_.sequenceId = desired_.sequenceId;

    /* reported знімається з ФАКТИЧНОГО стану заліза, а не з бажаного:
       вузол звітує про те, що зробив, а не про те, що йому наказали. */
    reported_ = active_;
    reportedDirty_ = true;

    return written;
}

void ShadowAgent::recordTelemetry(TelemetryEntry entry) noexcept
{
    entry.fromOfflineCache = (link_ != Link::Connected && link_ != Link::Syncing);
    entry.heatingActive = active_.heatingEnabled;
    queue_.push(entry);
}

} // namespace iot
