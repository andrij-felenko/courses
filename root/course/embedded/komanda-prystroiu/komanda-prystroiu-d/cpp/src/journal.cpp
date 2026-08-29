#include "journal.hpp"

#include <algorithm>

namespace cmdctl {
namespace {

// Розкладка запису у FRAM: magic "JRN1" · token · type · open · crc32.
// Контрольна сума потрібна тому, що запис може обірватися на середині:
// недописаний запис не має видаватися за дійсний.
constexpr std::uint32_t JournalMagic = 0x4A524E31u;
constexpr std::size_t OffMagic = 0, OffToken = 4, OffType = 12, OffOpen = 13, OffCrc = 14;
constexpr std::size_t RecordSize = 18;

void put32(std::span<std::byte> cells, std::size_t at, std::uint32_t v) noexcept {
    cells[at + 0] = static_cast<std::byte>(v & 0xFFu);
    cells[at + 1] = static_cast<std::byte>((v >> 8) & 0xFFu);
    cells[at + 2] = static_cast<std::byte>((v >> 16) & 0xFFu);
    cells[at + 3] = static_cast<std::byte>((v >> 24) & 0xFFu);
}

[[nodiscard]] std::uint32_t get32(std::span<const std::byte> cells, std::size_t at) noexcept {
    return std::to_integer<std::uint32_t>(cells[at + 0]) |
           (std::to_integer<std::uint32_t>(cells[at + 1]) << 8) |
           (std::to_integer<std::uint32_t>(cells[at + 2]) << 16) |
           (std::to_integer<std::uint32_t>(cells[at + 3]) << 24);
}

}  // namespace

void Journal::write(std::uint64_t token, Type type, bool open) {
    auto cells = nvm_.cells();
    std::ranges::fill(cells, std::byte{0});

    put32(cells, OffMagic, JournalMagic);
    put32(cells, OffToken, static_cast<std::uint32_t>(token & 0xFFFFFFFFu));
    put32(cells, OffToken + 4, static_cast<std::uint32_t>(token >> 32));
    cells[OffType] = static_cast<std::byte>(type);
    cells[OffOpen] = static_cast<std::byte>(open ? 1 : 0);
    put32(cells, OffCrc, crc32(cells.first(OffCrc)));
}

void Journal::clear() {
    write(0, Type::Noop, false);
}

std::optional<JournalEntry> Journal::open_entry() const {
    auto cells = nvm_.cells();
    if (cells.size() < RecordSize) return std::nullopt;
    if (get32(cells, OffMagic) != JournalMagic) return std::nullopt;
    if (crc32(cells.first(OffCrc)) != get32(cells, OffCrc)) return std::nullopt;   // обірваний запис
    if (std::to_integer<std::uint8_t>(cells[OffOpen]) != 1) return std::nullopt;

    JournalEntry e;
    e.token = static_cast<std::uint64_t>(get32(cells, OffToken)) |
              (static_cast<std::uint64_t>(get32(cells, OffToken + 4)) << 32);
    e.type = static_cast<Type>(std::to_integer<std::uint8_t>(cells[OffType]));
    return e;
}

Journal::Transaction::Transaction(Journal& owner, std::uint64_t token, Type type) : owner_{&owner} {
    owner_->write(token, type, true);
}

Journal::Transaction::Transaction(Transaction&& other) noexcept : owner_{other.owner_} {
    other.owner_ = nullptr;
}

Journal::Transaction& Journal::Transaction::operator=(Transaction&& other) noexcept {
    if (this != &other) {
        close();
        owner_ = other.owner_;
        other.owner_ = nullptr;
    }
    return *this;
}

Journal::Transaction::~Transaction() {
    close();
}

void Journal::Transaction::close() noexcept {
    if (owner_ != nullptr) {
        owner_->clear();
        owner_ = nullptr;
    }
}

}  // namespace cmdctl
