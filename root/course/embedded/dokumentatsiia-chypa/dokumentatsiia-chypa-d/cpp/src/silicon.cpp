#include "hw/silicon.hpp"

#include <algorithm>
#include <array>

#include "hw/registers.hpp"

namespace hw::silicon {
namespace {

/* Таблиця 1: сирий REV_ID → літера ревізії. Числа з розділу «Device
 * identification» еррати ES0182; коду, якого там немає, ми не вигадуємо. */
struct RevisionRow {
    std::uint16_t    rev_id;
    Revision         revision;
    std::string_view name;
};

constexpr std::array revisions{
    RevisionRow{0x1000U, Revision::rev_a, "Rev A"},
    RevisionRow{0x1001U, Revision::rev_z, "Rev Z"},
    RevisionRow{0x1003U, Revision::rev_1, "Rev 1"},
    RevisionRow{0x1007U, Revision::rev_2, "Rev 2"},
    RevisionRow{0x100FU, Revision::rev_y, "Rev Y"},
    RevisionRow{0x2001U, Revision::rev_3, "Rev 3"},
};

/* Таблиця 2: маска уражених ревізій — та сама колонка з хрестиком
 * у зведеній таблиці еррати, лише записана бітами. */
using RevisionSet = std::uint32_t;

[[nodiscard]] constexpr RevisionSet only(Revision revision) noexcept
{
    return RevisionSet{1} << static_cast<unsigned>(revision);
}

constexpr RevisionSet all_revisions =
    only(Revision::rev_a) | only(Revision::rev_z) | only(Revision::rev_1) |
    only(Revision::rev_2) | only(Revision::rev_y) | only(Revision::rev_3);

struct ErratumRow {
    Erratum          erratum;
    std::string_view title;
    RevisionSet      affected;
};

constexpr std::array errata{
    ErratumRow{
        Erratum::rcc_clock_enable_delay,
        "ES0182: Delay after an RCC peripheral clock enabling",
        all_revisions,  // виправлення немає в жодній ревізії
    },
    ErratumRow{
        Erratum::i2c_busy_lock,
        "ES0182: I2C analog filter may provide wrong value, locking BUSY flag",
        only(Revision::rev_a) | only(Revision::rev_z),  // далі виправлено
    },
};

[[nodiscard]] Revision decode(std::uint16_t rev_id) noexcept
{
    const auto found = std::ranges::find(revisions, rev_id, &RevisionRow::rev_id);
    return (found != revisions.end()) ? found->revision : Revision::unknown;
}

} // namespace

std::expected<Device, IdError> identify() noexcept
{
    /* Єдине читання регістра: DEV_ID [11:0], REV_ID [31:16],
     * біти [15:12] зарезервовані й маскуються. */
    const std::uint32_t idcode = dbgmcu().idcode;

    Device info{
        .dev_id   = static_cast<std::uint16_t>(idcode & 0x0FFFU),
        .rev_id   = static_cast<std::uint16_t>((idcode >> 16) & 0xFFFFU),
        .revision = decode(static_cast<std::uint16_t>((idcode >> 16) & 0xFFFFU)),
    };

    if (info.dev_id != expected_dev_id) {
        return std::unexpected{IdError::foreign_device};
    }
    return info;
}

const Device& device() noexcept
{
    /* Звернення до шини налагодження не безкоштовне, а під час старту
     * ревізію питають кілька модулів — читаємо один раз. */
    static const Device cached = identify().value_or(Device{});
    return cached;
}

bool affected(Erratum erratum) noexcept
{
    const Device& info = device();

    if (info.dev_id != expected_dev_id || info.revision == Revision::unknown) {
        return true;  // безпечний бік: обходимо
    }

    const auto row = std::ranges::find(errata, erratum, &ErratumRow::erratum);
    if (row == errata.end()) {
        return false;
    }
    return (row->affected & only(info.revision)) != 0U;
}

std::string_view name(Revision revision) noexcept
{
    const auto found = std::ranges::find(revisions, revision, &RevisionRow::revision);
    return (found != revisions.end()) ? found->name : std::string_view{"Rev ?"};
}

std::string_view title(Erratum erratum) noexcept
{
    const auto row = std::ranges::find(errata, erratum, &ErratumRow::erratum);
    return (row != errata.end()) ? row->title : std::string_view{"невідомий дефект"};
}

} // namespace hw::silicon
