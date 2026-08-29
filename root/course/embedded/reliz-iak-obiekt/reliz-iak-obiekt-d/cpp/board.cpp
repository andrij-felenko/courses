#include "board.hpp"

#include <algorithm>

/* Прив'язка до заліза: STM32F4, доступ прямо до регістрів. CMSIS сюди не
   тягнемо — завантажувач мусить лишатися малим і самодостатнім. */

namespace board {
namespace {

[[nodiscard]] volatile std::uint32_t& reg(std::uint32_t address) noexcept
{
    return *reinterpret_cast<volatile std::uint32_t*>(address);
}

constexpr std::uint32_t rcc_ahb1enr = 0x40023800u + 0x30u;

constexpr std::uint32_t gpiob_moder = 0x40020400u + 0x00u;
constexpr std::uint32_t gpiob_pupdr = 0x40020400u + 0x0Cu;
constexpr std::uint32_t gpiob_idr   = 0x40020400u + 0x10u;

constexpr std::uint32_t gpioc_moder = 0x40020800u + 0x00u;
constexpr std::uint32_t gpioc_bsrr  = 0x40020800u + 0x18u;

constexpr std::uint32_t flash_keyr = 0x40023C00u + 0x04u;
constexpr std::uint32_t flash_sr   = 0x40023C00u + 0x0Cu;
constexpr std::uint32_t flash_cr   = 0x40023C00u + 0x10u;

constexpr std::uint32_t flash_key1 = 0x45670123u;
constexpr std::uint32_t flash_key2 = 0xCDEF89ABu;

constexpr std::uint32_t sr_busy   = 1u << 16;
constexpr std::uint32_t sr_errors = (1u << 7) | (1u << 6) | (1u << 5) | (1u << 4) | (1u << 1);
constexpr std::uint32_t sr_eop    = 1u << 0;
constexpr std::uint32_t cr_pg     = 1u << 0;
constexpr std::uint32_t cr_psize  = 3u << 8;
constexpr std::uint32_t cr_lock   = 1u << 31;

/* OTP-блок STM32F4: 16 блоків по 32 байти від 0x1FFF7800. Блок 0 тримає
   лічильник безпеки, блок 1 — кореневий ключ (його байт блокування завод
   пропалює одразу після персоналізації). */
constexpr std::uint32_t otp_base       = 0x1FFF7800u;
constexpr std::size_t   otp_block_size = 32;
constexpr std::uint32_t otp_counter    = otp_base + 0 * otp_block_size;
constexpr std::uint32_t otp_root_key   = otp_base + 1 * otp_block_size;

/* Ревізія плати: три виводи PB12..PB14. Зовнішні резистори 10 кОм тягнуть
   кожен вивід до 3.3 В або до землі; усередині вмикаємо слабку (≈40 кОм)
   підтяжку до землі, щоб нерозпаяний вивід читався як нуль, а не плавав.
   Зовнішні 10 кОм до живлення перебивають її з запасом: 3.3 · 40/50 ≈ 2.6 В,
   а це впевнена логічна одиниця. */
constexpr unsigned rev_pin_first = 12;
constexpr unsigned rev_pin_count = 3;
constexpr unsigned led_pin       = 13;   // PC13

[[nodiscard]] std::span<const std::byte> otp_span(std::uint32_t address, std::size_t size) noexcept
{
    return {reinterpret_cast<const std::byte*>(address), size};
}

[[nodiscard]] bool flash_wait_idle() noexcept
{
    while ((reg(flash_sr) & sr_busy) != 0u) {
    }
    if ((reg(flash_sr) & sr_errors) != 0u) {
        reg(flash_sr) = sr_errors | sr_eop;   // прапорці скидаються записом одиниці
        return false;
    }
    return true;
}

[[nodiscard]] bool flash_program_byte(std::uint32_t address, std::uint8_t value) noexcept
{
    if (!flash_wait_idle()) {
        return false;
    }

    reg(flash_cr) &= ~cr_psize;      // PSIZE = 00: програмуємо побайтно
    reg(flash_cr) |= cr_pg;
    *reinterpret_cast<volatile std::uint8_t*>(address) = value;

    const bool ok = flash_wait_idle();
    reg(flash_cr) &= ~cr_pg;
    if (!ok) {
        return false;
    }

    /* Читаємо назад: OTP пропалюється один раз, і мовчазна невдача тут
       означала б пристрій, який назавжди приймає старі версії. */
    return *reinterpret_cast<volatile std::uint8_t*>(address) == value;
}

/* Замок Flash сам себе закриває при виході з області — RAII замість
   гілок «не забути зняти PG й повернути LOCK» на кожному return. */
class FlashUnlock {
public:
    FlashUnlock() noexcept
    {
        if ((reg(flash_cr) & cr_lock) != 0u) {
            reg(flash_keyr) = flash_key1;
            reg(flash_keyr) = flash_key2;
        }
        opened_ = (reg(flash_cr) & cr_lock) == 0u;
    }

