#include "flags.hpp"

#include <array>
#include <format>

namespace tty {
namespace {

// Таблиці constexpr: у бінарнику це просто дані, жодної ініціалізації
// в рантаймі. Прапорці поза POSIX закриті #ifdef — на BSD їх немає.
constexpr FlagBit kInput[] = {
    {"ignbrk", IGNBRK}, {"brkint", BRKINT}, {"ignpar", IGNPAR},
    {"parmrk", PARMRK}, {"inpck", INPCK},   {"istrip", ISTRIP},
    {"inlcr", INLCR},   {"igncr", IGNCR},   {"icrnl", ICRNL},
#ifdef IUCLC
    {"iuclc", IUCLC},
#endif
    {"ixon", IXON},     {"ixany", IXANY},   {"ixoff", IXOFF},
#ifdef IMAXBEL
    {"imaxbel", IMAXBEL},
#endif
#ifdef IUTF8
    {"iutf8", IUTF8},
#endif
};

constexpr FlagBit kOutput[] = {
    {"opost", OPOST},
#ifdef OLCUC
    {"olcuc", OLCUC},
#endif
    {"onlcr", ONLCR},  {"ocrnl", OCRNL},  {"onocr", ONOCR},
    {"onlret", ONLRET},
#ifdef OFILL
    {"ofill", OFILL},  {"ofdel", OFDEL},
#endif
};

// CSIZE — двобітове поле, а не прапорець: його друкуємо окремо.
constexpr FlagBit kControl[] = {
    {"cstopb", CSTOPB}, {"cread", CREAD},   {"parenb", PARENB},
    {"parodd", PARODD}, {"hupcl", HUPCL},   {"clocal", CLOCAL},
#ifdef CRTSCTS
    {"crtscts", CRTSCTS},
#endif
#ifdef CMSPAR
    {"cmspar", CMSPAR},
#endif
};

constexpr FlagBit kLocal[] = {
    {"isig", ISIG}, {"icanon", ICANON},
#ifdef XCASE
    {"xcase", XCASE},
#endif
    {"echo", ECHO}, {"echoe", ECHOE}, {"echok", ECHOK}, {"echonl", ECHONL},
    {"noflsh", NOFLSH}, {"tostop", TOSTOP},
#ifdef ECHOCTL
    {"echoctl", ECHOCTL},
#endif
#ifdef ECHOPRT
    {"echoprt", ECHOPRT},
#endif
#ifdef ECHOKE
    {"echoke", ECHOKE},
#endif
#ifdef FLUSHO
    {"flusho", FLUSHO},
#endif
#ifdef PENDIN
    {"pendin", PENDIN},
#endif
    {"iexten", IEXTEN},
#ifdef EXTPROC
    {"extproc", EXTPROC},
#endif
};

constexpr CharSlot kChars[] = {
    {"intr", VINTR},  {"quit", VQUIT},  {"erase", VERASE}, {"kill", VKILL},
    {"eof", VEOF},    {"eol", VEOL},
#ifdef VEOL2
    {"eol2", VEOL2},
#endif
    {"start", VSTART}, {"stop", VSTOP}, {"susp", VSUSP},
#ifdef VREPRINT
    {"rprnt", VREPRINT},
#endif
#ifdef VWERASE
    {"werase", VWERASE},
#endif
#ifdef VLNEXT
    {"lnext", VLNEXT},
#endif
#ifdef VDISCARD
    {"discard", VDISCARD},
#endif
};

struct BaudRow {
    speed_t code;
    unsigned long rate;
};

constexpr BaudRow kBauds[] = {
    {B0, 0},       {B50, 50},       {B75, 75},       {B110, 110},
    {B134, 134},   {B150, 150},     {B200, 200},     {B300, 300},
    {B600, 600},   {B1200, 1200},   {B1800, 1800},   {B2400, 2400},
    {B4800, 4800}, {B9600, 9600},   {B19200, 19200}, {B38400, 38400},
#ifdef B57600
    {B57600, 57600},
#endif
#ifdef B115200
    {B115200, 115200},
#endif
#ifdef B230400
    {B230400, 230400},
#endif
#ifdef B460800
    {B460800, 460800},
#endif
#ifdef B921600
    {B921600, 921600},
#endif
#ifdef B1000000
    {B1000000, 1000000},
#endif
#ifdef B2000000
    {B2000000, 2000000},
#endif
#ifdef B4000000
    {B4000000, 4000000},
#endif
};

std::string join(std::span<const FlagBit> table, tcflag_t value)
{
    std::string out;
    int in_row = 0;

    for (const FlagBit& f : table) {
        if (in_row == 6) {
            out += "\n  ";
            in_row = 0;
        } else if (!out.empty()) {
            out += ' ';
        }
        if ((value & f.bit) == 0)
            out += '-';
        out += f.stty;
        ++in_row;
    }
    return out;
}

// Витягує багатобітове поле (CRDLY, TABDLY…): зсув рахуємо з маски,
// щоб не зашивати його руками.
constexpr unsigned field_value(tcflag_t value, tcflag_t mask) noexcept
{
    unsigned shift = 0;
    while (mask != 0 && (mask & 1u) == 0) {
        mask >>= 1;
        ++shift;
    }
    return static_cast<unsigned>((value >> shift) & mask);
}

std::string_view csize_name(tcflag_t c) noexcept
{
    switch (c & CSIZE) {
    case CS5: return "cs5";
    case CS6: return "cs6";
    case CS7: return "cs7";
    default:  return "cs8";
    }
}

std::string char_name(cc_t v)
{
    if (v == 0)
        return "<undef>";                      // _POSIX_VDISABLE
    if (v == 0x7F)
        return "^?";
    if (v < 0x20)
        return std::format("^{}", static_cast<char>(v + 64));
    return std::format("'{}'", static_cast<char>(v));
}

}  // namespace

std::span<const FlagBit> input_flags() noexcept { return kInput; }
std::span<const FlagBit> output_flags() noexcept { return kOutput; }
std::span<const FlagBit> control_flags() noexcept { return kControl; }
std::span<const FlagBit> local_flags() noexcept { return kLocal; }
std::span<const CharSlot> special_chars() noexcept { return kChars; }

unsigned long baud_rate(const termios& t) noexcept
{
    const speed_t code = cfgetospeed(&t);

#ifdef BOTHER
    // BOTHER: швидкість задано числом у c_ospeed, а не кодом із CBAUD —
    // так виставляють 31250 бод для MIDI чи 250000 для DMX512.
    if (code == BOTHER)
        return static_cast<unsigned long>(t.c_ospeed);
#endif
    for (const BaudRow& row : kBauds)
        if (row.code == code)
            return row.rate;
    return 0;
}

std::string describe(const termios& t)
{
    std::string out = std::format("швидкість {} бод; лінійна дисципліна {}\n\n",
                                  baud_rate(t), static_cast<int>(t.c_line));

    out += std::format("c_iflag = {:#010x}\n  {}\n",
                       t.c_iflag, join(input_flags(), t.c_iflag));
    out += std::format("c_oflag = {:#010x}\n  {}\n",
                       t.c_oflag, join(output_flags(), t.c_oflag));
    // Затримки виводу — спадок телетайпів: поля, а не окремі біти.
    out += std::format("  затримки: nl{} cr{} tab{} bs{} vt{} ff{}\n",
                       field_value(t.c_oflag, NLDLY), field_value(t.c_oflag, CRDLY),
                       field_value(t.c_oflag, TABDLY), field_value(t.c_oflag, BSDLY),
                       field_value(t.c_oflag, VTDLY), field_value(t.c_oflag, FFDLY));
    out += std::format("c_cflag = {:#010x}\n  {} {}\n",
                       t.c_cflag, csize_name(t.c_cflag),
                       join(control_flags(), t.c_cflag));
    out += std::format("c_lflag = {:#010x}\n  {}\n",
                       t.c_lflag, join(local_flags(), t.c_lflag));

    out += "c_cc:\n";
    for (const CharSlot& c : special_chars())
        out += std::format("  {:<8} {}\n", c.stty, char_name(t.c_cc[c.index]));
    out += std::format("  {:<8} {}\n", "min", static_cast<unsigned>(t.c_cc[VMIN]));
    out += std::format("  {:<8} {} (× 0.1 с)\n", "time",
                       static_cast<unsigned>(t.c_cc[VTIME]));
    return out;
}

std::string diagnose(const termios& t)
{
    std::string out;

    if ((t.c_lflag & ECHO) == 0)
        out += "сліпий термінал: знято ECHO — набране не видно  →  stty echo\n";
    if ((t.c_lflag & ICANON) == 0)
        out += "немає редагування рядка: знято ICANON — Backspace друкується "
               "як ^?  →  stty icanon\n";
    if ((t.c_lflag & ISIG) == 0)
        out += "мертві Ctrl+C/Ctrl+Z: знято ISIG — байти йдуть як дані  →  stty isig\n";
    if ((t.c_oflag & OPOST) == 0 || (t.c_oflag & ONLCR) == 0)
        out += "ефект сходів: знято OPOST або ONLCR — \\n не розгортається "
               "в \\r\\n  →  stty opost onlcr\n";
    if ((t.c_iflag & ICRNL) == 0 && (t.c_iflag & IGNCR) == 0)
        out += "мертвий Enter: знято ICRNL — оболонка чекає \\n, а клавіша шле "
               "\\r  →  Ctrl+J, потім stty icrnl\n";
    if ((t.c_iflag & IGNCR) != 0)
        out += "мертвий Enter: стоїть IGNCR — усі \\r знищуються ядром  →  stty -igncr\n";
    if ((t.c_iflag & ISTRIP) != 0)
        out += "побитий UTF-8: стоїть ISTRIP — старший біт кожного байта "
               "відсікається  →  stty -istrip\n";
    if ((t.c_cflag & CREAD) == 0)
        out += "лінія глуха: знято CREAD — приймач не бере байтів  →  stty cread\n";

    return out;
}

}  // namespace tty
