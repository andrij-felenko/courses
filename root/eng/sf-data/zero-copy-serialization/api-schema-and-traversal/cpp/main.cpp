#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <expected>

namespace zc {

enum class Status : std::int32_t {
    Ok = 0,
    BufferTruncated = -1,
    InvalidRootOffset = -2,
    InvalidVtable = -3,
    TableOutOfBounds = -4,
    FieldOutOfBounds = -5,
    CycleDetected = -6,
    AlignmentViolation = -7
};

class Verifier {
public:
    explicit constexpr Verifier(std::span<const std::byte> buffer,
                                std::size_t max_depth = 64,
                                std::size_t byte_budget = 1024 * 1024 * 64) noexcept;

    [[nodiscard]] Status verify_all() const noexcept;
    [[nodiscard]] bool check_range(const std::byte* ptr, std::size_t len, std::size_t align) const noexcept;
};

template <typename TableType>
class MessageView {
public:
    [[nodiscard]] static std::expected<MessageView<TableType>, Status>
    create(std::span<const std::byte> buffer) noexcept;

    [[nodiscard]] const TableType* root() const noexcept;
    [[nodiscard]] std::span<const std::byte> raw_buffer() const noexcept;
};

} // namespace zc
