#pragma once

#include <chrono>
#include <concepts>
#include <cstdint>

namespace safety {

/*
 * Контракт апаратної платформи, виражений концептом. Драйвер не має
 * віртуальних викликів і не знає конкретного мікроконтролера, але помилка
 * в адаптері (не та сигнатура, не той тип часу) ловиться компілятором
 * на місці інстанціації, а не осцилографом на стенді.
 */
template <typename Platform>
concept HardwarePlatform = requires(Platform &p,
                                    bool level,
                                    std::uint16_t duty,
                                    std::chrono::milliseconds window) {
    /* Вивід серцебиття: рівень динамічного меандру помпи заряду. */
    { p.writeHeartbeat(level) } -> std::same_as<void>;

    /* Вивід ШІМ мотора, тики заповнення. */
    { p.setPwmDuty(duty) } -> std::same_as<void>;

    /* Вільний лічильник. Тип із <chrono> навмисно: сплутати мілісекунди
     * з мікросекундами тут коштувало б розірваного меандру. */
    { p.now() } -> std::same_as<std::chrono::microseconds>;

    { p.supplyVoltageMv() } -> std::same_as<std::uint16_t>;
    { p.estopActive() } -> std::same_as<bool>;
    { p.overTemperature() } -> std::same_as<bool>;
    { p.overCurrent() } -> std::same_as<bool>;

    { p.startWatchdog(window) } -> std::same_as<void>;
    { p.feedWatchdog() } -> std::same_as<void>;
};

} // namespace safety