    ~FlashUnlock() noexcept
    {
        reg(flash_cr) &= ~cr_pg;
        reg(flash_cr) |= cr_lock;
    }

    FlashUnlock(const FlashUnlock&) = delete;
    FlashUnlock& operator=(const FlashUnlock&) = delete;

    [[nodiscard]] bool opened() const noexcept { return opened_; }

private:
    bool opened_{false};
};

}  // namespace

void early_init() noexcept
{
    reg(rcc_ahb1enr) |= (1u << 1) | (1u << 2);   // такт на GPIOB і GPIOC

    for (unsigned i = 0; i < rev_pin_count; ++i) {
        const unsigned pin = rev_pin_first + i;
        reg(gpiob_moder) &= ~(3u << (2 * pin));          // вхід
        reg(gpiob_pupdr) &= ~(3u << (2 * pin));
        reg(gpiob_pupdr) |=  (2u << (2 * pin));          // підтяжка до землі
    }

    reg(gpioc_moder) &= ~(3u << (2 * led_pin));
    reg(gpioc_moder) |=  (1u << (2 * led_pin));          // вихід push-pull

    /* Підтяжка з ємністю виводу дає сталу в одиниці мікросекунд —
       читати одразу після налаштування не можна. */
    for (volatile unsigned settle = 0; settle < 2000u; ++settle) {
    }
}

std::uint8_t pcb_revision() noexcept
{
    const std::uint32_t idr = reg(gpiob_idr);
    std::uint8_t revision = 0;

    for (unsigned i = 0; i < rev_pin_count; ++i) {
        if ((idr & (1u << (rev_pin_first + i))) != 0u) {
            revision |= static_cast<std::uint8_t>(1u << i);
        }
    }
    return revision;
}

std::optional<fw::PublicKey> root_public_key() noexcept
{
    const auto cells = otp_span(otp_root_key, 32);

    /* Незаписана OTP — суцільні 0xFF. Такий «ключ» узяти за кореневий
       означало б перевіряти підпис проти сміття. */
    if (std::ranges::all_of(cells, [](std::byte b) { return b == std::byte{0xFF}; })) {
        return std::nullopt;
    }
    return fw::PublicKey{cells.data(), 32};
}

std::uint32_t security_counter() noexcept
{
    /* Термометровий код: рівень — це кількість пропалених у нуль байтів.
       Максимум 32 підвищення безпеки за життя виробу. */
    const auto cells = otp_span(otp_counter, otp_block_size);
    return static_cast<std::uint32_t>(std::ranges::count(cells, std::byte{0x00}));
}

bool burn_security_counter(std::uint32_t level) noexcept
{
    if (level > otp_block_size) {
        return false;                    // більше рівнів чип не вміє
    }

    std::uint32_t current = security_counter();
    if (level <= current) {
        return true;                     // уже на цьому рівні — нічого палити
    }

    const FlashUnlock unlock;
    if (!unlock.opened()) {
        return false;                    // послідовність відкриття не спрацювала
    }

    for (; current < level; ++current) {
        if (!flash_program_byte(otp_counter + current, 0x00u)) {
            return false;
        }
    }
    return true;
}

std::span<const std::byte> flash_window(std::uint32_t address, std::size_t size) noexcept
{
    /* Внутрішня Flash відображена в адресний простір, тож «читання» — це
       вид на неї. Межі все одно перевіряємо: розмір приходить із файлу,
       якому ми ще не довіряємо. */
    if (address < flash_base || size > flash_size ||
        address - flash_base > flash_size - size) {
        return {};
    }
    return {reinterpret_cast<const std::byte*>(address), size};
}

void led(bool on) noexcept
{
    // BSRR: молодша половина вмикає, старша скидає — без read-modify-write.
    reg(gpioc_bsrr) = on ? (1u << led_pin) : (1u << (led_pin + 16));
}

void delay_ms(std::uint32_t ms) noexcept
{
    /* Завантажувач працює на HSI 16 МГц до будь-якого налаштування PLL.
       Точності тут не треба: затримка потрібна лише миготінню й підтяжкам. */
    while (ms-- > 0u) {
        for (volatile unsigned i = 0; i < 1600u; ++i) {
        }
    }
}

}  // namespace board
