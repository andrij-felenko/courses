#include "storage.hpp"

#include <algorithm>
#include <cstring>

namespace fleet {
namespace {

constexpr std::uint32_t kStateMagic = 0x4F544131u;   // 'O','T','A','1'
constexpr std::size_t   kStateWords = 8;             // 7 слів даних + CRC
constexpr std::size_t   kStateSlots = 2;             // запис не псує чинного стану
constexpr std::uint32_t kRecordBytes = kStateWords * 4;
constexpr std::uint32_t kJournalLimit = kNvramBase + kPageSize;

// --- периферія -------------------------------------------------------------
// На кристалі це справжні RTC Backup Domain і контролер Flash. Тут — модель,
// у якій запис уміє лише гасити біти, а стирання повертає сторінку в 0xFF:
// без цього помилка «запис у нестерту комірку» знайшлася б аж у полі.
class SimulatedFlash {
public:
    static SimulatedFlash& instance()
    {
        static SimulatedFlash flash;
        return flash;
    }

    std::uint32_t backup(std::size_t idx) const noexcept
    {
        return idx < backup_.size() ? backup_[idx] : 0u;
    }
    void set_backup(std::size_t idx, std::uint32_t value) noexcept
    {
        if (idx < backup_.size()) {
            backup_[idx] = value;
        }
    }

    bool unlock() noexcept { unlocked_ = true; return true; }
    void lock() noexcept { unlocked_ = false; }
    bool unlocked() const noexcept { return unlocked_; }

    const std::byte* at(std::uint32_t addr) const noexcept
    {
        if (addr < kFlashBase || addr >= kFlashBase + kFlashSize) {
            return nullptr;
        }
        return cells_.data() + (addr - kFlashBase);
    }

    bool erase_page(std::uint32_t addr) noexcept
    {
        if (!unlocked_ || addr % kPageSize != 0) {
            return false;
        }
        if (addr < kFlashBase || addr + kPageSize > kFlashBase + kFlashSize) {
            return false;
        }
        std::fill_n(cells_.begin() + (addr - kFlashBase), kPageSize, std::byte{0xFF});
        return true;
    }

    bool program(std::uint32_t addr, std::span<const std::byte> data) noexcept
    {
        if (!unlocked_ || addr % kWriteQuantum != 0 || data.size() % kWriteQuantum != 0) {
            return false;
        }
        if (addr < kFlashBase || addr + data.size() > kFlashBase + kFlashSize) {
            return false;
        }
        std::byte* dst = cells_.data() + (addr - kFlashBase);
        for (std::size_t i = 0; i < data.size(); ++i) {
            if ((dst[i] & data[i]) != data[i]) {
                return false;   // запис у нестерту комірку
            }
            dst[i] &= data[i];
        }
        return true;
    }

private:
    SimulatedFlash() { cells_.fill(std::byte{0xFF}); }

