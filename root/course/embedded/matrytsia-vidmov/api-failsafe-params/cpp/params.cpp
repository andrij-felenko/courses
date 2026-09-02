#include "params.hpp"

#include <algorithm>
#include <cmath>
#include <format>

namespace autopilot::failsafe {

namespace {

// Прапорці й таймери в мілісекундах зберігаються цілими: округлюємо на вході.
float quantize(const ParamDesc& d, float value) noexcept
{
    return d.type == ParamType::Float ? value : std::nearbyint(value);
}

bool inRange(const ParamDesc& d, float value) noexcept
{
    // Записано "не в межах", щоб NaN гарантовано не пройшов.
    return value >= d.min && value <= d.max;
}

} // namespace

std::string_view toString(ParamError e) noexcept
{
    switch (e) {
    case ParamError::UnknownName: return "UNKNOWN_PARAM";
    case ParamError::OutOfRange:  return "OUT_OF_RANGE";
    }
    return "?";
}

ParamBlock::ParamBlock() noexcept
{
    for (std::size_t i = 0; i < kParamCount; ++i)
        v_[i] = kParamDesc[i].def;
}

std::expected<void, ParamError> ParamBlock::set(ParamId id, float value) noexcept
{
    const auto idx = static_cast<std::size_t>(id);
    if (idx >= kParamCount)
        return std::unexpected(ParamError::UnknownName);
    const auto& d = kParamDesc[idx];
    if (!inRange(d, value))
        return std::unexpected(ParamError::OutOfRange);
    v_[idx] = quantize(d, value);
    return {};
}

std::expected<void, ParamError> ParamBlock::set(std::string_view name, float value) noexcept
{
    return find(name).and_then([&](ParamId id) { return set(id, value); });
}

std::expected<ParamId, ParamError> ParamBlock::find(std::string_view name) noexcept
{
    const auto it = std::ranges::find(kParamDesc, name, &ParamDesc::name);
    if (it == kParamDesc.end())
        return std::unexpected(ParamError::UnknownName);
    return static_cast<ParamId>(std::distance(kParamDesc.begin(), it));
}

std::size_t ParamBlock::restore(std::span<const float> stored) noexcept
{
    std::size_t replaced = 0;
    const std::size_t n = std::min(stored.size(), kParamCount);

    for (std::size_t i = 0; i < n; ++i) {
        const auto& d = kParamDesc[i];
        if (inRange(d, stored[i])) {
            v_[i] = quantize(d, stored[i]);
        } else {
            v_[i] = d.def;  // калібрування зі старої схеми не лізе в нові межі
            ++replaced;
        }
    }
    // Параметрів, доданих новішою схемою, у секторі просто немає — лишаються дефолти.
    for (std::size_t i = n; i < kParamCount; ++i)
        v_[i] = kParamDesc[i].def;
    return replaced;
}

std::vector<std::string> ParamBlock::validate(float rtlAltM) const
{
    std::vector<std::string> bad;

    for (std::size_t i = 0; i < kParamCount; ++i) {
        const auto& d = kParamDesc[i];
        if (!inRange(d, v_[i]))
            bad.push_back(std::format("{}={:.2f} поза [{:.2f}..{:.2f}]",
                                      d.name, v_[i], d.min, d.max));
    }

    const float low  = get(ParamId::BattLowV);
    const float crit = get(ParamId::BattCritV);

    // 1. Між попередженням і примусовою посадкою мусить лишатися запас часу.
    if (low - crit < 0.15f)
        bad.push_back(std::format("FS_BATT_LOW_V({:.2f}) - FS_BATT_CRIT_V({:.2f})"
                                  " < 0.15 В/комірка", low, crit));

    // 2. Приймач у режимі Hold Last State повторює останній кадр, і програмний
    //    лічильник обриву не побачить: поріг газу мусить бути нижчим за 1000 мкс.
    if (getInt(ParamId::ThrEnable) != 0 && get(ParamId::ThrValue) >= 1000.0f)
        bad.push_back(std::format("FS_THR_VALUE({:.0f}) не нижчий за мінімум газу 1000 мкс",
                                  get(ParamId::ThrValue)));

    // 3. Гістерезис відновлення коротший за секунду дає брязкіт на межі радіовидимості.
    if (get(ParamId::RcRecover) < 1.0f)
        bad.push_back(std::format("FS_RC_RECOVER({:.2f}) < 1.0 с", get(ParamId::RcRecover)));

    // 4. Стеля геозони мусить бути вищою за висоту повернення, інакше RTL
    //    пробиває власний висотний бар'єр.
    if (get(ParamId::FenceAltMax) < rtlAltM + 20.0f)
        bad.push_back(std::format("FS_FENCE_ALT_MAX({:.0f}) < RTL_ALT({:.0f}) + 20 м",
                                  get(ParamId::FenceAltMax), rtlAltM));

    // 5. Зведення з вимкненим батарейним чи канальним захистом заборонене.
    if (getInt(ParamId::BattAct) < 1)
        bad.emplace_back("батарейний захист вимкнено (FS_BATT_ACT=0)");
    if (getInt(ParamId::ThrEnable) == 0)
        bad.emplace_back("канальний failsafe вимкнено (FS_THR_ENABLE=0)");

    return bad;
}

} // namespace autopilot::failsafe
