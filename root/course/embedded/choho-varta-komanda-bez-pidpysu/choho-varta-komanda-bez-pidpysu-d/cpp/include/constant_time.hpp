#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace ct {

/// Довжина тегу автентичності: повний HMAC-SHA256.
inline constexpr std::size_t kTagLen = 32;

using Tag = std::array<std::uint8_t, kTagLen>;

/// Звіряє два буфери за сталий час: читає ЗАВЖДИ всі байти обох.
/// Час виконання не залежить від позиції першого незбігу — саме цю
/// позицію й видає наївне порівняння.
[[nodiscard]] bool verify(std::span<const std::uint8_t> a,
                          std::span<const std::uint8_t> b) noexcept;

/// Затирає буфер так, щоб оптимізатор не мав права викинути запис
/// як мертвий. Відповідник explicit_bzero, якого в стандарті немає.
void wipe(std::span<std::uint8_t> buffer) noexcept;

/// Секрет, який затирає себе сам.
///
/// У C ключ доводиться чистити руками на КОЖНІЙ гілці виходу, і рано чи
/// пізно одну гілку забувають. Тут за це відповідає деструктор: забути
/// його неможливо, а копіювання й переміщення заборонені, щоб секрет не
/// розповзся тимчасовими копіями по стеку.
class Secret {
public:
    explicit Secret(const Tag& value) noexcept : bytes_{value} {}

    ~Secret() { wipe(bytes_); }

    Secret(const Secret&) = delete;
    Secret& operator=(const Secret&) = delete;
    Secret(Secret&&) = delete;
    Secret& operator=(Secret&&) = delete;

    [[nodiscard]] std::span<const std::uint8_t> view() const noexcept { return bytes_; }

private:
    Tag bytes_;
};

}  // namespace ct
