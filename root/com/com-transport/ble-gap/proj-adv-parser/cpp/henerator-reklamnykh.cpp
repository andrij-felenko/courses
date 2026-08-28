#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <array>
#include <optional>
#include <cstring>

class BleAdvBuilder {
public:
    static constexpr size_t MaxPayloadSize = 31;

    BleAdvBuilder() = default;

    [[nodiscard]] bool add_field(BleAdType type, std::span<const uint8_t> data) noexcept {
        const size_t required_space = 2 + data.size();
        if (current_size_ + required_space > MaxPayloadSize) {
            return false; // Не вміщується в буфер
        }

        buffer_[current_size_]     = static_cast<uint8_t>(1 + data.size());
        buffer_[current_size_ + 1] = static_cast<uint8_t>(type);

        if (!data.empty()) {
            std::memcpy(&buffer_[current_size_ + 2], data.data(), data.size());
        }

        current_size_ += required_space;
        return true;
    }

    [[nodiscard]] bool add_flags(uint8_t flags) noexcept {
        const std::array<uint8_t, 1> f{flags};
        return add_field(BleAdType::Flags, f);
    }

    [[nodiscard]] bool add_complete_name(std::string_view name) noexcept {
        const auto span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(name.data()), name.size()
        );
        return add_field(BleAdType::CompleteLocalName, span);
    }

    [[nodiscard]] std::span<const uint8_t> build() const noexcept {
        return {buffer_.data(), current_size_};
    }

private:
    std::array<uint8_t, MaxPayloadSize> buffer_{};
    size_t current_size_{0};
};
