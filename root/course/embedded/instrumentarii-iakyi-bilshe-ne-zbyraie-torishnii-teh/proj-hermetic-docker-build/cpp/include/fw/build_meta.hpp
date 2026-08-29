// Метадані збірки у секції .meta — та сама задача, що й у c/, але засобами
// C++23: діапазони замість «вказівник + довжина», std::expected замість кодів
// повернення, консteval-перевірки замість _Static_assert.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace fw {

enum class MetaError : std::uint8_t {
    Magic,      // сигнатури немає — це не наш образ
    Version,    // формат розійшовся з відомим коду
    Size,       // інша довжина структури: несумісний штампувальник
    Unstamped,  // образ зібрано, але stamp_meta.py по ньому не пройшов
    Range,      // метадані лежать поза межами наданого образу
    Crc         // образ пошкоджено або підмінено
};

[[nodiscard]] std::string_view describe(MetaError error) noexcept;

// Розкладку читають ззовні (Python, бутлоадер), тож жодних вирівнювальних
// дірок: packed тут не оптимізація, а зобов'язання перед іншим інструментом.
struct [[gnu::packed]] Meta {
    static constexpr std::uint32_t kMagic = 0x544F4F4CU;  // 'TOOL'
    static constexpr std::uint16_t kVersion = 1;
    static constexpr std::size_t kSize = 92;

    std::uint32_t magic;
    std::uint16_t version;
    std::uint16_t size;
    std::uint32_t build_epoch;
    std::uint32_t image_size;
    std::uint32_t image_crc32;
    std::array<char, 40> git_commit;    // повний SHA-1 у hex, без нуля
    std::array<char, 32> toolchain_id;  // добитий нулями рядок

    [[nodiscard]] constexpr std::string_view gitCommit() const noexcept
    {
        return {git_commit.data(), git_commit.size()};
    }

    [[nodiscard]] constexpr std::string_view toolchainId() const noexcept
    {
        std::string_view all{toolchain_id.data(), toolchain_id.size()};
        const auto zero = all.find('\0');
        return zero == std::string_view::npos ? all : all.substr(0, zero);
    }
};

static_assert(sizeof(Meta) == Meta::kSize,
              "розкладка Meta розійшлася зі stamp_meta.py");

namespace detail {

consteval std::array<std::uint32_t, 256> makeCrcTable() noexcept
{
    std::array<std::uint32_t, 256> table{};
    for (std::uint32_t i = 0; i < table.size(); ++i) {
        std::uint32_t value = i;
        for (int bit = 0; bit < 8; ++bit) {
            value = (value & 1U) ? (0xEDB8'8320U ^ (value >> 1)) : (value >> 1);
        }
        table[i] = value;
    }
    return table;
}

inline constexpr auto kCrcTable = makeCrcTable();

}  // namespace detail

// CRC-32 (IEEE 802.3) без фінального інвертування: продовжується по шматках.
[[nodiscard]] constexpr std::uint32_t crc32(std::span<const std::byte> data,
                                            std::uint32_t crc = 0xFFFF'FFFFU) noexcept
{
    for (const std::byte b : data) {
        crc = detail::kCrcTable[(crc ^ std::to_integer<std::uint32_t>(b)) & 0xFFU] ^ (crc >> 8);
    }
    return crc;
}

// Повна перевірка образу: сигнатура, версія, довжина, межі й CRC32.
// image — фактичні межі прошитого двійкового образу.
[[nodiscard]] std::expected<void, MetaError> verify(const Meta& meta,
                                                    std::span<const std::byte> image) noexcept;

// Метадані, прочитані з Flash за адресою секції. До самого об'єкта
// звертатися не можна: компілятор підставив би нулі, які лежали в ньому
// ДО штампування, і перевірка CRC виродилася б у константу.
[[nodiscard]] const Meta& currentMeta() noexcept;

// Однорядковий звіт «чим і коли це зібрано» у наданий буфер, без <cstdio>.
// Повертає вигляд на записану частину.
[[nodiscard]] std::string_view report(std::span<char> out, const Meta& meta) noexcept;

}  // namespace fw
