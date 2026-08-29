// sleep.hpp — детермінований автомат присипляння плати.
//
// Порядок кроків тут не косметичний: паркування ліній мусить статися до
// розмикання ключа, аналоговий режим — після, а WFI — тільки коли озброєне
// джерело пробудження й аудит не знайшов плаваючих входів. Кожне порушення
// повертається як Fault, а не тоне в логах.
#pragma once

#include <chrono>
#include <cstdint>
#include <expected>

#include "board.hpp"

namespace lowpower {

enum class Fault : std::uint8_t {
    OutOfOrder,        // крок викликано не в тому порядку
    RailStillPowered,  // ключ розімкнено, а шина датчика жива
    FloatingPins,      // лишилися цифрові входи без підтяжки
    NoWakeSource,      // нікому розбудити: заснули б назавжди
    RtcTimeout,        // LSE не завівся або таймер не прийняв значення
    StandbyRefused     // з режиму Standby керування не мало повернутися
};

enum class WakeSource : std::uint8_t { RtcTimer, Button, Unknown };

enum class Stage : std::uint8_t {
    Awake,
    BusesParked,
    RailOff,
    PinsAnalog,
    DebugSilent,
    WakeArmed,
    Ready
};

// Те, що вимір показав би, якби мав голос: чим розбудило й що по дорозі
// виглядало підозріло. Приєднаний зонд робить будь-який вимір струму
// недостовірним, але сну не заважає.
struct Report {
    WakeSource source{WakeSource::Unknown};
    bool probeAttached{false};
    bool railSuspect{false};
    board::FloatingPins audit{};
};

// Налагоджувальна інфраструктура ядра — окрема від автомата річ:
// вона не має станів, її просто гасять.
namespace coresight {

[[nodiscard]] bool probeAttached() noexcept;
void silence() noexcept;             // DBGMCU_CR, TRCENA, ITM, DWT, виводи SWD/SWO
void unfreezePeripherals() noexcept; // заморожені таймери лишаються під тактом
void relaxSupervisors() noexcept;    // PVD геть, BOR на імпульсне опитування

} // namespace coresight

[[nodiscard]] std::expected<void, Fault> initRtc() noexcept;

// Нуль секунд — свідомий випадок: годинника немає, і єдиним джерелом
// пробудження лишається кнопка на WKUP1.
[[nodiscard]] std::expected<Report, Fault> enterStop2(std::chrono::seconds duration) noexcept;

// Зі Standby виходять через скидання, тож успіх сюди не повертається.
[[nodiscard]] std::expected<void, Fault> enterStandby(std::chrono::seconds duration) noexcept;

[[nodiscard]] Stage stage() noexcept;

} // namespace lowpower
