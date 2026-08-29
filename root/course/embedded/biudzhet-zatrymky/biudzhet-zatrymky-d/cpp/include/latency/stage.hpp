// stage.hpp — одна ланка тракту затримки.
//
// Час тут не double, а std::chrono::duration: одиниця живе в типі, тож
// переплутати мілісекунди з мікросекундами компілятор не дасть. Усі
// конструктори constexpr — конфігурація комплексу рахується на етапі
// компіляції, а хибна вилка стає помилкою збірки, а не збоєм у польоті.
#pragma once

#include <chrono>
#include <stdexcept>
#include <string_view>

namespace latency {

using Ms = std::chrono::duration<double, std::milli>;

enum class Kind {
    Fixed,     // стала: час у дроті, час обчислення, час у повітрі
    Periodic,  // квантування тактом: чекання наступного циклу
    Band       // вилка min..typ..max: фізика з розкидом
};

enum class Domain {
    Electronic,  // цифра й радіо: те, що інженер може прискорити
    Physical     // інерція гвинта, експозиція, час відгуку пікселя
};

struct Stage {
    std::string_view name{};
    Kind             kind{Kind::Fixed};
    Domain           domain{Domain::Electronic};
    Ms               min{};
    Ms               typ{};
    Ms               max{};
    Ms               period{};        // період такту для Kind::Periodic
    bool             phase_locked{};  // тайм-слот зведено з попередньою ланкою
};

// Вилка: фізика з розкидом (розгін гвинта, експозиція, декодер).
constexpr Stage band(std::string_view name, Ms min, Ms typ, Ms max) {
    if (!(min >= Ms{0}) || !(typ >= min) || !(max >= typ)) {
        // У constexpr-контексті це не виняток, а відмова компілятора
        // зібрати конфігурацію — саме там, де описку й треба ловити.
        throw std::invalid_argument{"хибна вилка ланки: треба 0 <= min <= typ <= max"};
    }
    return Stage{name, Kind::Band, Domain::Electronic, min, typ, max, Ms{}, false};
}

// Стала: обчислення мікшера, комутація ключів, кадр DShot.
constexpr Stage fixed(std::string_view name, Ms value) {
    if (!(value >= Ms{0})) {
        throw std::invalid_argument{"стала затримка не може бути від'ємною"};
    }
    return Stage{name, Kind::Fixed, Domain::Electronic, value, value, value, Ms{}, false};
}

// Вільний такт: подія рівноймовірно падає всередину періоду,
// тож min = 0, typ = T/2, max = T.
constexpr Stage periodic(std::string_view name, double rate_hz) {
    if (!(rate_hz > 0.0)) {
        throw std::invalid_argument{"частота такту має бути додатною"};
    }
    const Ms period{1000.0 / rate_hz};
    return Stage{name, Kind::Periodic, Domain::Electronic,
                 Ms{0}, period / 2.0, period, period, false};
}

// Зведений такт (EdgeTX Mixer Sync, растр аналогових окулярів за
// синхросигналом): квант згортається до сталого зсуву — у цьому весь виграш.
constexpr Stage periodic_locked(std::string_view name, double rate_hz, Ms slack) {
    if (!(rate_hz > 0.0)) {
        throw std::invalid_argument{"частота такту має бути додатною"};
    }
    const Ms period{1000.0 / rate_hz};
    if (!(slack >= Ms{0}) || slack > period) {
        throw std::invalid_argument{"люфт фазування не може перевищувати період такту"};
    }
    return Stage{name, Kind::Periodic, Domain::Electronic,
                 slack, slack, slack, period, true};
}

// Час фізичної видачі кадру в асинхронну шину: SBUS, CRSF, будь-який UART.
// bits_per_byte враховує старт/стоп/парність: 10 для 8-N-1, 11 для 8-E-2.
constexpr Stage serial(std::string_view name, std::size_t frame_bytes,
                       double baud_bps, unsigned bits_per_byte = 10) {
    if (frame_bytes == 0 || bits_per_byte == 0 || !(baud_bps > 0.0)) {
        throw std::invalid_argument{"параметри шини мають бути додатними"};
    }
    const Ms t{static_cast<double>(frame_bytes) * bits_per_byte * 1000.0 / baud_bps};
    return Stage{name, Kind::Fixed, Domain::Electronic, t, t, t, Ms{}, false};
}

// Позначає ланку фізичною: її не прискорити ні прошивкою, ні швидшим МК.
constexpr Stage physical(Stage s) noexcept {
    s.domain = Domain::Physical;
    return s;
}

}  // namespace latency
