// fault_log.hpp — причина перезапуску й журнал аварій у резервному домені RTC.
//
// Двадцять слів, які переживають скидання й короткий провал живлення, —
// уся пам'ять, що лишається після Brownout-перезапуску. Перше, що робить
// польовий прилад після старту, — з'ясовує, ЧОМУ він стартував: без цього
// нескінченний цикл перезавантажень ззовні виглядає як нормальна робота.
#pragma once

#include <chrono>
#include <cstdint>
#include <span>
#include <string_view>

namespace field {

enum class ResetCause : std::uint8_t {
    Unknown = 0,
    PowerOn,    // штатне ввімкнення
    Pin,        // зовнішня кнопка NRST
    Brownout,   // просадка шини нижче порогу BOR
    Watchdog,   // зависання: сторожовий таймер не нагодували
    HardFault,  // виняток процесора, зафіксований обробником
    Software,   // навмисний перезапуск із коду
    LowPower    // збій виходу з режиму зниженого споживання
};

[[nodiscard]] std::string_view name(ResetCause cause) noexcept;

struct Event {
    ResetCause cause{ResetCause::Unknown};
    std::int16_t temperatureC{};      // округлено до градуса, −64…+191
    std::uint16_t voltageMv{};        // крок 16 мВ
    std::chrono::seconds uptime{};    // стеля 8191 с
};

struct Counters {
    std::uint16_t boots{};
    std::uint16_t brownouts{};
    std::uint16_t watchdogs{};
    std::uint16_t busRecoveries{};
};

struct BootReport {
    ResetCause cause{ResetCause::Unknown};
    bool historyLost{};        // домен був порожній: попередню історію втрачено
    std::uint32_t faultPc{};   // молодші 24 біти адреси, де впав HardFault
    Counters counters{};

    // Чи входити одразу в обережний режим. Один сторожовий перезапуск за
    // все життя приладу — випадковість; три і більше — зависання
    // повторюване, і повна частота приведе нас сюди ж.
    [[nodiscard]] bool needsSafeStart() const noexcept {
        return cause == ResetCause::Brownout || cause == ResetCause::HardFault ||
               counters.watchdogs >= 3;
    }
};

// Розкладка двадцяти слів BKP0R..BKP19R:
//   [0]      сигнатура (16 біт) | лічильник записів (8) | голова кільця (8)
//   [1]      старти (16) | Brownout-скидання (16)
//   [2]      скидання сторожем (16) | порятунки шини (16)
//   [3]      слід HardFault: 0xFA у старшому байті | молодші 24 біти PC
//   [4..19]  шістнадцять подій, по одному слову на подію
class FaultLog {
public:
    static constexpr std::uint8_t kSlots = 16;

    // Читає прапори заліза, розмічає домен за потреби, оновлює лічильники.
    // Викликати один раз, на самому початку main().
    [[nodiscard]] BootReport open();

    void append(ResetCause cause, std::int16_t temperatureC, std::uint16_t voltageMv,
                std::chrono::milliseconds uptime);

    // Заповнює out від найсвіжішої події до найстарішої; повертає скільки віддав.
    [[nodiscard]] std::size_t readRecent(std::span<Event> out) const;

    void noteBusRecovery();
};

}  // namespace field

// Викликається з голого обробника винятку; описаний у fault_log.cpp.
extern "C" [[noreturn]] void fieldRecordHardFault(const std::uint32_t* frame);
