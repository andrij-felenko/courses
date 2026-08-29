#pragma once

#include <cstdint>
#include <type_traits>
#include <variant>

#include "evse/cp_line.hpp"
#include "evse/units.hpp"

namespace evse {

enum class TimerId : std::uint8_t {
    AuthWindow = 0,     /* вікно на прикладання картки */
    ContactorSettle,    /* перехідні процеси після замикання контактора */
    FaultLockout,       /* мінімальне утримання в аварії */
    Count
};

/*
 * Кожна подія — окремий тип, а не число з полем «параметр на всі випадки».
 * Через це компілятор сам стежить, щоб обробник Overcurrent читав ампери, а не
 * мілівольти, і жодне поле не лишається «іноді осмисленим».
 */
struct Tick10ms {};
struct CpChanged     { CpClass level{CpClass::A}; };
struct RfidTag       { std::uint32_t id{}; };
struct EmergencyStop {};
struct Overcurrent   { Amperes peak{}; };
struct LeakageTrip   { Milliamps leak{}; };
struct Expired       { TimerId id{}; };
struct ResetButton   {};
struct QueueOverflow {};

using Event = std::variant<Tick10ms, CpChanged, RfidTag, EmergencyStop, Overcurrent,
                           LeakageTrip, Expired, ResetButton, QueueOverflow>;

/* Подія з міткою часу — саме вона лежить у кільцевій черзі. */
struct Stamped {
    Event  event{};
    Millis at{};
};

/*
 * Запис мусить копіюватися побайтово: його заповнює обробник переривання, і
 * жодних конструкторів, деструкторів чи виділення пам'яті там бути не може.
 */
static_assert(std::is_trivially_copyable_v<Stamped>,
              "подія має копіюватися побайтово, інакше її не можна класти в чергу з ISR");
static_assert(sizeof(Stamped) <= 16, "запис події роздувся — перевірте поля");

} // namespace evse
