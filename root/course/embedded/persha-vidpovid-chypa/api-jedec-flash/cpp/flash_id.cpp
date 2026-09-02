#include "flash_id.hpp"

#include <algorithm>
#include <ranges>

namespace flash {
namespace {

struct VendorEntry {
    std::uint8_t     bank;
    std::uint8_t     id;
    std::string_view name;
};

/* Той самий код у різних банках — різні компанії, тому ключ це пара. */
constexpr std::array kVendors{
    VendorEntry{1, 0xEF, "Winbond Electronics"},
    VendorEntry{1, 0xC2, "Macronix (MXIC)"},
    VendorEntry{1, 0xC8, "GigaDevice"},
    VendorEntry{1, 0x20, "Micron / Numonyx / ST"},
    VendorEntry{1, 0x01, "Spansion / Cypress / Infineon"},
    VendorEntry{1, 0xBF, "Microchip / SST"},
    VendorEntry{1, 0x9D, "ISSI"},
    VendorEntry{1, 0x85, "Puya Semiconductor"},
    VendorEntry{1, 0x68, "Boya Microelectronics"},
    VendorEntry{1, 0x5E, "Zbit Semiconductor"},
};

bool all_equal(std::span<const std::uint8_t> data, std::uint8_t value)
{
    return std::ranges::all_of(data, [value](std::uint8_t b) { return b == value; });
}

void read_id(SpiLink &link, std::span<std::uint8_t> raw)
{
    const std::array<std::uint8_t, 1> cmd{kCmdReadId};
    std::ranges::fill(raw, std::uint8_t{0});
    command(link, cmd, raw);
}

/* Вихід із QPI: сам опкод теж мусить піти по чотирьох лініях, інакше кристал
   його не почує — у цьому вся пастка стану QPI. */
void leave_qpi(SpiLink &link)
{
    const std::array<std::uint8_t, 1> cmd{kCmdExitQpi};
    ChipSelect cs{link};
    link.quad_write(cmd);
}

[[nodiscard]] bool wait_not_busy(SpiLink &link)
{
    const std::array<std::uint8_t, 1> cmd{kCmdReadStatus1};
    const auto start = link.now();
    for (;;) {
        std::array<std::uint8_t, 1> status{};
        command(link, cmd, status);
        if ((status[0] & kStatusWip) == 0) {
            return true;
        }
        if (link.now() - start > kWipTimeout) {
            return false;
        }
    }
}

}  // namespace

std::string_view vendor_name(std::uint8_t bank, std::uint8_t manufacturer) noexcept
{
    const auto it = std::ranges::find_if(kVendors, [&](const VendorEntry &e) {
        return e.bank == bank && e.id == manufacturer;
    });
    return it == kVendors.end() ? std::string_view{"невідомий виробник"} : it->name;
}

std::string_view Passport::vendor() const noexcept
{
    return vendor_name(bank, manufacturer);
}

std::string_view describe(IdError error) noexcept
{
    switch (error) {
    case IdError::ShortAnswer:     return "відповідь коротша за три байти";
    case IdError::StuckHigh:       return "суцільні 0xFF: обрив MISO, немає живлення або чип у QPI";
    case IdError::StuckLow:        return "суцільні 0x00: замикання MISO на землю або утримане скидання";
    case IdError::Continuation:    return "нескінченні байти продовження 0x7F";
    case IdError::StillBusy:       return "прапорець WIP не скинувся: кристал досі стирає";
    case IdError::UnknownCapacity: return "код ємності поза діапазоном 0x10..0x1A";
    }
    return "невідомий стан";
}

std::expected<Passport, IdError> decode(std::span<const std::uint8_t> answer)
{
    if (answer.size() < 3) {
        return std::unexpected{IdError::ShortAnswer};
    }

    Passport passport;
    passport.raw_len = std::min(answer.size(), kIdMaxBytes);
    std::ranges::copy(answer.first(passport.raw_len), passport.raw.begin());

    /* Скільки байтів 0x7F попереду — стільки банків JEP106 перегорнуто. */
    std::size_t skip = 0;
    while (skip < answer.size() && answer[skip] == 0x7F && skip <= kMaxContinuation) {
        ++skip;
    }
    if (skip > kMaxContinuation || skip + 3 > answer.size()) {
        return std::unexpected{IdError::Continuation};
    }

    const auto body = answer.subspan(skip, 3);
    if (all_equal(body, 0xFF)) {
        return std::unexpected{IdError::StuckHigh};
    }
    if (all_equal(body, 0x00)) {
        return std::unexpected{IdError::StuckLow};
    }

    passport.bank          = static_cast<std::uint8_t>(skip + 1);
    passport.manufacturer  = body[0];
    passport.memory_type   = body[1];
    passport.capacity_code = body[2];

    /* Ємність логарифмічна: код це степінь двійки в байтах. Поза смугою
       0x10..0x1A це або не код ємності, або взагалі не наша відповідь. */
    if (passport.capacity_code < 0x10 || passport.capacity_code > 0x1A) {
        return std::unexpected{IdError::UnknownCapacity};
    }
    passport.size_bytes = std::uint32_t{1} << passport.capacity_code;
    return passport;
}

std::expected<Passport, IdError> identify(SpiLink &link)
{
    /* Читання даних кристал тягне на 104–133 МГц, а сам опкод 0x9F у
       специфікаціях обмежений 33–50 МГц. Сторож поверне частоту на виході. */
    ClockGuard slow{link, kSafeClockHz};

    std::array<std::uint8_t, kIdMaxBytes> raw{};
    read_id(link, raw);

    /* Суцільні 0xFF — це або мертва лінія, або живий кристал у QPI.
       Дешева перевірка: одна спроба виходу з QPI й повторне читання.
       Судимо по трьох паспортних байтах: хвіст відповіді чипи добивають
       одиницями і в цілком справному стані. */
    const auto body = [&raw] { return std::span<const std::uint8_t>{raw}.first(3); };

    bool recovered = false;
    if (all_equal(body(), 0xFF)) {
        leave_qpi(link);
        read_id(link, raw);
        if (all_equal(body(), 0xFF)) {
            return std::unexpected{IdError::StuckHigh};
        }
        recovered = true;
    }

    /* Кристал говорить — тепер читається й регістр статусу. Якщо всередині
       йде стирання, перший байт відповіді 0x9F буває спотвореним, тож чекаємо
       скидання WIP і питаємо ще раз. */
    if (!wait_not_busy(link)) {
        return std::unexpected{IdError::StillBusy};
    }
    read_id(link, raw);

    return decode(raw).transform([recovered](Passport p) {
        p.recovered_from_qpi = recovered;
        return p;
    });
}

}  // namespace flash
