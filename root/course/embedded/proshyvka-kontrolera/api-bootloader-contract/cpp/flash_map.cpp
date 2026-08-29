#include "flash_map.hpp"

#include <algorithm>
#include <array>

namespace fc::flash {
namespace {

// Регістровий блок контролера пам'яті STM32F4 (RM0090, розділ 3.9).
constexpr std::uintptr_t kFlashRegs = 0x4002'3C00;
constexpr std::uint32_t kKey1 = 0x4567'0123;
constexpr std::uint32_t kKey2 = 0xCDEF'89AB;

constexpr std::uint32_t kSrEop = 1u << 0;
constexpr std::uint32_t kSrOperr = 1u << 1;
constexpr std::uint32_t kSrWrperr = 1u << 4;
constexpr std::uint32_t kSrPgaerr = 1u << 5;
constexpr std::uint32_t kSrPgperr = 1u << 6;
constexpr std::uint32_t kSrPgserr = 1u << 7;
constexpr std::uint32_t kSrBsy = 1u << 16;
constexpr std::uint32_t kSrErrors = kSrOperr | kSrWrperr | kSrPgaerr | kSrPgperr | kSrPgserr;

constexpr std::uint32_t kCrPg = 1u << 0;
constexpr std::uint32_t kCrSer = 1u << 1;
constexpr std::uint32_t kCrSnb = 0x1Fu << 3;
constexpr std::uint32_t kCrPsize = 0x3u << 8;
constexpr std::uint32_t kCrPsizeX8 = 0x0u << 8;  // побайтний запис працює від 1.8 В
constexpr std::uint32_t kCrStrt = 1u << 16;
constexpr std::uint32_t kCrLock = 1u << 31;

// Межі SRAM STM32F405 — за ними перевіряємо вектор початкового стека.
constexpr std::uint32_t kSramBase = 0x2000'0000;
constexpr std::uint32_t kSramEnd = 0x2002'0000;

volatile std::uint32_t& reg(std::uintptr_t address) noexcept
{
    return *reinterpret_cast<volatile std::uint32_t*>(address);
}

volatile std::uint32_t& keyr() noexcept { return reg(kFlashRegs + 0x04); }
volatile std::uint32_t& sr() noexcept { return reg(kFlashRegs + 0x0C); }
volatile std::uint32_t& cr() noexcept { return reg(kFlashRegs + 0x10); }

constexpr std::uint8_t kAppAccess = kRead | kErase | kWrite;

constexpr std::array<Sector, 12> kSectors{{
    {0x0800'0000, 16u * 1024u, 0, kRead},
    {0x0800'4000, 16u * 1024u, 1, kRead},
    {0x0800'8000, 16u * 1024u, 2, kAppAccess},
    {0x0800'C000, 16u * 1024u, 3, kAppAccess},
    {0x0801'0000, 64u * 1024u, 4, kAppAccess},
    {0x0802'0000, 128u * 1024u, 5, kAppAccess},
    {0x0804'0000, 128u * 1024u, 6, kAppAccess},
    {0x0806'0000, 128u * 1024u, 7, kAppAccess},
    {0x0808'0000, 128u * 1024u, 8, kAppAccess},
    {0x080A'0000, 128u * 1024u, 9, kAppAccess},
    {0x080C'0000, 128u * 1024u, 10, kAppAccess},
    {0x080E'0000, 128u * 1024u, 11, kAppAccess},
}};

void clear_errors() noexcept
{
    sr() = kSrEop | kSrErrors;  // запис одиниці скидає прапорець
}

std::expected<void, dfu::Status> wait_ready() noexcept
{
    while ((sr() & kSrBsy) != 0) {
        // Порожнє очікування: під час запису ядро й так стоїть на шині.
    }

    const std::uint32_t status = sr();
    clear_errors();

    if ((status & kSrWrperr) != 0) {
        return std::unexpected(dfu::Status::ErrWrite);  // апаратний захист запису
    }
    if ((status & (kSrPgaerr | kSrPgperr | kSrPgserr)) != 0) {
        return std::unexpected(dfu::Status::ErrProg);
    }
    if ((status & kSrOperr) != 0) {
        return std::unexpected(dfu::Status::ErrErase);
    }
    return {};
}

// Форматування руками: бібліотечний snprintf з'їв би кілька кілобайтів
// із тридцяти двох, відведених завантажувачу.
class Writer {
public:
    explicit Writer(std::span<char> out) noexcept : out_{out} {}

    Writer& text(std::string_view value) noexcept
    {
        for (char c : value) {
            put(c);
        }
        return *this;
    }

    Writer& dec(std::uint32_t value, std::size_t width) noexcept
    {
        std::array<char, 10> digits{};
        std::size_t n = 0;
        do {
            digits[n++] = static_cast<char>('0' + value % 10);
            value /= 10;
        } while (value != 0 && n < digits.size());
        while (n < width && n < digits.size()) {
            digits[n++] = '0';  // доповнення нулями зліва: 4 -> "04"
        }
        while (n > 0) {
            put(digits[--n]);
        }
        return *this;
    }

    Writer& hex32(std::uint32_t value) noexcept
    {
        constexpr std::string_view kDigits = "0123456789ABCDEF";
        for (int shift = 28; shift >= 0; shift -= 4) {
            put(kDigits[(value >> shift) & 0xFu]);
        }
        return *this;
    }

    Writer& put(char c) noexcept
    {
        if (!ok_ || pos_ + 1 >= out_.size()) {
            ok_ = false;
            return *this;
        }
        out_[pos_++] = c;
        return *this;
    }

    [[nodiscard]] std::string_view finish() noexcept
    {
        if (!ok_) {
            return {};  // не влізло — краще порожньо, ніж обрізок
        }
        out_[pos_] = '\0';
        return std::string_view{out_.data(), pos_};
    }

private:
    std::span<char> out_;
    std::size_t pos_ = 0;
    bool ok_ = true;
};

constexpr char access_letter(std::uint8_t mask) noexcept
{
    // DfuSe кодує права літерою: 'a' = лише читання ... 'g' = read+write+erase.
    return static_cast<char>('a' - 1 + (mask & 0x7u));
}

}  // namespace

std::span<const Sector> sectors() noexcept
{
    return kSectors;
}

std::optional<Sector> sector_at(std::uint32_t address) noexcept
{
    const auto it = std::ranges::find_if(kSectors, [address](const Sector& s) {
        return address >= s.address && address < s.address + s.size;
    });
    if (it == kSectors.end()) {
        return std::nullopt;
    }
    return *it;
}

bool in_application(std::uint32_t address, std::size_t length) noexcept
{
    if (length == 0 || length > kTotalSize) {
        return false;
    }
    const auto end = static_cast<std::uint64_t>(address) + length;
    return address >= kApplicationBase && end <= static_cast<std::uint64_t>(kBase) + kTotalSize;
}

std::chrono::milliseconds erase_timeout(const Sector& sector) noexcept
{
    // Довідник дає typ/max на стирання; хостові віддаємо верхню оцінку.
    if (sector.size <= 16u * 1024u) {
        return std::chrono::milliseconds{800};
    }
    if (sector.size <= 64u * 1024u) {
        return std::chrono::milliseconds{1600};
    }
    return std::chrono::milliseconds{3000};
}

std::chrono::milliseconds application_erase_timeout() noexcept
{
    std::chrono::milliseconds total{0};
    for (const Sector& sector : kSectors) {
        if (sector.erasable()) {
            total += erase_timeout(sector);
        }
    }
    return total;
}

std::string_view layout_string(std::span<char> out) noexcept
{
    Writer writer{out};
    writer.text("@Internal Flash  /0x").hex32(kBase).put('/');

    std::size_t i = 0;
    bool first = true;
    while (i < kSectors.size()) {
        // Групуємо підряд однакові сектори: розмір і права мусять збігтися.
        std::size_t n = 1;
        while (i + n < kSectors.size() && kSectors[i + n].size == kSectors[i].size &&
               kSectors[i + n].access == kSectors[i].access) {
            ++n;
        }

        if (!first) {
            writer.put(',');
        }
        first = false;

        writer.dec(static_cast<std::uint32_t>(n), 2)
              .put('*')
              .dec(kSectors[i].size / 1024u, 3)
              .put('K')
              .put(access_letter(kSectors[i].access));
        i += n;
    }

    return writer.finish();
}

std::span<const std::byte> layout_descriptor(std::span<std::byte> out) noexcept
{
    std::array<char, 96> text{};
    const std::string_view layout = layout_string(text);
    if (layout.empty()) {
        return {};
    }

    // USB String Descriptor: bLength, bDescriptorType = 0x03, далі UTF-16LE.
    const std::size_t total = 2 + 2 * layout.size();
    if (total > 255 || total > out.size()) {
        return {};
    }

    out[0] = static_cast<std::byte>(total);
    out[1] = std::byte{0x03};
    for (std::size_t i = 0; i < layout.size(); ++i) {
        out[2 + 2 * i] = static_cast<std::byte>(layout[i]);
        out[3 + 2 * i] = std::byte{0};
    }
    return out.first(total);
}

std::span<const std::byte> read(std::uint32_t address, std::size_t length) noexcept
{
    if (length == 0 || length > kTotalSize || address < kBase) {
        return {};
    }
    const auto end = static_cast<std::uint64_t>(address) + length;
    if (end > static_cast<std::uint64_t>(kBase) + kTotalSize) {
        return {};
    }
    return {reinterpret_cast<const std::byte*>(static_cast<std::uintptr_t>(address)), length};
}

bool application_image_valid() noexcept
{
    const auto* vectors = reinterpret_cast<const volatile std::uint32_t*>(
        static_cast<std::uintptr_t>(kApplicationBase));
    const std::uint32_t stack_top = vectors[0];
    const std::uint32_t reset_pc = vectors[1];

    if (stack_top < kSramBase || stack_top > kSramEnd) {
        return false;  // образ стерли або записали сміття
    }
    if (reset_pc < kApplicationBase || reset_pc >= kBase + kTotalSize) {
        return false;
    }
    // Cortex-M виконує лише Thumb: молодший біт вектора Reset мусить бути 1.
    return (reset_pc & 1u) != 0;
}

Controller::Controller() noexcept
{
    if ((cr() & kCrLock) != 0) {
        keyr() = kKey1;
        keyr() = kKey2;
    }
    clear_errors();
}

Controller::~Controller()
{
    cr() |= kCrLock;
}

std::expected<void, dfu::Status> Controller::erase(std::uint32_t address) noexcept
{
    const auto sector = sector_at(address);
    if (!sector) {
        return std::unexpected(dfu::Status::ErrAddress);
    }
    if (!sector->erasable()) {
        // Сектори завантажувача хост стерти не може: після обриву живлення
        // платі не було б чим стартувати.
        return std::unexpected(dfu::Status::ErrTarget);
    }

    if (auto ready = wait_ready(); !ready) {
        return ready;
    }

    cr() &= ~(kCrSnb | kCrPsize);
    cr() |= kCrSer | kCrPsizeX8 | (static_cast<std::uint32_t>(sector->index) << 3);
    cr() |= kCrStrt;

    const auto result = wait_ready();
    cr() &= ~(kCrSer | kCrSnb);
    return result;
}

std::expected<void, dfu::Status> Controller::erase_application() noexcept
{
    // Справжнього Mass Erase не робимо: він змів би й завантажувач.
    for (const Sector& sector : kSectors) {
        if (!sector.erasable()) {
            continue;
        }
        if (auto result = erase(sector.address); !result) {
            return result;
        }
    }
    return {};
}

std::expected<void, dfu::Status> Controller::program(std::uint32_t address,
                                                     std::span<const std::byte> data) noexcept
{
    if (!in_application(address, data.size())) {
        return std::unexpected(dfu::Status::ErrAddress);
    }

    if (auto ready = wait_ready(); !ready) {
        return ready;
    }

    cr() &= ~kCrPsize;
    cr() |= kCrPsizeX8 | kCrPg;

    std::expected<void, dfu::Status> result{};
    for (std::size_t i = 0; i < data.size(); ++i) {
        auto* cell = reinterpret_cast<volatile std::uint8_t*>(
            static_cast<std::uintptr_t>(address) + i);
        *cell = static_cast<std::uint8_t>(data[i]);

        result = wait_ready();
        if (!result) {
            break;
        }
        // Перечитуємо одразу: не кожен промах запису піднімає прапорець.
        if (*cell != static_cast<std::uint8_t>(data[i])) {
            result = std::unexpected(dfu::Status::ErrVerify);
            break;
        }
    }

    cr() &= ~kCrPg;
    return result;
}

}  // namespace fc::flash
