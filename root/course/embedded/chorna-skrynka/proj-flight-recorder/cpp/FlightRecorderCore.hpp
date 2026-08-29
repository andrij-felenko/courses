// FlightRecorderCore.hpp — кільцевий реєстратор подій (C++20).
// Двійкова розкладка кадру й тому збігається з версією на C: обидві прошивки
// віддають файл, який читає той самий декодер py/decode_blackbox.py.
#pragma once

#include "McuPort.hpp"

#include <array>
#include <atomic>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <span>
#include <type_traits>

namespace embedded::diagnostics {

enum class Subsystem : std::uint8_t {
    Core     = 0x00,
    Power    = 0x01,
    Nav      = 0x02,
    Actuator = 0x03,
    Comm     = 0x04
};

enum class EventCode : std::uint8_t {
    None          = 0x00,
    BootOk        = 0x01,
    FsmTransition = 0x02,
    BusNack       = 0x03,
    BusTimeout    = 0x04,
    VoltageWarn   = 0x05,
    TempCritical  = 0x06,
    FaultContext  = 0xFC, // LR повернення + номер винятку IPSR
    FaultAddr     = 0xFD, // MMFAR/BFAR + прапорці дійсності
    HardFault     = 0xFE, // PC збою + молодша половина CFSR
    PanicAbort    = 0xFF  // програмна паніка
};

enum class BootKind : std::uint8_t {
    Cold  = 0, // пам'ять не пережила знеструмлення
    Warm  = 1, // тепле скидання, хронологія ціла
    Crash = 2  // попередня сесія впала, буфер заморожено
};

// Що показало ядро в момент винятку.
struct FaultInfo {
    std::uint32_t pc{};
    std::uint32_t lr{};
    std::uint32_t psr{};
    std::uint32_t exc_return{};
    std::uint32_t cfsr{};
    std::uint32_t hfsr{};
    std::uint32_t fault_addr{};
    std::uint8_t  addr_valid{}; // біт0 — MMARVALID, біт1 — BFARVALID
};

inline constexpr std::size_t kPayloadSize = 6;

[[nodiscard]] constexpr std::uint16_t crc16_ccitt(std::span<const std::byte> data) noexcept {
    std::uint16_t crc = 0xFFFFU;
    for (const std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint8_t>(b)) << 8;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000U) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021U)
                                  : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

// 16 байтів рівно, без атрибута packed: поля вже стоять на своїх природних
// межах, тож і діри вирівнювання не з'являються, і непарного доступу на
// Cortex-M0+ не буде. Розкладку стереже static_assert нижче.
struct alignas(4) EventFrame {
    std::uint32_t timestamp_ms{};
    Subsystem     subsystem{Subsystem::Core};
    EventCode     event_code{EventCode::None};
    std::uint16_t fsm_state{};
    std::array<std::uint8_t, kPayloadSize> payload{};
    std::uint16_t crc16{};

    [[nodiscard]] std::span<const std::byte> covered_bytes() const noexcept {
        return {reinterpret_cast<const std::byte*>(this), 14}; // усе, крім самого CRC
    }

    void seal() noexcept { crc16 = crc16_ccitt(covered_bytes()); }

    [[nodiscard]] bool valid() const noexcept { return crc16 == crc16_ccitt(covered_bytes()); }
};

static_assert(sizeof(EventFrame) == 16, "кадр мусить лишатися 16-байтним");
static_assert(std::is_trivially_copyable_v<EventFrame>);
static_assert(offsetof(EventFrame, payload) == 8);
static_assert(offsetof(EventFrame, crc16) == 14);

template <std::size_t Capacity = 256>
    requires(Capacity >= 16 && std::has_single_bit(Capacity))
class FlightRecorderEngine {
public:
    static constexpr std::uint32_t kMagic = 0x424F5831U; // 'BOX1'
    static constexpr std::uint32_t kMask  = Capacity - 1U;

