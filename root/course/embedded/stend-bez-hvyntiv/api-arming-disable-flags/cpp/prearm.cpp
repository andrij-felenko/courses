#include "prearm.hpp"

namespace bf {
namespace {

[[nodiscard]] bool linkUsable(const StandInputs& in) noexcept
{
    return in.rxFrameValid && !in.rxFailsafeFlag;
}

}  // namespace

PrearmMonitor::PrearmMonitor(const StandInputs& atBoot, Millis now)
    : linkOk_{linkUsable(atBoot)},
      linkOkSince_{now},
      linkLostSince_{now},
      failsafe_{!linkUsable(atBoot)},
      // Плату ввімкнено з піднятим тумблером — засувка, яку знімає лише
      // фізичне опускання тумблера, а не наступний такт.
      armSwitchLatched_{atBoot.armSwitchHigh}
{
}

void PrearmMonitor::updateLink(const StandInputs& in, Millis now)
{
    const bool usable = linkUsable(in);

    if (usable && !linkOk_) {
        linkOk_ = true;
        linkOkSince_ = now;          // відлік захисної секунди з нуля
    } else if (!usable && linkOk_) {
        linkOk_ = false;
        linkLostSince_ = now;
    }

    if (!linkOk_ && now - linkLostSince_ >= kFailsafeDelay) {
        failsafe_ = true;
    }
    // Знімається тільки після цілої секунди БЕЗ жодного пропуску: кожен
    // втрачений кадр перезаписує linkOkSince_ і відлік починається знову.
    if (failsafe_ && linkOk_ && now - linkOkSince_ >= kRxRecovery) {
        failsafe_ = false;
    }
}

Mask PrearmMonitor::update(const StandInputs& in, Millis now)
{
    updateLink(in, now);
    if (!in.armSwitchHigh) {
        armSwitchLatched_ = false;
    }

    Mask mask;

    // сенсори
    mask.set(Flag::NoGyro, !in.gyroPresent);
    mask.set(Flag::Calibrating, in.gyroCalibrating);
    mask.set(Flag::AccCal, !in.accCalibrated);

    // радіолінк
    mask.set(Flag::Failsafe, failsafe_);
    mask.set(Flag::BadRxRecovery, failsafe_ && linkOk_);
    mask.set(Flag::RxFailsafe, in.rxFailsafeFlag);
    mask.set(Flag::BoxFailsafe, in.boxFailsafe);

    // органи керування
    mask.set(Flag::Throttle, in.throttleUs > kMinCheckUs);
    const bool clipped = in.rollUs < kRcMinUs || in.rollUs > kRcMaxUs ||
                         in.pitchUs < kRcMinUs || in.pitchUs > kRcMaxUs;
    mask.set(Flag::RollPitchClipped, clipped);
    mask.set(Flag::ArmSwitch, armSwitchLatched_);
    mask.set(Flag::NoPrearm, in.prearmRequired && !in.prearmEngaged);

    // інтерфейси конфігурації
    mask.set(Flag::Cli, in.cliOpen);
    mask.set(Flag::Msp, in.mspClientActive);
    mask.set(Flag::MotorTest, in.motorTestActive);
    mask.set(Flag::CmsMenu, in.cmsMenuOpen);
    mask.set(Flag::OsdMenu, in.osdMenuOpen);

    // мотори й приводи
    mask.set(Flag::ServoInit, in.servosSettling);
    mask.set(Flag::MotorProtocol, !in.motorProtocolOk);
    mask.set(Flag::RpmFilter, in.rpmFilterEnabled && !in.escTelemetryOk);

    // решта
    mask.set(Flag::Paralyze, in.paralyze);
    mask.set(Flag::Rescue, in.rescueSwitch);
    mask.set(Flag::RebootRequired, in.rebootRequired);
    mask.set(Flag::Gps, in.gpsRequired && in.gpsSats < kGpsMinSats);
    mask.set(Flag::CpuLoad, in.cpuLoadPercent > kCpuLoadLimitPercent);

    return mask;
}

}  // namespace bf
