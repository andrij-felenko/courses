// recorder.hpp — рівень L1 бортового реєстратора: кільце кадрів у .noinit.
//
// Запис — константний час, без купи, без блокувальних примітивів RTOS, тому
// кликати можна звідусіль, включно з обробником HardFault.
#pragma once

#include <concepts>
#include <cstddef>
#include <cstdint>
#include <span>
#include <type_traits>

#include "frame.hpp"

namespace blackbox {

// Монотонні мілісекунди від старту ядра. Визначає платформа; мусить бути
// читанням лічильника, а не чимось, що блокується.
[[nodiscard]] std::uint32_t uptime_ms() noexcept;

// Критична секція як RAII: PRIMASK зберігається й відновлюється, а не
// вмикається наосліп. Реєстратор кличуть із переривання, де переривання вже
// могли бути заборонені, і сліпе cpsie i відкрило б вкладене переривання
// посеред запису кадру.
class InterruptGuard {
public:
    InterruptGuard() noexcept : saved_{lock()} {}
    ~InterruptGuard() noexcept { unlock(saved_); }

    InterruptGuard(const InterruptGuard&) = delete;
    InterruptGuard& operator=(const InterruptGuard&) = delete;

private:
    [[nodiscard]] static std::uint32_t lock() noexcept
    {
#if defined(__ARM_ARCH)
        std::uint32_t primask;
        __asm volatile("mrs %0, primask" : "=r"(primask));
        __asm volatile("cpsid i" ::: "memory");
        return primask;
#else
        // Хостова збірка перевірок: переривань немає, лишається бар'єр
        // компілятора, щоб порядок звернень до кільця не перекроїли.
        __asm volatile("" ::: "memory");
        return 0u;
#endif
    }

    static void unlock([[maybe_unused]] std::uint32_t primask) noexcept
    {
#if defined(__ARM_ARCH)
        if (primask == 0u) {
            __asm volatile("cpsie i" ::: "memory");
        }
#else
        __asm volatile("" ::: "memory");
#endif
    }

    std::uint32_t saved_;
};

template <std::size_t Capacity = 256, std::uint8_t PostTrigger = 8>
class Recorder {
    static_assert(Capacity > 0);

public:
    static constexpr std::uint32_t magic_value = 0x424F5831u; // 'BOX1'
    static constexpr std::uint16_t schema_version = 1;

    // Заголовок навмисно розділено. Перші 16 байтів міняються рідко — тільки
    // на старті й на аварії, — і саме їх накриває crc. Лічильники нижче
    // міняються на КОЖНОМУ записі; тримати їх під сумою означало б рахувати
    // CRC заголовка щоразу, а це дорожче за сам запис кадру. Їхню осудність
    // перевіряємо діапазоном.
    struct alignas(4) Header {
        std::uint32_t magic;
        std::uint16_t schema;
        std::uint16_t capacity;
        std::uint32_t boot_count;
        std::uint32_t crash_count;
        std::uint16_t crc; // CRC-16 над magic..crash_count
        std::uint16_t reserved;
        std::uint32_t sequence; // скільки кадрів записано за всю історію
        std::uint32_t head;     // куди ляже наступний кадр
        std::uint8_t  frozen;
        std::uint8_t  post_trigger_left;
        std::uint16_t padding;

        static constexpr std::size_t crc_covered = 16;
    };

    // Викликається один раз якнайраніше в main(), ДО ініціалізації периферії.
    void init(std::uint8_t reset_cause) noexcept
    {
        if (header_intact()) {
            header_.boot_count++; // теплий старт: живлення SRAM не зникало
            seal_header();
        } else {
            cold_start();
        }

        // Заморожене кільце НЕ розморожуємо: там лежить аварійний знімок, і
        // його має спершу забрати прошивка, а вже потім покликати release().
        if (header_.frozen == 0u) {
            log(SubsystemId::Core, EventId::Boot,
                static_cast<std::uint16_t>(header_.boot_count),
                Health{.vbat_mv = 0, .load_ma = 0, .code = reset_cause});
        }
    }

    template <Payload T>
    void log(SubsystemId subsys, EventId evt, std::uint16_t fsm_state, const T& body) noexcept
    {
        const InterruptGuard guard;
        if (header_.frozen != 0u) {
            return;
        }
        BlackBoxEvent& slot = reserve();
        slot.payload.fill(std::byte{0});
        slot.store(body);
        finish(slot, subsys, evt, fsm_state);
    }

    void log(SubsystemId subsys, EventId evt, std::uint16_t fsm_state = 0) noexcept
    {
        const InterruptGuard guard;
        if (header_.frozen != 0u) {
            return;
        }
        BlackBoxEvent& slot = reserve();
        slot.payload.fill(std::byte{0});
        finish(slot, subsys, evt, fsm_state);
    }

    void state_change(SubsystemId subsys, std::uint8_t previous, std::uint8_t next,
                      std::uint8_t hw_flags, std::uint8_t trigger, std::uint32_t dwell_ms) noexcept
    {
        const auto fsm = static_cast<std::uint16_t>((hw_flags << 8) | next);
        log(subsys, EventId::StateChange, fsm,
            Transition{.previous = previous, .trigger = trigger, .dwell_ms = dwell_ms});
    }

