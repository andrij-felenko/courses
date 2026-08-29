#include "fw/build_meta.hpp"

#include <algorithm>
#include <bit>

// Ті самі три значення з Makefile через -D; без котрогось образ був би
// невідстежуваним, тож краще не зібратися взагалі.
#ifndef SOURCE_DATE_EPOCH
#error "SOURCE_DATE_EPOCH не заданий: збірка не була б відтворюваною"
#endif
#ifndef FW_GIT_COMMIT
#error "FW_GIT_COMMIT не заданий: образ неможливо звести до коміту"
#endif
#ifndef FW_TOOLCHAIN_ID
#error "FW_TOOLCHAIN_ID не заданий: невідомо, чим це скомпільовано"
#endif

// Початок секції .meta, який розставив компонувальник
extern "C" const std::byte __meta_start[];

namespace fw {
namespace {

// Рівно N символів: коротший хеш робить виклик невірним ще на компіляції.
// Кидок у consteval — не виняток під час виконання, а відмова зібратися.
template <std::size_t N>
consteval std::array<char, N> exactly(std::string_view text)
{
    if (text.size() != N) {
        throw "рядок мусить мати рівно N символів";
    }
    std::array<char, N> chars{};
    std::ranges::copy(text, chars.begin());
    return chars;
}

// Коротший за поле рядок допускається — решта лишається нулями.
template <std::size_t N>
consteval std::array<char, N> padded(std::string_view text)
{
    if (text.size() > N) {
        throw "рядок не влазить у поле";
    }
    std::array<char, N> chars{};
    std::ranges::copy(text, chars.begin());
    return chars;
}

}  // namespace

// used — щоб --gc-sections не викинув структуру, на яку ніхто не посилається
// з коду: її читає зовнішній інструмент, а не сама прошивка.
[[gnu::section(".meta"), gnu::used]]
constinit const Meta g_meta{
    .magic = Meta::kMagic,
    .version = Meta::kVersion,
    .size = static_cast<std::uint16_t>(sizeof(Meta)),
    .build_epoch = static_cast<std::uint32_t>(SOURCE_DATE_EPOCH),
    .image_size = 0,   // обидва проставить stamp_meta.py: до компонування
    .image_crc32 = 0,  // ні розміру, ні контрольної суми ще не існує
    .git_commit = exactly<40>(FW_GIT_COMMIT),
    .toolchain_id = padded<32>(FW_TOOLCHAIN_ID),
};

const Meta& currentMeta() noexcept
{
    return *reinterpret_cast<const Meta*>(__meta_start);
}

std::expected<void, MetaError> verify(const Meta& meta,
                                      std::span<const std::byte> image) noexcept
{
    if (meta.magic != Meta::kMagic) {
        return std::unexpected(MetaError::Magic);
    }
    if (meta.version != Meta::kVersion) {
        return std::unexpected(MetaError::Version);
    }
    if (meta.size != sizeof(Meta)) {
        return std::unexpected(MetaError::Size);
    }
    if (meta.image_size == 0) {
        return std::unexpected(MetaError::Unstamped);
    }
    if (meta.image_size > image.size()) {
        return std::unexpected(MetaError::Range);
    }

    const auto body = image.first(meta.image_size);
    const auto* self = reinterpret_cast<const std::byte*>(&meta);

    // Метадані мусять лежати всередині того самого образу — інакше зсув
    // поля CRC рахувати нема від чого.
    if (self < body.data() || self + sizeof(Meta) > body.data() + body.size()) {
        return std::unexpected(MetaError::Range);
    }

    const auto crcOffset = static_cast<std::size_t>(self - body.data()) + offsetof(Meta, image_crc32);
    const std::size_t tail = crcOffset + sizeof(std::uint32_t);
    if (tail > body.size()) {
        return std::unexpected(MetaError::Range);
    }

    // Рахуємо так само, як штампувальник: поле CRC на час підрахунку
    // вважається нульовим, решта образу — як є.
    static constexpr std::array<std::byte, sizeof(std::uint32_t)> kZeros{};
    std::uint32_t crc = crc32(body.first(crcOffset));
    crc = crc32(kZeros, crc);
    crc = crc32(body.subspan(tail), crc);
    crc ^= 0xFFFF'FFFFU;

    if (crc != meta.image_crc32) {
        return std::unexpected(MetaError::Crc);
    }
    return {};
}

std::string_view describe(MetaError error) noexcept
{
    using enum MetaError;
    switch (error) {
        case Magic:     return "bad-magic";
        case Version:   return "bad-version";
        case Size:      return "bad-size";
        case Unstamped: return "unstamped";
        case Range:     return "bad-range";
        case Crc:       return "bad-crc";
    }
    return "unknown";
}

namespace {

// Дописує скільки влізло й повертає новий хвіст буфера: замість
// «вказівник + залишок» скрізь їздить один span.
std::span<char> put(std::span<char> out, std::string_view text) noexcept
{
    const auto n = std::min(out.size(), text.size());
    std::ranges::copy_n(text.begin(), static_cast<std::ptrdiff_t>(n), out.begin());
    return out.subspan(n);
}

std::span<char> putDecimal(std::span<char> out, std::uint32_t value) noexcept
{
    std::array<char, 10> digits{};
    std::size_t n = 0;
    do {
        digits[n++] = static_cast<char>('0' + value % 10);
        value /= 10;
    } while (value != 0);

    while (n != 0 && !out.empty()) {
        out[0] = digits[--n];
        out = out.subspan(1);
    }
    return out;
}

std::span<char> putHex32(std::span<char> out, std::uint32_t value) noexcept
{
    constexpr std::string_view kHex = "0123456789abcdef";
    for (int shift = 28; shift >= 0 && !out.empty(); shift -= 4) {
        out[0] = kHex[(value >> shift) & 0xFU];
        out = out.subspan(1);
    }
    return out;
}

}  // namespace

std::string_view report(std::span<char> out, const Meta& meta) noexcept
{
    if (out.empty()) {
        return {};
    }

    std::span<char> tail = out;
    tail = put(tail, "git=");
    tail = put(tail, meta.gitCommit());
    tail = put(tail, " tc=");
    tail = put(tail, meta.toolchainId());
    tail = put(tail, " epoch=");
    tail = putDecimal(tail, meta.build_epoch);
    tail = put(tail, " size=");
    tail = putDecimal(tail, meta.image_size);
    tail = put(tail, " crc=0x");
    tail = putHex32(tail, meta.image_crc32);

    return {out.data(), out.size() - tail.size()};
}

}  // namespace fw
