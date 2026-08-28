#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>

namespace zerocopy {

template <typename T>
[[nodiscard]] constexpr T load_le(const std::byte* ptr) noexcept {
    T val{};
    std::memcpy(&val, ptr, sizeof(T));
    return val;
}

class PacketView {
public:
    [[nodiscard]] static std::optional<PacketView> create(std::span<const std::byte> buf) noexcept {
        if (buf.size() < 8) return std::nullopt;

        const auto root_off = load_le<std::uint32_t>(buf.data());
        if (root_off >= buf.size() || buf.size() - root_off < 4) return std::nullopt;

        const std::byte* table = buf.data() + root_off;
        const auto vtable_soff = load_le<std::int32_t>(table);
        const auto vtable_abs = static_cast<std::ptrdiff_t>(table - buf.data()) - vtable_soff;

        if (vtable_abs < 0 || static_cast<std::size_t>(vtable_abs) + 4 > buf.size()) {
            return std::nullopt;
        }

        const std::byte* vtable = buf.data() + vtable_abs;
        const auto vtable_len = load_le<std::uint16_t>(vtable);

        return PacketView(buf, table, vtable, vtable_len);
    }

    [[nodiscard]] std::uint32_t get_price(std::uint16_t field_idx, std::uint32_t def_val = 0) const noexcept {
        const std::size_t voff_pos = 4 + field_idx * sizeof(std::uint16_t);
        if (voff_pos + sizeof(std::uint16_t) > vtable_len_) return def_val;

        const auto field_off = load_le<std::uint16_t>(vtable_ + voff_pos);
        if (field_off == 0) return def_val;

        return load_le<std::uint32_t>(table_ + field_off);
    }

private:
    constexpr PacketView(std::span<const std::byte> buf,
                         const std::byte* table,
                         const std::byte* vtable,
                         std::uint16_t vlen) noexcept
        : buf_(buf), table_(table), vtable_(vtable), vtable_len_(vlen) {}

    std::span<const std::byte> buf_;
    const std::byte* table_;
    const std::byte* vtable_;
    std::uint16_t vtable_len_;
};

} // namespace zerocopy
