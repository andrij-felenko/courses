#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <variant>

#include "dfu_protocol.hpp"
#include "flash_map.hpp"

namespace fc::dfu {

// Кінцевий автомат завантажувача. Запит на EP0 мусить відповісти за
// мілісекунди, а стирання сектора триває секунди — тому GETSTATUS лише
// оголошує таймаут, а роботу робить poll() із головного циклу.
class Device {
public:
    using Reply = std::span<const std::byte>;

    [[nodiscard]] std::expected<Reply, Status> control_request(
        Request request, std::uint16_t block, std::uint16_t length,
        std::span<const std::byte> data);

    void poll();

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] Status status() const noexcept { return status_; }

private:
    struct WriteOp { std::uint32_t address; std::size_t length; };
    struct EraseSectorOp { std::uint32_t address; };
    struct EraseApplicationOp {};
    struct ManifestOp {};

    using Pending = std::variant<std::monostate, WriteOp, EraseSectorOp,
                                 EraseApplicationOp, ManifestOp>;

    std::unexpected<Status> fail(Status status) noexcept;
    std::expected<Reply, Status> dnload(std::uint16_t block, std::span<const std::byte> data);
    std::expected<Reply, Status> upload(std::uint16_t block, std::uint16_t length);
    std::expected<Reply, Status> get_status();

    State state_ = State::DfuIdle;   // завантажувач стартує вже в dfuIdle
    Status status_ = Status::Ok;
    std::uint32_t address_pointer_ = flash::kBase;  // його ставить команда 0x21
    Pending pending_{};
    std::chrono::milliseconds poll_timeout_{0};
    std::array<std::byte, StatusResponse::kLength> reply_{};
    std::array<std::byte, kTransferSize> buffer_{};
};

}  // namespace fc::dfu
