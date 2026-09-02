// Контракт валідації: чого ми вимагаємо від драйвера шини, чим описуємо
// цільовий кристал і які числа несе діагностичний звіт.
//
// Драйвер задано концептом, а не віртуальним інтерфейсом: на етапі оживлення
// шина відома на етапі компіляції, і таблиця віртуальних викликів тут була б
// платою ні за що.
#pragma once

#include <chrono>
#include <concepts>
#include <cstdint>
#include <expected>
#include <optional>
#include <string_view>

namespace bringup {

using Byte = std::uint8_t;
using Register = std::uint8_t;

// Чому кадр не відбувся на фізичному рівні. Це ще не діагноз — лише вхідні
// дані для нього; прочитаний байт 0x00 чи 0xFF сюди не належить.
enum class BusError : std::uint8_t {
    NoAcknowledge,   // слейв не притиснув SDA на дев'ятому такті
    Timeout,         // периферія ведучого не дочекалася завершення кадру
    ArbitrationLost  // лінію тримає хтось інший
};

template <class T>
concept BusDriver = requires(T& bus, Register reg, Byte value, std::chrono::milliseconds pause) {
    { bus.read(reg) } -> std::same_as<std::expected<Byte, BusError>>;
    { bus.write(reg, value) } -> std::same_as<std::expected<void, BusError>>;
    { bus.wait(pause) } -> std::same_as<void>;
};

// Паспорт чипа з даташита. power_on_delay — розділ Power-On Reset Time,
// scratchpad_reg — безпечна вісімка тригерів для тесту запису.
struct DeviceDescriptor {
    std::string_view name;
    Register id_reg{};
    Byte expected_id{};
    Register scratchpad_reg{};
    std::chrono::milliseconds power_on_delay{15};
    std::chrono::milliseconds retry_delay{2};
    unsigned read_attempts{5};
};

enum class Fault : std::uint8_t {
    NoAnswer,            // NACK або тайм-аут: відповіді немає взагалі
    BusStuckHigh,        // 0xFF: весь кадр читалася підтяжка
    BusStuckLow,         // 0x00: весь кадр лінія була на землі
    BitShift,            // ID зсунуто рівно на розряд: збита фаза, а не пайка
    ForeignId,           // відповів чужий кремній
    WritePathDead,       // читання живе, запис до кристала не доходить
    ScratchpadCorrupted  // запис доходить, але біти спотворюються
};

enum class Shift : std::uint8_t {
    None,
    Left,   // прийшло (expected << 1): ведучий стробує на пів такту пізніше
    Right   // прийшло (expected >> 1): ведучий стробує на пів такту раніше
};

struct BitDefects {
    Byte stuck_high{};  // читається одиницею попри записаний нуль
    Byte stuck_low{};   // читається нулем попри записану одиницю
    Byte bridged{};     // сусідні розряди, злиті між собою
};

struct Failure {
    Fault fault{};
    Byte received_id{};
    Shift shift{Shift::None};
    Byte written{};
    Byte readback{};
    BitDefects bits{};
    unsigned attempts{};
    std::optional<BusError> bus_error{};
};

// Те, заради чого все затівалося: підтверджений паспорт живого кристала.
struct Passport {
    Byte id{};
    unsigned attempts{};
    bool scratchpad_verified{};
};

}  // namespace bringup