    // Розкладка тому: заголовок 28 байтів + кадри. header_crc покриває лише
    // незмінні перші 16 байтів — sequence росте на кожному записі, і рахувати
    // CRC заголовка щоразу коштувало б більше за сам запис.
    struct Volume {
        std::uint32_t magic{};
        std::uint32_t boot_counter{};
        std::uint32_t crash_counter{};
        std::uint32_t capacity{};
        std::atomic<std::uint32_t> sequence{};  // вільно росте, слот = sequence & kMask
        std::atomic<std::uint32_t> frozen{};
        std::uint16_t header_crc{};
        std::uint16_t reserved{};
        std::array<EventFrame, Capacity> frames{};
    };

    BootKind init() noexcept {
        if (!header_is_sane()) {
            raise_fresh_volume();
            return BootKind::Cold;
        }
        ++volume_.boot_counter;
        seal_header();
        // Після аварії буфер лишається замороженим, доки застосунок не забере
        // знімок: інакше перші ж записи нового запуску затруть катастрофу.
        return volume_.frozen.load(std::memory_order_acquire) != 0U ? BootKind::Crash : BootKind::Warm;
    }

    void release() noexcept { volume_.frozen.store(0U, std::memory_order_release); }

    void log(Subsystem subsystem, EventCode code, std::uint16_t fsm = 0,
             std::span<const std::byte> payload = {}) noexcept {
        if (volume_.frozen.load(std::memory_order_relaxed) != 0U) {
            return;
        }
        // Захоплення слота одним атомарним інкрементом: працює і з переривання,
        // і з другого ядра SoC, де вимкнення переривань чужому ядру не указ.
        const std::uint32_t ticket = volume_.sequence.fetch_add(1, std::memory_order_acq_rel);
        write_frame(volume_.frames[ticket & kMask], subsystem, code, fsm, payload);
    }

    // Тривіальний вантаж (структура телеметрії, код помилки шини) кладеться
    // байтами без ручного memcpy на боці виклику.
    template <typename T>
        requires(std::is_trivially_copyable_v<T> && sizeof(T) <= kPayloadSize)
    void log(Subsystem subsystem, EventCode code, std::uint16_t fsm, const T& value) noexcept {
        log(subsystem, code, fsm, std::as_bytes(std::span<const T, 1>{&value, 1}));
    }

    // Три кадри: разом вони вміщують увесь стан збою, який шість байтів
    // одного кадру втримати не можуть.
    void panic(const FaultInfo& fault) noexcept {
        mcu::IrqLock lock;
        lock.keep_locked();

        if (!header_is_sane()) {
            raise_fresh_volume(); // виняток стався до init() або рознесло заголовок
        }

        std::array<std::uint8_t, kPayloadSize> payload{};
        pack(payload, fault.pc, static_cast<std::uint16_t>(fault.cfsr & 0xFFFFU));
        panic_frame(EventCode::HardFault, static_cast<std::uint16_t>(fault.cfsr >> 16), payload);

        pack(payload, fault.fault_addr, fault.addr_valid);
        panic_frame(EventCode::FaultAddr, pack_hfsr(fault.hfsr), payload);

        pack(payload, fault.lr, static_cast<std::uint16_t>(fault.psr & 0x1FFU));
        panic_frame(EventCode::FaultContext, static_cast<std::uint16_t>(fault.exc_return & 0xFFFFU), payload);

        freeze();
    }

    void panic_abort(std::uint16_t reason, std::uint32_t context) noexcept {
        mcu::IrqLock lock;
        lock.keep_locked();

        if (!header_is_sane()) {
            raise_fresh_volume();
        }
        std::array<std::uint8_t, kPayloadSize> payload{};
        pack(payload, context, std::uint16_t{0});
        panic_frame(EventCode::PanicAbort, reason, payload);
        freeze();
    }

    [[nodiscard]] bool has_crash_dump() const noexcept {
        return header_is_sane() && volume_.crash_counter > 0U &&
               volume_.frozen.load(std::memory_order_relaxed) != 0U;
    }

    [[nodiscard]] std::span<const EventFrame> frames() const noexcept { return volume_.frames; }

    // Сирі байти тому — рівно те, що піде в енергонезалежний носій.
    [[nodiscard]] std::span<const std::byte> raw_image() const noexcept {
        return {reinterpret_cast<const std::byte*>(&volume_), sizeof(Volume)};
    }

