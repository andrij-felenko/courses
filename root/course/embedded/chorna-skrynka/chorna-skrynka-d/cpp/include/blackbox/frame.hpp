// frame.hpp — двійковий кадр чорної скриньки: 16 байтів, без жодного тексту.
//
// Тип живе у секції .noinit, тому в ньому НЕМАЄ ініціалізаторів полів і немає
// власного конструктора: усе, що конструктор мав би записати, стартовий код
// затер би саме ту передісторію, заради якої кадр існує. Порожнеча полів тут
// не недбалість, а вимога.
#pragma once

#include <algorithm>
#include <array>
#include <bit>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <span>
#include <type_traits>
#include <variant>

#include "crc16.hpp"

namespace blackbox {

enum class SubsystemId : std::uint8_t {
    Core   = 0x00, // ядро, винятки, планувальник
    Power  = 0x01,
    Nav    = 0x02,
    Motors = 0x03,
    Com    = 0x04,
};

enum class EventId : std::uint8_t {
    None        = 0x00,
    Boot        = 0x01,
    StateChange = 0x02,
    BusError    = 0x03,
    WarnThresh  = 0x04,
    Heartbeat   = 0x05,
    LinkStats   = 0x06,
    CrashPanic  = 0xFF,
};

// --- шість байтів корисного навантаження ------------------------------------
// packed тут не косметика: без нього uint32_t + uint16_t роздувається
// вирівнюванням до восьми байтів і в кадр більше не влазить.

struct [[gnu::packed]] Transition {
    std::uint8_t  previous;  // стан, з якого вийшли
    std::uint8_t  trigger;   // код події-тригера
    std::uint32_t dwell_ms;  // скільки пробули в попередньому стані
};

struct [[gnu::packed]] Health {
    std::uint16_t vbat_mv;
    std::uint16_t load_ma;
    std::uint16_t code; // код помилки шини або порогу
};

struct [[gnu::packed]] FaultContext {
    std::uint32_t pc;     // адреса інструкції, що впала
    std::uint16_t status; // молодші 16 бітів CFSR
};

struct [[gnu::packed]] LinkStats {
    std::uint16_t lost_packets;
    std::int16_t  rssi_dbm;
    std::int16_t  snr_cb; // сотні дБ, щоб лишитися цілим числом
};

template <class T>
concept Payload = std::is_trivially_copyable_v<T> && sizeof(T) <= 6;

static_assert(sizeof(Transition) == 6);
static_assert(sizeof(Health) == 6);
static_assert(sizeof(FaultContext) == 6);
static_assert(sizeof(LinkStats) == 6);

// --- сам кадр ----------------------------------------------------------------

struct alignas(4) BlackBoxEvent {
    std::uint32_t timestamp_ms;
    SubsystemId   subsystem_id;
    EventId       event_id;
    std::uint16_t fsm_state; // молодший байт — стан автомата, старший — прапорці ліній
    std::array<std::byte, 6> payload;
    std::uint16_t crc16;

    // Сума накриває перші 14 байтів — усе, крім самої суми.
    static constexpr std::size_t crc_covered = 14;

    [[nodiscard]] std::span<const std::byte, sizeof(BlackBoxEvent)> raw() const noexcept
    {
        return std::as_bytes(std::span<const BlackBoxEvent, 1>{this, 1});
    }

    void seal() noexcept { crc16 = crc16_ccitt(raw().first(crc_covered)); }

    [[nodiscard]] bool valid() const noexcept
    {
        return crc16 == crc16_ccitt(raw().first(crc_covered));
    }

    template <Payload T>
    void store(const T& value) noexcept
    {
        payload.fill(std::byte{0});
        const auto src = std::bit_cast<std::array<std::byte, sizeof(T)>>(value);
        std::copy(src.begin(), src.end(), payload.begin());
    }

    template <Payload T>
    [[nodiscard]] T load() const noexcept
    {
        std::array<std::byte, sizeof(T)> src{};
        std::copy_n(payload.begin(), sizeof(T), src.begin());
        return std::bit_cast<T>(src);
    }
};

static_assert(sizeof(BlackBoxEvent) == 16, "кадр мусить бути рівно 16 байтів");
static_assert(alignof(BlackBoxEvent) == 4, "Cortex-M0+ не читає uint32 за непарною адресою");
static_assert(std::is_trivially_copyable_v<BlackBoxEvent>);
static_assert(std::is_trivially_default_constructible_v<BlackBoxEvent>,
              ".noinit не терпить конструктора: він затер би передісторію");

// --- розбір навантаження на хості й у звіті після рестарту -------------------
// Тег лежить в event_id, тож замість void* із switch за тегом віддаємо variant:
// компілятор сам стежить, що кожну гілку розібрано.

using DecodedPayload = std::variant<std::monostate, Transition, Health, FaultContext, LinkStats>;

[[nodiscard]] inline DecodedPayload decode(const BlackBoxEvent& ev) noexcept
{
    switch (ev.event_id) {
    case EventId::StateChange:
        return ev.load<Transition>();
    case EventId::Boot:
    case EventId::BusError:
    case EventId::WarnThresh:
    case EventId::Heartbeat:
        return ev.load<Health>();
    case EventId::CrashPanic:
        return ev.load<FaultContext>();
    case EventId::LinkStats:
        return ev.load<LinkStats>();
    case EventId::None:
    default:
        return std::monostate{}; // порожній слот або кадр чужої схеми
    }
}

} // namespace blackbox
