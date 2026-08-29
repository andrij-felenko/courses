#pragma once

#include <concepts>
#include <cstdint>

#include "evse/units.hpp"

namespace evse {

enum class Led : std::uint8_t { Green, Blue, Red };

/* Замок-пустушка для випадків, де взаємного витіснення виробників немає. */
struct NoLock {};

/*
 * Межа порту, виражена концептом, а не віртуальним інтерфейсом: виклик
 * board.setRelay(true) компілюється в одну інструкцію запису в регістр, тоді
 * як таблиця віртуальних методів коштувала б непрямого стрибка на кожній дії
 * автомата й забороняла б вбудовування.
 *
 * IrqLock — RAII-об'єкт критичної секції: конструктор забороняє переривання,
 * деструктор відновлює попередній стан маски.
 */
template <class B>
concept Board = requires(B& b, bool on, Duty duty, Led led) {
    typename B::IrqLock;
    requires std::default_initializable<typename B::IrqLock>;

    { b.now() } -> std::same_as<Millis>;

    { b.setRelay(on) } -> std::same_as<void>;
    { b.relayClosed() } -> std::same_as<bool>;

    { b.setPilotDuty(duty) } -> std::same_as<void>;
    { b.forcePilotLow() } -> std::same_as<void>;
    { b.pilotHigh() } -> std::same_as<Millivolts>;
    { b.pilotLow() } -> std::same_as<Millivolts>;
    { b.pilotPeriod() } -> std::same_as<Micros>;

    { b.leakage() } -> std::same_as<Milliamps>;

    { b.setLed(led, on) } -> std::same_as<void>;
    { b.setLock(on) } -> std::same_as<void>;

    /* Засинання до найближчого переривання: WFI на Cortex-M. */
    { b.waitForInterrupt() } -> std::same_as<void>;
};

} // namespace evse