    std::array<std::byte, kFlashSize> cells_{};
    std::array<std::uint32_t, 32> backup_{};   // RTC Backup Domain
    bool unlocked_{false};
};

// Функція, яку лінкер кладе в RAM.
#if defined(__arm__)
[[gnu::section(".RamFunc"), gnu::noinline]]
#endif
bool program_from_ram(std::uint32_t addr, std::span<const std::byte> data) noexcept
{
    return SimulatedFlash::instance().program(addr, data);
}

std::array<std::uint32_t, kStateWords> pack(const RolloutState& st) noexcept
{
    std::array<std::uint32_t, kStateWords> w{};
    w[0] = kStateMagic;
    w[1] = (static_cast<std::uint32_t>(st.seq) << 24) |
           (static_cast<std::uint32_t>(std::to_underlying(st.active)) << 16) |
           (static_cast<std::uint32_t>(st.trial_pending ? 1u : 0u) << 8) |
           static_cast<std::uint32_t>(st.boot_failures);
    w[2] = st.campaign_id;
    w[3] = st.length[0];
    w[4] = st.crc[0];
    w[5] = st.length[1];
    w[6] = st.crc[1];
    w[7] = crc32(std::as_bytes(std::span{w}).first(7 * 4));
    return w;
}

std::expected<RolloutState, StorageError> unpack(std::span<const std::uint32_t> w) noexcept
{
    if (w.size() < kStateWords || w[0] != kStateMagic) {
        return std::unexpected(StorageError::NoRecord);
    }
    if (w[7] != crc32(std::as_bytes(w.first(7)))) {
        return std::unexpected(StorageError::CrcMismatch);
    }

    RolloutState st;
    st.seq           = static_cast<std::uint8_t>(w[1] >> 24);
    st.active        = ((w[1] >> 16) & 1u) ? Bank::B : Bank::A;
    st.trial_pending = ((w[1] >> 8) & 1u) != 0u;
    st.boot_failures = static_cast<std::uint8_t>(w[1] & 0xFFu);
    st.campaign_id   = w[2];
    st.length[0]     = w[3];
    st.crc[0]        = w[4];
    st.length[1]     = w[5];
    st.crc[1]        = w[6];
    return st;
}

// Порівняння версій із урахуванням переповнення восьмибітного лічильника.
bool newer(std::uint8_t a, std::uint8_t b) noexcept
{
    return static_cast<std::int8_t>(a - b) > 0;
}

std::expected<RolloutState, StorageError> read_slot(std::size_t slot) noexcept
{
    std::array<std::uint32_t, kStateWords> w{};
    for (std::size_t i = 0; i < kStateWords; ++i) {
        w[i] = SimulatedFlash::instance().backup(slot * kStateWords + i);
    }
    return unpack(w);
}

std::expected<RolloutState, StorageError> journal_latest()
{
    std::expected<RolloutState, StorageError> best = std::unexpected(StorageError::NoRecord);

    for (std::uint32_t addr = kNvramBase; addr < kJournalLimit; addr += kRecordBytes) {
        const std::byte* p = SimulatedFlash::instance().at(addr);
        if (p == nullptr) {
            break;
        }
        std::array<std::uint32_t, kStateWords> w{};
        std::memcpy(w.data(), p, sizeof(w));
        if (w[0] == 0xFFFFFFFFu) {
            break;   // далі незаписаний хвіст сторінки
        }
        const auto record = unpack(w);
        if (!record) {
            continue;   // обірваний запис: живлення зникло під час програмування
        }
        if (!best || newer(record->seq, best->seq)) {
            best = record;
        }
    }
    return best;
}

std::expected<void, StorageError> journal_append(const RolloutState& st)
{
    std::uint32_t addr = kNvramBase;
    while (addr < kJournalLimit) {
        const std::byte* p = SimulatedFlash::instance().at(addr);
        if (p == nullptr) {
            return std::unexpected(StorageError::OutOfBounds);
        }
        std::uint32_t magic{};
        std::memcpy(&magic, p, sizeof(magic));
        if (magic == 0xFFFFFFFFu) {
            break;
        }
        addr += kRecordBytes;
    }

    FlashGuard guard;
    if (!guard.unlocked()) {
        return std::unexpected(StorageError::Locked);
    }

    if (addr >= kJournalLimit) {
        // Сторінка заповнена. Чинний стан уже в backup-регістрах, тож вікно
        // без журналу безпечне.
        if (!SimulatedFlash::instance().erase_page(kNvramBase)) {
            return std::unexpected(StorageError::EraseFailed);
        }
        addr = kNvramBase;
    }

    const auto w = pack(st);
    if (!SimulatedFlash::instance().program(addr, std::as_bytes(std::span{w}))) {
        return std::unexpected(StorageError::ProgramFailed);
    }
    return {};
}

} // namespace

std::string_view describe(StorageError e) noexcept
{
    switch (e) {
        case StorageError::Locked:        return "контролер Flash закритий";
        case StorageError::Misaligned:    return "невирівняна адреса або довжина";
        case StorageError::OutOfBounds:   return "за межами банку";
        case StorageError::EraseFailed:   return "сторінка не стерлася";
        case StorageError::ProgramFailed: return "запис у нестерту комірку";
        case StorageError::NoRecord:      return "цілого запису стану немає";
        case StorageError::CrcMismatch:   return "контрольна сума не збіглася";
    }
    return "невідома помилка";
}

std::uint32_t crc32(std::span<const std::byte> data, std::uint32_t seed) noexcept
{
    std::uint32_t crc = ~seed;
    for (std::byte b : data) {
        crc ^= static_cast<std::uint32_t>(b);
        for (int bit = 0; bit < 8; ++bit) {
            const std::uint32_t mask = ~(crc & 1u) + 1u;
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }
    return ~crc;
}

FlashGuard::FlashGuard() noexcept : unlocked_(SimulatedFlash::instance().unlock()) {}

FlashGuard::~FlashGuard()
{
    if (unlocked_) {
        SimulatedFlash::instance().lock();
    }
}

RolloutState StateStore::load() const
{
    std::expected<RolloutState, StorageError> best = std::unexpected(StorageError::NoRecord);

    for (std::size_t slot = 0; slot < kStateSlots; ++slot) {
        const auto record = read_slot(slot);
        if (record && (!best || newer(record->seq, best->seq))) {
            best = record;
        }
    }

    if (!best) {
        best = journal_latest();   // живлення зникало: backup-регістри чисті
    }

    return best.value_or(RolloutState{});
}

std::expected<void, StorageError> StateStore::save(RolloutState& st)
{
    ++st.seq;

    // Пишемо в слот, який НЕ був чинним: якщо живлення зникне посеред запису,
    // попередній слот лишається читабельним.
    std::size_t target = 0;
    if (const auto first = read_slot(0); first) {
        const auto second = read_slot(1);
        if (!second || newer(first->seq, second->seq)) {
            target = 1;
        }
    }

    const auto w = pack(st);
    for (std::size_t i = 0; i < kStateWords; ++i) {
        SimulatedFlash::instance().set_backup(target * kStateWords + i, w[i]);
    }

    return journal_append(st);
}

std::expected<void, StorageError> BankWriter::erase()
{
    FlashGuard guard;
    if (!guard.unlocked()) {
        return std::unexpected(StorageError::Locked);
    }
    const std::uint32_t base = bank_base(bank_);
    for (std::uint32_t off = 0; off < kBankSize; off += kPageSize) {
        if (!SimulatedFlash::instance().erase_page(base + off)) {
            return std::unexpected(StorageError::EraseFailed);
        }
    }
    return {};
}

std::expected<void, StorageError> BankWriter::write(std::uint32_t offset,
                                                    std::span<const std::byte> data)
{
    if (offset % kWriteQuantum != 0) {
        return std::unexpected(StorageError::Misaligned);
    }
    if (offset > kBankSize || data.size() > kBankSize - offset) {
        return std::unexpected(StorageError::OutOfBounds);
    }

    FlashGuard guard;
    if (!guard.unlocked()) {
        return std::unexpected(StorageError::Locked);
    }

    const std::uint32_t addr = bank_base(bank_) + offset;
    const std::size_t whole = data.size() - data.size() % kWriteQuantum;

    if (whole > 0 && !program_from_ram(addr, data.first(whole))) {
        return std::unexpected(StorageError::ProgramFailed);
    }
    if (whole < data.size()) {
        // Хвіст доповнюємо 0xFF — у стертій Flash це той самий стан, тож CRC
        // рахується по справжній довжині образу.
        std::array<std::byte, kWriteQuantum> tail{};
        tail.fill(std::byte{0xFF});
        std::ranges::copy(data.subspan(whole), tail.begin());
        if (!program_from_ram(addr + static_cast<std::uint32_t>(whole), tail)) {
            return std::unexpected(StorageError::ProgramFailed);
        }
    }
    return {};
}

std::span<const std::byte> bank_view(Bank bank, std::uint32_t len)
{
    if (len == 0 || len > kBankSize) {
        return {};
    }
    const std::byte* p = SimulatedFlash::instance().at(bank_base(bank));
    return p == nullptr ? std::span<const std::byte>{} : std::span{p, len};
}

std::uint32_t bank_crc(Bank bank, std::uint32_t len)
{
    return crc32(bank_view(bank, len));
}

} // namespace fleet
