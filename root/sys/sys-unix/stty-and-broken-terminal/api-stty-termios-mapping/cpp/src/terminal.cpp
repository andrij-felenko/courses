#include "terminal.hpp"

#include <cerrno>
#include <cstddef>
#include <cstring>

#include <signal.h>
#include <unistd.h>

namespace tty {
namespace {

std::error_code last_error() noexcept
{
    return std::error_code(errno, std::generic_category());
}

// Обробник сигналу не має ні аргументів, ні контексту — лише статика.
RawMode* g_mode = nullptr;
volatile std::sig_atomic_t g_resized = 0;

int install(int signo, void (*handler)(int), int flags) noexcept
{
    struct sigaction sa {};
    sa.sa_handler = handler;
    // Поки працює обробник, решта сигналів чекає: інакше SIGWINCH
    // посеред відновлення termios дав би вкладений виклик.
    sigfillset(&sa.sa_mask);
    sa.sa_flags = flags;
    return sigaction(signo, &sa, nullptr);
}

void resend(int signo) noexcept
{
    // Самогубство тим самим сигналом: оболонка має побачити справжню
    // причину смерті, а не рівний _exit(1).
    struct sigaction sa {};
    sigemptyset(&sa.sa_mask);
    sa.sa_handler = SIG_DFL;
    sigaction(signo, &sa, nullptr);

    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, signo);
    sigprocmask(SIG_UNBLOCK, &set, nullptr);

    raise(signo);
}

void fatal_handler(int signo)
{
    const int saved_errno = errno;

    if (g_mode != nullptr)
        g_mode->restore();
    resend(signo);

    errno = saved_errno;
}

void tstp_handler(int signo)
{
    const int saved_errno = errno;

    if (g_mode != nullptr)
        g_mode->restore();
    resend(signo);          // ядро спиняє процес рівно тут

    // Сюди повертаємось після fg: обробник довелося скинути на SIG_DFL,
    // тож ставимо свій назад і повертаємо власний режим термінала.
    install(signo, tstp_handler, 0);
    if (g_mode != nullptr)
        g_mode->reapply();
    g_resized = 1;          // хай головний цикл перемалює екран

    errno = saved_errno;
}

void cont_handler(int)
{
    const int saved_errno = errno;

    // Якщо процес зупинили не нашим Ctrl+Z (наприклад, kill -STOP),
    // сирий режим доводиться повертати вже тут.
    if (g_mode != nullptr && !g_mode->active())
        g_mode->reapply();
    g_resized = 1;

    errno = saved_errno;
}

void winch_handler(int)
{
    // Єдина дозволена дія — прапорець: ioctl і перемальовування робить
    // головний цикл.
    g_resized = 1;
}

}  // namespace

std::expected<termios, std::error_code> attributes(int fd)
{
    termios t{};
    if (tcgetattr(fd, &t) < 0)
        return std::unexpected(last_error());
    return t;
}

termios make_sane(termios t) noexcept
{
    t.c_iflag |= (BRKINT | ICRNL | IXON);
#ifdef IMAXBEL
    t.c_iflag |= IMAXBEL;
#endif
#ifdef IUTF8
    t.c_iflag |= IUTF8;
#endif
    t.c_iflag &= ~static_cast<tcflag_t>(IGNBRK | INLCR | IGNCR | IXOFF | IXANY |
                                        IGNPAR | PARMRK | INPCK | ISTRIP);

    t.c_oflag |= (OPOST | ONLCR);
    t.c_oflag &= ~static_cast<tcflag_t>(OCRNL | ONOCR | ONLRET |
                                        NLDLY | CRDLY | TABDLY |
                                        BSDLY | VTDLY | FFDLY);

    t.c_cflag |= (CREAD | CLOCAL);
    t.c_cflag &= ~static_cast<tcflag_t>(PARENB | PARODD | CSTOPB | CSIZE);
    t.c_cflag |= CS8;

    t.c_lflag |= (ISIG | ICANON | IEXTEN | ECHO | ECHOE | ECHOK);
#ifdef ECHOCTL
    t.c_lflag |= ECHOCTL;
#endif
#ifdef ECHOKE
    t.c_lflag |= ECHOKE;
#endif
    t.c_lflag &= ~static_cast<tcflag_t>(ECHONL | NOFLSH | TOSTOP);

    t.c_cc[VINTR] = 0x03;   // ^C
    t.c_cc[VQUIT] = 0x1C;   // ^\
    t.c_cc[VERASE] = 0x7F;  // ^?
    t.c_cc[VKILL] = 0x15;   // ^U
    t.c_cc[VEOF] = 0x04;    // ^D
    t.c_cc[VSTART] = 0x11;  // ^Q
    t.c_cc[VSTOP] = 0x13;   // ^S
    t.c_cc[VSUSP] = 0x1A;   // ^Z
    t.c_cc[VEOL] = 0x00;    // _POSIX_VDISABLE
    t.c_cc[VMIN] = 1;
    t.c_cc[VTIME] = 0;
    return t;
}