    // Аварійний слід: кличуть із HardFault_Handler або з обробника PVD.
    void panic(std::uint8_t reason, const FaultContext& fault) noexcept
    {
        const InterruptGuard guard;

        // Якщо кільце вже заморожене, це або друга аварія поспіль, або звіт
        // про попередню ще не забрали: перетирати старший доказ не можна.
        if (header_.frozen != 0u) {
            return;
        }

        BlackBoxEvent& slot = reserve();
        slot.payload.fill(std::byte{0});
        slot.store(fault);
        finish(slot, SubsystemId::Core, EventId::CrashPanic, reason);

        header_.crash_count++;
        if constexpr (PostTrigger == 0) {
            header_.frozen = 1u;
        }
        seal_header(); // crash_count входить у накриту сумою частину
    }

    void freeze() noexcept // спинити кільце негайно, перед скиданням у L2
    {
        const InterruptGuard guard;
        header_.frozen = 1u;
        header_.post_trigger_left = 0u;
    }

    void release() noexcept // звіт віддано — знову писати
    {
        const InterruptGuard guard;
        header_.frozen = 0u;
        header_.post_trigger_left = 0u;
    }

    [[nodiscard]] bool history_valid() const noexcept
    {
        return header_intact() && header_.sequence != 0u;
    }

    [[nodiscard]] bool crash_pending() const noexcept
    {
        return header_intact() && header_.frozen != 0u && header_.crash_count != 0u;
    }

    // Обхід кільця в хронологічному порядку — від найстарішого вцілілого кадру
    // до найновішого. Другим аргументом іде ознака цілісності: недозаписаний
    // кадр показують із позначкою, а не викидають мовчки.
    template <class Fn>
        requires std::invocable<Fn, const BlackBoxEvent&, bool>
    std::size_t replay(Fn&& visit) const noexcept
    {
        if (!history_valid()) {
            return 0;
        }

        const bool wrapped = header_.sequence >= Capacity;
        const std::size_t total = wrapped ? Capacity : static_cast<std::size_t>(header_.sequence);
        const std::size_t start = wrapped ? static_cast<std::size_t>(header_.head) : 0u;

        for (std::size_t i = 0; i < total; ++i) {
            const BlackBoxEvent& ev = events_[(start + i) % Capacity];
            visit(ev, ev.valid());
        }
        return total;
    }

    [[nodiscard]] const Header& header() const noexcept { return header_; }

    // Суцільний блок для скидання у FRAM/Flash одним потоком SPI.
    [[nodiscard]] std::span<const std::byte> raw_image() const noexcept
    {
        return std::as_bytes(std::span<const Recorder, 1>{this, 1});
    }

private:
    // Викликається лише з-під InterruptGuard.
    [[nodiscard]] BlackBoxEvent& reserve() noexcept
    {
        BlackBoxEvent& slot = events_[header_.head];
        header_.head = static_cast<std::uint32_t>((header_.head + 1u) % Capacity);
        header_.sequence++; // переповнення за 2^32 записів свідомо ігноруємо:
                            // при 20 подіях/с це 6.8 року неперервної роботи
        return slot;
    }

    void finish(BlackBoxEvent& slot, SubsystemId subsys, EventId evt, std::uint16_t fsm) noexcept
    {
        slot.timestamp_ms = uptime_ms();
        slot.subsystem_id = subsys;
        slot.event_id = evt;
        slot.fsm_state = fsm;
        slot.seal();

        // Пост-тригерне вікно: після аварії дописуємо ще кілька кадрів — саме
        // вони показують, ЯК система звалилася, — і замикаємо кільце.
        if (header_.post_trigger_left != 0u) {
            if (--header_.post_trigger_left == 0u) {
                header_.frozen = 1u;
            }
        } else if (slot.event_id == EventId::CrashPanic) {
            header_.post_trigger_left = PostTrigger;
        }
    }

    [[nodiscard]] std::uint16_t header_checksum() const noexcept
    {
        const auto bytes = std::as_bytes(std::span<const Header, 1>{&header_, 1});
        return crc16_ccitt(bytes.first(Header::crc_covered));
    }

    void seal_header() noexcept { header_.crc = header_checksum(); }

    [[nodiscard]] bool header_intact() const noexcept
    {
        return header_.magic == magic_value
            && header_.schema == schema_version
            && header_.capacity == Capacity
            && header_.crc == header_checksum()
            && header_.head < Capacity
            && header_.post_trigger_left <= PostTrigger;
    }

    void cold_start() noexcept
    {
        header_ = Header{};
        header_.magic = magic_value;
        header_.schema = schema_version;
        header_.capacity = Capacity;
        header_.boot_count = 1u;
        events_.fill(BlackBoxEvent{});
        seal_header();
    }

    Header header_;
    std::array<BlackBoxEvent, Capacity> events_;
};

static_assert(std::is_trivially_default_constructible_v<Recorder<>>,
              "конструктор поїхав би в стартовий код і затер би .noinit");

// Єдиний примірник поза .data і .bss: стартовий код (crt0 / Reset_Handler)
// його не займає, тож передісторія переживає скидання. Секцію .noinit мусить
// оголосити скрипт компонувальника — без цього змінна мовчки поїде в .bss і
// кожне скидання стиратиме буфер.
[[gnu::section(".noinit")]] inline Recorder<256> recorder;

} // namespace blackbox
