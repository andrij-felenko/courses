// Єдина одиниця трансляції, де живе ядрова struct termios2.
// <asm/termbits.h> і <termios.h> разом не збираються: обидва оголошують
// struct termios і struct termio. Тому все ядрове замкнене тут, а решта
// програми працює зі звичайним POSIX-заголовком і бачить звідси числа.
#include "baud.hpp"

#include <cerrno>

#ifdef __linux__

#include <asm/termbits.h>   // struct termios2, BOTHER, TCGETS2/TCSETS2
#include <cstddef>

// ioctl() оголошуємо самі з тієї ж причини: <sys/ioctl.h> притягнув би
// bits/ioctl-types.h із власними struct termio й struct winsize.
extern "C" int ioctl(int fd, unsigned long request, ...);

namespace tty {
namespace {

std::error_code last_error() noexcept
{
    return std::error_code(errno, std::generic_category());
}

}  // namespace

std::optional<KernelLayout> kernel_layout() noexcept
{
    return KernelLayout{
        sizeof(termios2),
        NCCS,
        offsetof(termios2, c_cc),
        offsetof(termios2, c_ispeed),
        offsetof(termios2, c_ospeed),
        CBAUD,
        BOTHER,
    };
}

std::expected<unsigned long, std::error_code> line_speed(int fd) noexcept
{
    termios2 t{};

    if (::ioctl(fd, TCGETS2, &t) < 0)
        return std::unexpected(last_error());
    // У termios2 ядро тримає в c_ospeed справжнє число незалежно від того,
    // кодом із CBAUD чи через BOTHER задавали швидкість. Саме тому цей
    // запит відповідає й там, де cfgetospeed() віддав би самий лише код.
    return t.c_ospeed;
}

std::expected<unsigned long, std::error_code> set_line_speed(int fd,
                                                             unsigned long rate) noexcept
{
    if (rate == 0)   // нуль — це «покласти слухавку», а не швидкість
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));

    termios2 t{};
    if (::ioctl(fd, TCGETS2, &t) < 0)
        return std::unexpected(last_error());

    // Код швидкості з поля CBAUD геть, замість нього BOTHER: «дивись не
    // в таблицю констант Bxxx, а прямо в c_ispeed/c_ospeed».
    t.c_cflag &= ~static_cast<tcflag_t>(CBAUD);
    t.c_cflag |= BOTHER;
    t.c_ispeed = static_cast<speed_t>(rate);
    t.c_ospeed = static_cast<speed_t>(rate);

    // TCSETS2 — негайно, як TCSANOW. Чекати спустошення черги (TCSETSW2)
    // на зупиненому по ^S виводі означало б зависнути просто тут.
    if (::ioctl(fd, TCSETS2, &t) < 0)
        return std::unexpected(last_error());

    // Дільник тактової частоти цілий, тож ядро ставить найближче досяжне:
    // 250000 бод для DMX512 лягає точно, а 31250 для MIDI на дешевому
    // перетворювачі може стати 31249. Перепитуємо, що вийшло насправді.
    if (::ioctl(fd, TCGETS2, &t) < 0)
        return std::unexpected(last_error());
    return t.c_ospeed;
}

}  // namespace tty

#else  // termios2 — розширення саме ядра Linux

namespace tty {

std::optional<KernelLayout> kernel_layout() noexcept
{
    return std::nullopt;
}

std::expected<unsigned long, std::error_code> line_speed(int) noexcept
{
    return std::unexpected(std::make_error_code(std::errc::function_not_supported));
}

std::expected<unsigned long, std::error_code> set_line_speed(int, unsigned long) noexcept
{
    return std::unexpected(std::make_error_code(std::errc::function_not_supported));
}

}  // namespace tty

#endif
