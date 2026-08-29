// protocol.hpp — той самий 16-байтовий контракт, але без пакованих структур.
//
// У C кадр — це структура під `#pragma pack`, і читач мусить пам'ятати про
// вирівнювання й порядок байтів. Тут кадр — просто масив байтів, а поля
// кладуться й читаються явно: жодного reinterpret_cast, жодного HardFault
// на невирівняному доступі, порядок байтів видно в самому коді.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string_view>
#include <variant>
#include <vector>

namespace field {

inline constexpr std::size_t kFrameSize = 16;
inline constexpr std::uint8_t kMagic = 0xAA;

using Wire = std::array<std::byte, kFrameSize>;
using WireView = std::span<const std::byte, kFrameSize>;

enum class FrameType : std::uint8_t { Telemetry = 0x01, Command = 0x02, Ack = 0x03 };
enum class CommandId : std::uint8_t { SetRelay = 0x10 };
enum class AckStatus : std::uint8_t { Ok = 0x00, UnknownCommand = 0x01, BadValue = 0x02 };

struct Flags {
    bool relay_on{false};
    bool sensor_fault{false};

    [[nodiscard]] constexpr std::uint8_t bits() const noexcept {
        return static_cast<std::uint8_t>((relay_on ? 0x01 : 0x00) | (sensor_fault ? 0x02 : 0x00));
    }
    [[nodiscard]] static constexpr Flags from_bits(std::uint8_t b) noexcept {
        return Flags{(b & 0x01) != 0, (b & 0x02) != 0};
    }
};

struct Telemetry {
    std::uint16_t node_id{};
    std::uint32_t seq{};
    std::int16_t  temp_c100{};   // сотні градуса: 2235 == 22.35 °C
    std::uint16_t battery_mv{};
    Flags         flags{};
};

struct Command {
    std::uint16_t node_id{};
    std::uint32_t seq{};
    CommandId     id{CommandId::SetRelay};
    std::uint8_t  value{};
};

struct Ack {
    std::uint16_t node_id{};
    std::uint32_t seq{};        // луна номера команди
    std::uint8_t  cmd_id{};     // сирий код: квитанція можлива й на невідому команду
    AckStatus     status{AckStatus::Ok};
    Flags         flags{};
};

using Frame = std::variant<Telemetry, Command, Ack>;

enum class DecodeError { BadMagic, BadCrc, UnknownType };
[[nodiscard]] std::string_view describe(DecodeError err) noexcept;

[[nodiscard]] std::uint16_t crc16_ccitt(std::span<const std::byte> data) noexcept;

[[nodiscard]] Wire encode(const Telemetry& t) noexcept;
[[nodiscard]] Wire encode(const Command& c) noexcept;
[[nodiscard]] Wire encode(const Ack& a) noexcept;

// Помилку повертаємо значенням, а не -1 з errno: тип каже, що саме не так.
[[nodiscard]] std::expected<Frame, DecodeError> decode(WireView wire) noexcept;

// Магія на місці й CRC зійшлася — критерій, за яким кадрувальник відрізняє
// справжню межу кадру від випадкового 0xAA у сміттєвих байтах.
[[nodiscard]] bool looks_valid(WireView wire) noexcept;

// Кадрувальник байтового потоку: ковзне вікно з ресинхронізацією.
// Живе поруч із кодеком, бо це така сама частина контракту, як розкладка полів.
class StreamFramer {
public:
    static constexpr std::size_t kCapacity = 4 * kFrameSize;

    void feed(std::span<const std::byte> chunk);
    [[nodiscard]] std::optional<Wire> next();

    [[nodiscard]] std::size_t resync_drops() const noexcept { return drops_; }
    [[nodiscard]] std::size_t buffered() const noexcept { return buf_.size(); }

private:
    void drop_front(std::size_t count);

    std::vector<std::byte> buf_;
    std::size_t drops_{0};
};

}  // namespace field
