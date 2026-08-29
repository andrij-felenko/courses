#include "chain.hpp"

std::optional<MeasurementChain::Taps>
MeasurementChain::advanceOneMillisecond(AnalogFrontEnd& afe)
{
    std::optional<std::int32_t> raw;

    for (std::size_t tick = 0; tick < kDecimationFactor; ++tick) {
        const auto code = static_cast<std::int32_t>(afe.step());

        if (mode_ == Sampling::Oversampled) {
            if (auto decimated = decimator_.push(code)) {
                raw = *decimated;
            }
        } else if (tick + 1 == kDecimationFactor) {
            // Один строб на мілісекунду; попередні 99 значень напруги прошивка
            // не бачила ніколи й відновити їх не зможе.
            raw = code;
        }
    }

    if (!raw) {
        return std::nullopt;
    }

    Taps taps{};
    taps.raw = *raw;
    taps.afterNotch = notch_.update(taps.raw);
    taps.afterSmoother = smoother_.update(taps.afterNotch);

    if (!notch_.ready()) {
        return std::nullopt;
    }
    return taps;
}
