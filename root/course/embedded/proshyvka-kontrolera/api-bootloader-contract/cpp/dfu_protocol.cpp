#include "dfu_protocol.hpp"

namespace fc::dfu {
namespace {

constexpr std::byte lo(std::uint32_t value, unsigned shift) noexcept
{
    return static_cast<std::byte>((value >> shift) & 0xFFu);
}

}  // namespace

std::uint32_t le32(std::span<const std::byte, 4> bytes) noexcept
{
    return static_cast<std::uint32_t>(bytes[0])
         | (static_cast<std::uint32_t>(bytes[1]) << 8)
         | (static_cast<std::uint32_t>(bytes[2]) << 16)
         | (static_cast<std::uint32_t>(bytes[3]) << 24);
}

std::array<std::byte, FunctionalDescriptor::kLength>
FunctionalDescriptor::to_bytes() const noexcept
{
    const auto timeout = static_cast<std::uint32_t>(detach_timeout.count());
    return {
        static_cast<std::byte>(kLength),
        static_cast<std::byte>(kDescriptorType),
        static_cast<std::byte>(attributes),
        lo(timeout, 0), lo(timeout, 8),
        lo(transfer_size, 0), lo(transfer_size, 8),
        lo(bcd_version, 0), lo(bcd_version, 8),
    };
}

std::array<std::byte, StatusResponse::kLength> StatusResponse::to_bytes() const noexcept
{
    auto poll = static_cast<std::uint32_t>(poll_timeout.count());
    if (poll > 0x00FF'FFFFu) {
        poll = 0x00FF'FFFFu;  // bwPollTimeout має лише 24 біти
    }
    return {
        static_cast<std::byte>(status),
        lo(poll, 0), lo(poll, 8), lo(poll, 16),
        static_cast<std::byte>(state),
        static_cast<std::byte>(string_index),
    };
}

namespace dfuse {

std::expected<Command, Status> parse(std::span<const std::byte> payload) noexcept
{
    if (payload.empty()) {
        return std::unexpected(Status::ErrStalledPkt);
    }

    const auto opcode = static_cast<std::uint8_t>(payload[0]);
    const auto address = [&]() -> std::uint32_t {
        return le32(payload.subspan<1, 4>());
    };

    switch (opcode) {
    case kSetAddress:
        if (payload.size() != 5) {
            return std::unexpected(Status::ErrStalledPkt);
        }
        if ((address() & 0x3u) != 0u) {
            return std::unexpected(Status::ErrAddress);  // пишемо словами
        }
        return Command{SetAddress{address()}};

    case kErase:
        if (payload.size() == 1) {
            return Command{EraseApplication{}};
        }
        if (payload.size() != 5) {
            return std::unexpected(Status::ErrStalledPkt);
        }
        return Command{EraseSector{address()}};

    case kReadUnprotect:
        // Зняття RDP стирає кристал цілком, разом із завантажувачем: не тут.
        return std::unexpected(Status::ErrVendor);

    default:
        return std::unexpected(Status::ErrVendor);
    }
}

}  // namespace dfuse
}  // namespace fc::dfu
