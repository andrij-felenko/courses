#include "storage.hpp"

#include <algorithm>
#include <bit>
#include <cstring>

namespace autopilot::failsafe {

namespace {

void putU16(std::byte* p, std::uint16_t v) noexcept
{
    p[0] = static_cast<std::byte>(v);
    p[1] = static_cast<std::byte>(v >> 8);
}

void putU32(std::byte* p, std::uint32_t v) noexcept
{
    for (int i = 0; i < 4; ++i)
        p[i] = static_cast<std::byte>(v >> (8 * i));
}

std::uint16_t getU16(const std::byte* p) noexcept
{
    return static_cast<std::uint16_t>(std::to_integer<unsigned>(p[0]) |
                                      (std::to_integer<unsigned>(p[1]) << 8));
}

std::uint32_t getU32(const std::byte* p) noexcept
{
    std::uint32_t v = 0;
    for (int i = 0; i < 4; ++i)
        v |= static_cast<std::uint32_t>(std::to_integer<unsigned>(p[i])) << (8 * i);
    return v;
}

static_assert(sizeof(float) == 4, "серіалізація розрахована на IEEE-754 binary32");

} // namespace

std::string_view toString(StoreError e) noexcept
{
    switch (e) {
    case StoreError::Erased:       return "ERASED";
    case StoreError::BadMagic:     return "BAD_MAGIC";
    case StoreError::BadCrc:       return "BAD_CRC";
    case StoreError::FutureSchema: return "FUTURE_SCHEMA";
    case StoreError::FlashFailure: return "FLASH_FAILURE";
    case StoreError::NoValidBank:  return "NO_VALID_BANK";
    }
    return "?";
}

std::uint32_t crc32(std::span<const std::byte> data) noexcept
{
    std::uint32_t crc = 0xFFFF'FFFFu;
    for (std::byte b : data) {
        crc ^= std::to_integer<std::uint32_t>(b);
        for (int i = 0; i < 8; ++i)
            crc = (crc >> 1) ^ (0xEDB8'8320u & static_cast<std::uint32_t>(-static_cast<std::int32_t>(crc & 1u)));
    }
    return crc ^ 0xFFFF'FFFFu;
}

void FlashSector::erase() noexcept
{
    std::ranges::fill(mem_, std::byte{0xFF});
}

bool FlashSector::program(std::span<const std::byte> src) noexcept
{
    if (src.size() > mem_.size())
        return false;
    // Програмування поверх незстертого сектора дало б побітове І — відсіюємо.
    if (!std::all_of(mem_.begin(), mem_.begin() + static_cast<std::ptrdiff_t>(src.size()),
                     [](std::byte b) { return b == std::byte{0xFF}; }))
        return false;
    std::ranges::copy(src, mem_.begin());
    return std::equal(src.begin(), src.end(), mem_.begin());  // верифікація зчитуванням
}

void FlashSector::flipBit(std::size_t byteOffset, int bit) noexcept
{
    if (byteOffset < mem_.size())
        mem_[byteOffset] ^= std::byte{static_cast<unsigned char>(1u << (bit & 7))};
}

std::expected<ParamStore::Decoded, StoreError> ParamStore::decode(const FlashSector& sector) const
{
    const auto raw = sector.read();
    const std::uint32_t magic = getU32(raw.data());

    if (magic == 0xFFFF'FFFFu)
        return std::unexpected(StoreError::Erased);
    if (magic != kParamMagic)
        return std::unexpected(StoreError::BadMagic);

    const std::uint16_t schema = getU16(raw.data() + 4);
    const std::size_t   count  = getU16(raw.data() + 6);
    if (schema > kSchemaVersion || count > kParamCount)
        return std::unexpected(StoreError::FutureSchema);

    const std::size_t payload = kHeaderSize + count * 4;
    if (payload + 4 > raw.size())
        return std::unexpected(StoreError::FutureSchema);

    if (getU32(raw.data() + payload) != crc32(raw.first(payload)))
        return std::unexpected(StoreError::BadCrc);

    std::vector<float> values(count);
    for (std::size_t i = 0; i < count; ++i)
        values[i] = std::bit_cast<float>(getU32(raw.data() + kHeaderSize + i * 4));

    Decoded d{};
    d.clamped = d.block.restore(values);  // тут же відбувається міграція схеми
    d.seq = getU32(raw.data() + 8);
    return d;
}

std::expected<ParamStore::Loaded, StoreError> ParamStore::load()
{
    auto a = decode(banks_[0]);
    auto b = decode(banks_[1]);

    if (!a && !b) {
        // Обидві копії втрачено: параметри заводські, зведення заблокує валідація.
        active_ = 0;
        seq_ = 0;
        return std::unexpected(a.error() == StoreError::Erased && b.error() == StoreError::Erased
                                   ? StoreError::Erased
                                   : StoreError::NoValidBank);
    }

    std::size_t pick;
    if (a && b)
        // Порівняння різниці стійке до переповнення лічильника.
        pick = static_cast<std::int32_t>(a->seq - b->seq) >= 0 ? 0 : 1;
    else
        pick = a ? 0 : 1;

    auto& chosen = (pick == 0) ? *a : *b;
    active_ = pick;
    seq_ = chosen.seq;
    return Loaded{ chosen.block, pick, chosen.clamped };
}

std::expected<void, StoreError> ParamStore::save(const ParamBlock& block)
{
    std::array<std::byte, kSectorSize> buf{};
    std::ranges::fill(buf, std::byte{0xFF});

    putU32(buf.data(), kParamMagic);
    putU16(buf.data() + 4, kSchemaVersion);
    putU16(buf.data() + 6, static_cast<std::uint16_t>(kParamCount));

    const std::uint32_t next = seq_ + 1;
    putU32(buf.data() + 8, next);

    std::size_t off = kHeaderSize;
    for (float value : block.raw()) {
        putU32(buf.data() + off, std::bit_cast<std::uint32_t>(value));
        off += 4;
    }
    putU32(buf.data() + off, crc32(std::span{buf}.first(off)));
    off += 4;

    // Транзакція: пишемо в резервний банк і робимо його активним лише після
    // вдалого перечитування. Обрив живлення посеред запису лишає старий банк.
    const std::size_t target = 1 - active_;
    banks_[target].erase();
    if (!banks_[target].program(std::span{buf}.first(off)))
        return std::unexpected(StoreError::FlashFailure);
    if (!decode(banks_[target]))
        return std::unexpected(StoreError::FlashFailure);

    active_ = target;
    seq_ = next;
    return {};
}

} // namespace autopilot::failsafe
