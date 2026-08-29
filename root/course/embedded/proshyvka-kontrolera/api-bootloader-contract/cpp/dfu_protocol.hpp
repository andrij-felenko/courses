#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <variant>

namespace fc::dfu {

using namespace std::chrono_literals;

// Класові запити USB DFU 1.1 — поле bRequest пакета SETUP.
enum class Request : std::uint8_t {
    Detach    = 0x00,
    Dnload    = 0x01,
    Upload    = 0x02,
    GetStatus = 0x03,
    ClrStatus = 0x04,
    GetState  = 0x05,
    Abort     = 0x06,
};

enum class State : std::uint8_t {
    AppIdle            = 0x00,
    AppDetach          = 0x01,
    DfuIdle            = 0x02,
    DnloadSync         = 0x03,
    DnBusy             = 0x04,
    DnloadIdle         = 0x05,
    ManifestSync       = 0x06,
    Manifest           = 0x07,
    ManifestWaitReset  = 0x08,
    UploadIdle         = 0x09,
    Error              = 0x0A,
};

enum class Status : std::uint8_t {
    Ok             = 0x00,
    ErrTarget      = 0x01,
    ErrFile        = 0x02,
    ErrWrite       = 0x03,
    ErrErase       = 0x04,
    ErrCheckErased = 0x05,
    ErrProg        = 0x06,
    ErrVerify      = 0x07,
    ErrAddress     = 0x08,
    ErrNotDone     = 0x09,
    ErrFirmware    = 0x0A,
    ErrVendor      = 0x0B,
    ErrUsbr        = 0x0C,
    ErrPor         = 0x0D,
    ErrUnknown     = 0x0E,
    ErrStalledPkt  = 0x0F,
};

inline constexpr std::size_t kTransferSize = 1024;

// Функціональний дескриптор DFU. Пакованої структури не тримаємо: на дріт
// байти кладе to_bytes(), і порядок там явний, а не як склалось у компілятора.
struct FunctionalDescriptor {
    std::uint8_t attributes = 0x0B;  // CanDnload | CanUpload | WillDetach
    std::chrono::milliseconds detach_timeout = 250ms;
    std::uint16_t transfer_size = static_cast<std::uint16_t>(kTransferSize);
    std::uint16_t bcd_version = 0x0110;  // DFU 1.1

    static constexpr std::uint8_t kDescriptorType = 0x21;
    static constexpr std::size_t kLength = 9;

    [[nodiscard]] std::array<std::byte, kLength> to_bytes() const noexcept;
};

inline constexpr FunctionalDescriptor kDefaultDescriptor{};

// Відповідь на DFU_GETSTATUS — шість байтів.
struct StatusResponse {
    Status status = Status::Ok;
    std::chrono::milliseconds poll_timeout = 0ms;
    State state = State::DfuIdle;
    std::uint8_t string_index = 0;

    static constexpr std::size_t kLength = 6;

    [[nodiscard]] std::array<std::byte, kLength> to_bytes() const noexcept;
};

// Команди розширення ST DfuSe — тіло DFU_DNLOAD із wBlockNum = 0.
namespace dfuse {

struct SetAddress { std::uint32_t address; };
struct EraseSector { std::uint32_t address; };
struct EraseApplication {};

using Command = std::variant<SetAddress, EraseSector, EraseApplication>;

inline constexpr std::uint8_t kSetAddress = 0x21;
inline constexpr std::uint8_t kErase = 0x41;
inline constexpr std::uint8_t kReadUnprotect = 0x92;

// Розбір повертає або команду, або код помилки DFU — на -1 з errno тут
// не спираємось, помилка їде тим самим типом, що поїде хостові.
[[nodiscard]] std::expected<Command, Status> parse(std::span<const std::byte> payload) noexcept;

}  // namespace dfuse

[[nodiscard]] std::uint32_t le32(std::span<const std::byte, 4> bytes) noexcept;

}  // namespace fc::dfu
