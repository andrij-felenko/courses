#include "abi.hpp"

#include "baud.hpp"

#include <cstddef>
#include <format>
#include <string_view>

#include <termios.h>
#include <unistd.h>

namespace tty {
namespace {

struct Field {
    std::string_view name;
    std::size_t offset;
    std::size_t size;
    std::string_view role;
};

// offsetof і sizeof питаємо в компілятора, а не переписуємо з документації:
// розкладка залежить від платформи, і саме її розбіжність із ядровою дає
// найдовші вечори з termios.
#define TTY_FIELD(f, text) Field{#f, offsetof(termios, f), sizeof(termios::f), text}

const Field kFields[] = {
    TTY_FIELD(c_iflag,  "вхід: BREAK, парність, CR/NL, XON/XOFF"),
    TTY_FIELD(c_oflag,  "вихід: OPOST, ONLCR, телетайпні затримки"),
    TTY_FIELD(c_cflag,  "лінія: кадр даних, парність, поле CBAUD"),
    TTY_FIELD(c_lflag,  "дисципліна: ICANON, ECHO, ISIG, IEXTEN"),
#ifdef __linux__
    TTY_FIELD(c_line,   "номер лінійної дисципліни (0 = N_TTY)"),
#endif
    TTY_FIELD(c_cc,     "спецсимволи за індексами VINTR…VEOL2"),
    TTY_FIELD(c_ispeed, "швидкість прийому"),
    TTY_FIELD(c_ospeed, "швидкість передачі"),
};

#undef TTY_FIELD

}  // namespace

std::string abi_report()
{
    std::string out =
        std::format("struct termios (простір користувача): {} байтів, NCCS = {}\n",
                    sizeof(termios), NCCS);

    out += std::format("  {:<9} {:>8} {:>6}  {}\n", "поле", "зміщення", "розмір", "роль");
    for (const Field& f : kFields)
        out += std::format("  {:<9} {:>8} {:>6}  {}\n", f.name, f.offset, f.size, f.role);
    out += std::format("  типи: tcflag_t {} Б, cc_t {} Б, speed_t {} Б; "
                       "_POSIX_VDISABLE = {:#04x}\n",
                       sizeof(tcflag_t), sizeof(cc_t), sizeof(speed_t),
                       static_cast<unsigned>(_POSIX_VDISABLE));

    const auto kernel = kernel_layout();
    if (!kernel)
        return out + "\nstruct termios2: ядрового <asm/termbits.h> тут немає\n";

    out += std::format("\nstruct termios2 (ядро): {} байтів, NCCS = {}\n",
                       kernel->size, kernel->nccs);
    out += std::format("  c_cc     +{}\n  c_ispeed +{}\n  c_ospeed +{}\n",
                       kernel->cc_offset, kernel->ispeed_offset, kernel->ospeed_offset);
    out += std::format("  CBAUD = {:#o}, BOTHER = {:#o}\n", kernel->cbaud, kernel->bother);

    // Ось де ховається головна пастка ABI: ядро віддає 19 спецсимволів,
    // а бібліотека розкладає їх у масив на 32. Тому struct termios ніколи
    // не передають у TCGETS2 напряму — між двома розкладками перекладає
    // сама бібліотека всередині tcgetattr().
    if (kernel->nccs != static_cast<unsigned long>(NCCS))
        out += std::format("  УВАГА: у ядрі {} спецсимволів, у бібліотеці {} —\n"
                           "         struct termios у TCGETS2 віддавати не можна\n",
                           kernel->nccs, NCCS);
    if (kernel->size != sizeof(termios))
        out += std::format("  розміри структур різні ({} проти {}), і це не поломка:\n"
                           "         у termios2 швидкість лежить числом, "
                           "а масив c_cc коротший\n",
                           kernel->size, sizeof(termios));
    return out;
}

}  // namespace tty