    [[nodiscard]] std::uint32_t boot_count() const noexcept { return volume_.boot_counter; }
    [[nodiscard]] std::uint32_t crash_count() const noexcept { return volume_.crash_counter; }

private:
    static constexpr std::size_t kHeaderCrcLen = 16; // magic, boot, crash, capacity

    void write_frame(EventFrame& slot, Subsystem subsystem, EventCode code,
                     std::uint16_t fsm, std::span<const std::byte> payload) noexcept {
        slot.timestamp_ms = mcu::uptime_ms();
        slot.subsystem    = subsystem;
        slot.event_code   = code;
        slot.fsm_state    = fsm;
        slot.payload.fill(0);

        const std::size_t take = payload.size() < kPayloadSize ? payload.size() : kPayloadSize;
        for (std::size_t i = 0; i < take; ++i) {
            slot.payload[i] = std::to_integer<std::uint8_t>(payload[i]);
        }
        // CRC ставимо останнім: доки він не збігається, декодер вважає кадр
        // недописаним — саме так виглядає слот, що його застало вимкнення.
        slot.seal();
    }

    void panic_frame(EventCode code, std::uint16_t fsm,
                     const std::array<std::uint8_t, kPayloadSize>& payload) noexcept {
        const std::uint32_t ticket = volume_.sequence.fetch_add(1, std::memory_order_acq_rel);
        write_frame(volume_.frames[ticket & kMask], Subsystem::Core, code, fsm,
                    std::as_bytes(std::span{payload}));
    }

    void freeze() noexcept {
        ++volume_.crash_counter;
        volume_.frozen.store(1U, std::memory_order_release);
        seal_header();
    }

    // HFSR стиснутий у три біти: 0 — VECTTBL (збій читання таблиці векторів),
    // 1 — FORCED (налаштований виняток ескалювали в HardFault), 2 — DEBUGEVT.
    [[nodiscard]] static constexpr std::uint16_t pack_hfsr(std::uint32_t hfsr) noexcept {
        std::uint16_t flags = 0;
        if ((hfsr & (1U << 1)) != 0U)  { flags |= 0x01U; }
        if ((hfsr & (1U << 30)) != 0U) { flags |= 0x02U; }
        if ((hfsr & (1U << 31)) != 0U) { flags |= 0x04U; }
        return flags;
    }

    static void pack(std::array<std::uint8_t, kPayloadSize>& out, std::uint32_t word,
                     std::uint16_t half) noexcept {
        out[0] = static_cast<std::uint8_t>(word & 0xFFU);
        out[1] = static_cast<std::uint8_t>((word >> 8) & 0xFFU);
        out[2] = static_cast<std::uint8_t>((word >> 16) & 0xFFU);
        out[3] = static_cast<std::uint8_t>((word >> 24) & 0xFFU);
        out[4] = static_cast<std::uint8_t>(half & 0xFFU);
        out[5] = static_cast<std::uint8_t>((half >> 8) & 0xFFU);
    }

    [[nodiscard]] std::span<const std::byte> header_bytes() const noexcept {
        return {reinterpret_cast<const std::byte*>(&volume_), kHeaderCrcLen};
    }

    void seal_header() noexcept { volume_.header_crc = crc16_ccitt(header_bytes()); }

    [[nodiscard]] bool header_is_sane() const noexcept {
        return volume_.magic == kMagic && volume_.capacity == Capacity &&
               volume_.header_crc == crc16_ccitt(header_bytes());
    }

    void raise_fresh_volume() noexcept {
        std::memset(static_cast<void*>(&volume_), 0, sizeof(Volume));
        volume_.magic        = kMagic;
        volume_.capacity     = Capacity;
        volume_.boot_counter = 1;
        seal_header();
    }

    Volume volume_{};
};

using Recorder = FlightRecorderEngine<256>;

static_assert(sizeof(Recorder::Volume) == 28 + 256 * sizeof(EventFrame),
              "заголовок тому мусить лишатися 28-байтним — на нього спирається декодер");
static_assert(offsetof(Recorder::Volume, frames) == 28);

// Єдиний екземпляр у секції .noinit; визначено у FlightRecorderCore.cpp.
[[nodiscard]] Recorder& recorder() noexcept;

} // namespace embedded::diagnostics
