#include <cstdint>
#include <cstddef>
#include <cstring>
#include <string_view>
#include <span>
#include <optional>
#include <expected>
#include <iostream>
#include <vector>

namespace zc {

using uoffset_t = std::uint32_t;
using soffset_t = std::int32_t;
using voffset_t = std::uint16_t;

enum class Error {
    BufferTooSmall,
    InvalidRootOffset,
    InvalidVtableOffset,
    TableOutOfBounds,
    FieldOutOfBounds,
    StringOutOfBounds
};

template <typename T>
[[nodiscard]] constexpr T load_scalar(const std::byte* ptr) noexcept {
    T val{};
    std::memcpy(&val, ptr, sizeof(T));
    return val;
}

class Reader {
public:
    [[nodiscard]] static std::expected<Reader, Error> create(std::span<const std::byte> buffer) noexcept {
        if (buffer.size() < sizeof(uoffset_t)) {
            return std::unexpected(Error::BufferTooSmall);
        }

        const auto root_off = load_scalar<uoffset_t>(buffer.data());
        if (root_off >= buffer.size() || buffer.size() - root_off < sizeof(soffset_t)) {
            return std::unexpected(Error::InvalidRootOffset);
        }

        const std::byte* root_ptr = buffer.data() + root_off;
        const auto vtable_soff = load_scalar<soffset_t>(root_ptr);
        const auto vtable_abs_offset = static_cast<std::ptrdiff_t>(root_ptr - buffer.data()) - vtable_soff;

        if (vtable_abs_offset < 0 || static_cast<std::size_t>(vtable_abs_offset) + 4 > buffer.size()) {
            return std::unexpected(Error::InvalidVtableOffset);
        }

        const std::byte* vtable_ptr = buffer.data() + vtable_abs_offset;
        const auto vtable_size = load_scalar<voffset_t>(vtable_ptr);
        const auto table_size = load_scalar<voffset_t>(vtable_ptr + sizeof(voffset_t));

        if (vtable_size < 4 || static_cast<std::size_t>(vtable_abs_offset) + vtable_size > buffer.size()) {
            return std::unexpected(Error::InvalidVtableOffset);
        }
        if (root_off + table_size > buffer.size()) {
            return std::unexpected(Error::TableOutOfBounds);
        }

        return Reader(buffer, root_ptr, vtable_ptr, vtable_size, table_size);
    }

    [[nodiscard]] std::expected<std::uint32_t, Error> get_uint32(std::uint16_t field_idx, std::uint32_t default_val = 0) const noexcept {
        const std::size_t voff_entry = 4 + field_idx * sizeof(voffset_t);
        if (voff_entry + sizeof(voffset_t) > vtable_size_) {
            return default_val;
        }

        const auto field_offset = load_scalar<voffset_t>(vtable_ + voff_entry);
        if (field_offset == 0) {
            return default_val;
        }

        if (field_offset + sizeof(std::uint32_t) > table_size_) {
            return std::unexpected(Error::FieldOutOfBounds);
        }

        return load_scalar<std::uint32_t>(root_table_ + field_offset);
    }

    [[nodiscard]] std::expected<std::string_view, Error> get_string(std::uint16_t field_idx) const noexcept {
        const std::size_t voff_entry = 4 + field_idx * sizeof(voffset_t);
        if (voff_entry + sizeof(voffset_t) > vtable_size_) {
            return std::string_view{};
        }

        const auto field_offset = load_scalar<voffset_t>(vtable_ + voff_entry);
        if (field_offset == 0) {
            return std::string_view{};
        }

        if (field_offset + sizeof(uoffset_t) > table_size_) {
            return std::unexpected(Error::FieldOutOfBounds);
        }

        const std::byte* ptr_pos = root_table_ + field_offset;
        const auto rel_offset = load_scalar<uoffset_t>(ptr_pos);
        const std::byte* str_pos = ptr_pos + rel_offset;

        if (str_pos < buffer_.data() || str_pos + sizeof(std::uint32_t) > buffer_.data() + buffer_.size()) {
            return std::unexpected(Error::StringOutOfBounds);
        }

        const auto str_len = load_scalar<std::uint32_t>(str_pos);
        const std::byte* str_data = str_pos + sizeof(std::uint32_t);

        if (str_data + str_len > buffer_.data() + buffer_.size()) {
            return std::unexpected(Error::StringOutOfBounds);
        }

        return std::string_view{reinterpret_cast<const char*>(str_data), str_len};
    }

private:
    constexpr Reader(std::span<const std::byte> buffer,
                     const std::byte* root,
                     const std::byte* vtable,
                     voffset_t vt_size,
                     voffset_t tbl_size) noexcept
        : buffer_(buffer), root_table_(root), vtable_(vtable), vtable_size_(vt_size), table_size_(tbl_size) {}

    std::span<const std::byte> buffer_;
    const std::byte* root_table_;
    const std::byte* vtable_;
    voffset_t vtable_size_;
    voffset_t table_size_;
};

} // namespace zc

int main() {
    alignas(8) std::byte buffer[256]{};

    // 1. Формуємо рядок "Order-A1" на зсуві 80
    std::byte* str_ptr = buffer + 80;
    const std::string_view sample_name = "Order-A1";
    const auto sample_len = static_cast<std::uint32_t>(sample_name.size());
    std::memcpy(str_ptr, &sample_len, sizeof(sample_len));
    std::memcpy(str_ptr + 4, sample_name.data(), sample_len);

    // 2. Формуємо Vtable на зсуві 4
    const zc::voffset_t vtable[] = { 10, 16, 4, 8, 12 };
    std::memcpy(buffer + 4, vtable, sizeof(vtable));

    // 3. Формуємо таблицю екземпляра на зсуві 24
    const zc::soffset_t soffset_vtable = 24 - 4;
    const std::uint32_t field_id = 42001;
    const std::uint32_t field_price = 1999;
    const auto rel_str_offset = static_cast<zc::uoffset_t>((buffer + 80) - (buffer + 24 + 12));

    std::memcpy(buffer + 24, &soffset_vtable, sizeof(soffset_vtable));
    std::memcpy(buffer + 28, &field_id, sizeof(field_id));
    std::memcpy(buffer + 32, &field_price, sizeof(field_price));
    std::memcpy(buffer + 36, &rel_str_offset, sizeof(rel_str_offset));

    // 4. Вказуємо Root Offset = 24
    const zc::uoffset_t root_off = 24;
    std::memcpy(buffer, &root_off, sizeof(root_off));

    // 5. Читаємо через нуль-копійний інтерфейс C++
    const auto reader = zc::Reader::create(buffer);
    if (!reader) {
        std::cerr << "Помилка валідації двійкового буфера!\n";
        return 1;
    }

    const auto order_id = reader->get_uint32(0);
    const auto price = reader->get_uint32(1);
    const auto name = reader->get_string(2);

    if (order_id && price && name) {
        std::cout << "ID: " << *order_id << ", Ціна: " << *price << ", Назва: " << *name << '\n';
    }

    return 0;
}
