#include <cstdint>
#include <string_view>
#include <span>
#include <array>

struct TransactionId {
    static constexpr size_t kMaxDataSize = 128;
    static constexpr size_t kMaxGtridSize = 64;
    static constexpr size_t kMaxBqualSize = 64;

    int64_t format_id{-1};
    int64_t gtrid_length{0};
    int64_t bqual_length{0};
    std::array<std::byte, kMaxDataSize> data{};

    [[nodiscard]] std::span<const std::byte> global_transaction_id() const noexcept {
        return std::span<const std::byte>(data.data(), static_cast<size_t>(gtrid_length));
    }

    [[nodiscard]] std::span<const std::byte> branch_qualifier() const noexcept {
        return std::span<const std::byte>(data.data() + gtrid_length, static_cast<size_t>(bqual_length));
    }
};