termios make_cooked(termios t) noexcept
{
    // cooked чіпає менше за sane: повертає обробку, але не переписує
    // спецсимволи, які користувач міг змінити свідомо.
    t.c_iflag |= (ICRNL | IXON | BRKINT);
    t.c_oflag |= (OPOST | ONLCR);
    t.c_lflag |= (ICANON | ISIG | ECHO | ECHOE | ECHOK | IEXTEN);
    t.c_cc[VMIN] = 1;
    t.c_cc[VTIME] = 0;
    return t;
}

termios make_raw(termios t) noexcept
{
    // Прозорий 8-бітний канал: ні нормалізації CR/NL, ні XON/XOFF,
    // ні відлуння, ні буферизації рядків, ні сигналів із клавіш.
    t.c_iflag &= ~static_cast<tcflag_t>(IGNBRK | BRKINT | PARMRK | ISTRIP |
                                        INLCR | IGNCR | ICRNL | IXON);
    t.c_oflag &= ~static_cast<tcflag_t>(OPOST);
    t.c_lflag &= ~static_cast<tcflag_t>(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
    t.c_cflag &= ~static_cast<tcflag_t>(CSIZE | PARENB);
    t.c_cflag |= CS8;
    t.c_cc[VMIN] = 1;
    t.c_cc[VTIME] = 0;
    return t;
}

termios make_noecho(termios t) noexcept
{
    // Канонічний режим лишається — рядок редагує ядро; гасне лише відлуння.
    t.c_lflag &= ~static_cast<tcflag_t>(ECHO | ECHOE | ECHOK);
    t.c_lflag |= ECHONL;   // перевід рядка по Enter усе-таки показуємо
    return t;
}

Status apply_verified(int fd, int optional_actions, const termios& want)
{
    if (tcsetattr(fd, optional_actions, &want) < 0)
        return std::unexpected(last_error());

    const auto got = attributes(fd);
    if (!got)
        return std::unexpected(got.error());

    const auto differs = [](tcflag_t a, tcflag_t b, tcflag_t mask) {
        return ((a ^ b) & mask) != 0;
    };
    // c_cflag звіряємо лише за кадром даних: швидкість і модемні лінії
    // на псевдотерміналі ядро мовчки ігнорує, і це не поломка.
    const bool bad =
        differs(want.c_iflag, got->c_iflag, ~static_cast<tcflag_t>(0)) ||
        differs(want.c_oflag, got->c_oflag, ~static_cast<tcflag_t>(0)) ||
        differs(want.c_lflag, got->c_lflag, ~static_cast<tcflag_t>(0)) ||
        differs(want.c_cflag, got->c_cflag,
                static_cast<tcflag_t>(CSIZE | PARENB | PARODD | CSTOPB | CREAD)) ||
        std::memcmp(want.c_cc, got->c_cc, sizeof want.c_cc) != 0;

    if (bad)
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    return {};
}

void emulator_reset(int fd) noexcept
{
    // Прапорці termios не повернуть екран: кінцевий автомат емулятора
    // живе окремо й нічого не знає про смерть програми.
    static constexpr char kSeq[] =
        "\033[?25h"                                    // показати курсор
        "\033[0m"                                      // скинути SGR
        "\033(B\017"                                   // G0 = US-ASCII, Shift-In
        "\033[?2004l"                                  // обрамлена вставка геть
        "\033[?1000l\033[?1002l\033[?1003l\033[?1006l" // миша геть
        "\033[?2026l"                                  // синхронний кадр закрити
        "\033[?1049l"                                  // вийти з альт-екрана
        "\033[r";                                      // межі прокрутки зняти

    const char* p = kSeq;
    std::size_t left = sizeof kSeq - 1;

    while (left > 0) {
        const ssize_t n = ::write(fd, p, left);
        if (n < 0) {
            if (errno == EINTR)
                continue;
            return;   // ми можемо бути в обробнику сигналу — більше нічого
        }
        p += n;
        left -= static_cast<std::size_t>(n);
    }
}

RawMode::RawMode(int fd, std::uint8_t vmin, std::uint8_t vtime) : fd_{fd}
{
    if (tcgetattr(fd_, &saved_) < 0)
        throw std::system_error(last_error(), "tcgetattr");

    raw_ = make_raw(saved_);
    raw_.c_cc[VMIN] = vmin;
    raw_.c_cc[VTIME] = vtime;

    // TCSAFLUSH: усе набране до перемикання викидаємо — інакше воно
    // прочитається вже за іншими правилами.
    if (tcsetattr(fd_, TCSAFLUSH, &raw_) < 0)
        throw std::system_error(last_error(), "tcsetattr(raw)");

    termios got{};
    if (tcgetattr(fd_, &got) < 0)
        throw std::system_error(last_error(), "tcgetattr");
    if ((got.c_lflag & (ICANON | ECHO | ISIG)) != 0 || (got.c_oflag & OPOST) != 0)
        throw std::system_error(std::make_error_code(std::errc::invalid_argument),
                                "ядро взяло сирий режим не повністю");
    active_ = 1;
}

RawMode::~RawMode()
{
    restore();
}

void RawMode::restore() noexcept
{
    if (active_ == 0)
        return;
    active_ = 0;
    emulator_reset(fd_);
    // TCSANOW, а не TCSADRAIN: якщо вивід зупинено по Ctrl+S, черга
    // ніколи не спорожніє, і TCSADRAIN зависне назавжди.
    tcsetattr(fd_, TCSANOW, &saved_);
}

void RawMode::reapply() noexcept
{
    if (tcsetattr(fd_, TCSANOW, &raw_) == 0)
        active_ = 1;
}

SignalGuard::SignalGuard(RawMode& mode)
{
    g_mode = &mode;

    for (int signo : {SIGINT, SIGQUIT, SIGTERM, SIGHUP, SIGABRT, SIGSEGV,
                      SIGBUS, SIGPIPE})
        install(signo, fatal_handler, 0);

    install(SIGTSTP, tstp_handler, 0);
    install(SIGCONT, cont_handler, SA_RESTART);
    // Свідомо без SA_RESTART: read() має повернути EINTR, щоб цикл
    // помітив зміну розміру, а не висів у ядрі.
    install(SIGWINCH, winch_handler, 0);
}

SignalGuard::~SignalGuard()
{
    for (int signo : {SIGINT, SIGQUIT, SIGTERM, SIGHUP, SIGABRT, SIGSEGV,
                      SIGBUS, SIGPIPE, SIGTSTP, SIGCONT, SIGWINCH})
        install(signo, SIG_DFL, 0);
    g_mode = nullptr;
}

bool SignalGuard::window_resized() noexcept
{
    if (g_resized == 0)
        return false;
    g_resized = 0;
    return true;
}

ReadResult read_byte(int fd, unsigned char& out) noexcept
{
    const ssize_t n = ::read(fd, &out, 1);

    if (n == 1)
        return ReadResult::Byte;
    if (n == 0)
        return ReadResult::Eof;
    if (errno == EINTR)
        return ReadResult::Interrupted;
    return ReadResult::Error;
}

}  // namespace tty
