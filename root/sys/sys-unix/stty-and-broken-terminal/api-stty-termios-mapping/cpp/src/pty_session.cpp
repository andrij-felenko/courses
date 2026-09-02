#include "pty_session.hpp"

#include "terminal.hpp"

#include <array>
#include <cerrno>
#include <cstdio>
#include <print>
#include <utility>

#include <fcntl.h>
#include <poll.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>

namespace tty {
namespace {

std::error_code last_error() noexcept
{
    return std::error_code(errno, std::generic_category());
}

bool write_all(int fd, std::span<const unsigned char> data) noexcept
{
    while (!data.empty()) {
        const ssize_t n = ::write(fd, data.data(), data.size());
        if (n < 0) {
            if (errno == EINTR)
                continue;
            return false;
        }
        data = data.subspan(static_cast<std::size_t>(n));
    }
    return true;
}

enum class Drain { Empty, Eof, Failed };

// Вичитує все, що вже лежить у буфері ядра, до EAGAIN. Без цього epoll
// у режимі EPOLLET більше ніколи не розбудить процес.
template <typename Sink>
Drain drain(int fd, Sink&& sink)
{
    std::array<unsigned char, 4096> buf{};

    for (;;) {
        const ssize_t n = ::read(fd, buf.data(), buf.size());
        if (n > 0) {
            sink(std::span<const unsigned char>(buf.data(),
                                                static_cast<std::size_t>(n)));
            continue;
        }
        if (n == 0)
            return Drain::Eof;
        if (errno == EINTR)
            continue;
        if (errno == EAGAIN || errno == EWOULDBLOCK)
            return Drain::Empty;
        return Drain::Failed;
    }
}

bool set_nonblock(int fd, bool on) noexcept
{
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0)
        return false;
    // O_NONBLOCK старший за VMIN/VTIME: read() на порожньому буфері
    // одразу віддає EAGAIN і не запускає жодного таймера.
    const int want = on ? (flags | O_NONBLOCK) : (flags & ~O_NONBLOCK);
    return ::fcntl(fd, F_SETFL, want) == 0;
}

void copy_winsize(int from, int to) noexcept
{
    winsize ws{};
    if (::ioctl(from, TIOCGWINSZ, &ws) == 0)
        (void)::ioctl(to, TIOCSWINSZ, &ws);
}

void report_queues(int master)
{
    int pending_in = -1;
    int pending_out = -1;

    (void)::ioctl(master, FIONREAD, &pending_in);
    (void)::ioctl(master, TIOCOUTQ, &pending_out);
    std::print(stderr, "\r\n[pty] FIONREAD = {}, TIOCOUTQ = {}\r\n",
               pending_in, pending_out);
}

}  // namespace

void Fd::reset(int fd) noexcept
{
    if (fd_ >= 0 && fd_ != fd)
        ::close(fd_);
    fd_ = fd;
}

std::expected<PtyMaster, std::error_code> PtyMaster::open()
{
    Fd master{::posix_openpt(O_RDWR | O_NOCTTY)};
    if (!master)
        return std::unexpected(last_error());

    if (::grantpt(master.get()) < 0 || ::unlockpt(master.get()) < 0)
        return std::unexpected(last_error());

    std::string slave(64, '\0');
    if (const int rc = ::ptsname_r(master.get(), slave.data(), slave.size()); rc != 0)
        return std::unexpected(std::error_code(rc, std::generic_category()));
    slave.resize(std::char_traits<char>::length(slave.c_str()));

    // Пакетний режим — лише на ведучому дескрипторі. Без нього ведучий
    // ніколи не дізнається ні про tcflush(), ні про ^S на тому боці.
    int mode = 1;
    if (::ioctl(master.get(), TIOCPKT, &mode) < 0)
        return std::unexpected(last_error());

    return PtyMaster{std::move(master), std::move(slave)};
}

std::expected<pid_t, std::error_code> PtyMaster::spawn(std::span<char* const> argv)
{
    if (argv.empty())
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));

    copy_winsize(STDIN_FILENO, fd_.get());

    const pid_t pid = ::fork();
    if (pid < 0)
        return std::unexpected(last_error());

    if (pid == 0) {
        // Дитина: жодних винятків і жодних деструкторів — тільки виклики,
        // після яких або execvp, або _exit.
        ::close(fd_.get());
        if (::setsid() < 0)
            ::_exit(127);

        const int slave = ::open(slave_.c_str(), O_RDWR);
        if (slave < 0)
            ::_exit(127);
        // Ведений стає контрольним терміналом сесії — інакше не працюють
        // ні ^C, ні керування завданнями.
        if (::ioctl(slave, TIOCSCTTY, 0) < 0)
            ::_exit(127);
        if (::dup2(slave, STDIN_FILENO) < 0 || ::dup2(slave, STDOUT_FILENO) < 0 ||
            ::dup2(slave, STDERR_FILENO) < 0)
            ::_exit(127);
        if (slave > STDERR_FILENO)
            ::close(slave);

        ::execvp(argv[0], argv.data());
        ::_exit(127);
    }

    child_ = pid;
    return pid;
}

void PtyMaster::handle_packet(std::span<const unsigned char> packet)
{
    if (packet.empty())
        return;

    const unsigned char control = packet.front();

    if (control == 0) {
        // Нуль у першому байті — далі звичайні вихідні дані веденого.
        if (!write_all(STDOUT_FILENO, packet.subspan(1)))
            std::print(stderr, "\r\n[pty] write(stdout) не вдався\r\n");
        return;
    }

    // Ненульовий байт стану приходить сам-один: це подія лінії.
    if (has(control, PacketFlag::FlushRead)) {
        std::print(stderr, "\r\n[pty] FLUSHREAD: вхідну чергу веденого скинуто\r\n");
        report_queues(fd_.get());
    }
    if (has(control, PacketFlag::FlushWrite))
        std::print(stderr, "\r\n[pty] FLUSHWRITE: вихідну чергу веденого скинуто\r\n");
    if (has(control, PacketFlag::Stop)) {
        flow_stopped_ = true;   // ^S: більше не наливаємо в нього ввід
        std::print(stderr, "\r\n[pty] STOP: вивід зупинено (^S)\r\n");
    }
    if (has(control, PacketFlag::Start)) {
        flow_stopped_ = false;
        std::print(stderr, "\r\n[pty] START: вивід поновлено (^Q)\r\n");
    }
    if (has(control, PacketFlag::NoStop))
        std::print(stderr, "\r\n[pty] NOSTOP: ^S/^Q більше не керують потоком\r\n");
    if (has(control, PacketFlag::DoStop))
        std::print(stderr, "\r\n[pty] DOSTOP: ^S/^Q знову стандартні\r\n");
    if (has(control, PacketFlag::Ioctl)) {
        // На ведучому дескрипторі TCGETS віддає termios веденого боку —
        // саме це й треба перечитати після такого пакета.
        if (const auto t = attributes(fd_.get()); t)
            std::print(stderr,
                       "\r\n[pty] termios веденого змінено: lflag = {:#010x} "
                       "(echo {}, icanon {})\r\n",
                       t->c_lflag, (t->c_lflag & ECHO) ? "є" : "нема",
                       (t->c_lflag & ICANON) ? "є" : "нема");
    }
}

std::expected<int, std::error_code> PtyMaster::run()
{
    try {
        // Власний термінал — у сирий режим: усю обробку тепер робить
        // лінійна дисципліна веденого.
        RawMode raw{STDIN_FILENO};
        SignalGuard guard{raw};

        // Обидва дескриптори неблокуючі: інакше write() у повний буфер
        // PTY дав би класичний дедлок «обидва чекають одне одного».
        set_nonblock(STDIN_FILENO, true);
        set_nonblock(fd_.get(), true);

        while (!eof_) {
            pollfd pfd[2]{};
            pfd[0].fd = STDIN_FILENO;
            pfd[0].events = flow_stopped_ ? 0 : POLLIN;
            pfd[1].fd = fd_.get();
            pfd[1].events = POLLIN;

            if (::poll(pfd, 2, -1) < 0) {
                if (errno == EINTR) {
                    if (SignalGuard::window_resized())
                        copy_winsize(STDIN_FILENO, fd_.get());
                    continue;
                }
                return std::unexpected(last_error());
            }

            if (pfd[0].revents & (POLLIN | POLLHUP)) {
                const auto state = drain(STDIN_FILENO,
                                         [this](std::span<const unsigned char> chunk) {
                                             write_all(fd_.get(), chunk);
                                         });
                if (state == Drain::Failed)
                    return std::unexpected(last_error());
            }
            if (pfd[1].revents & (POLLIN | POLLHUP | POLLERR)) {
                const auto state = drain(fd_.get(),
                                         [this](std::span<const unsigned char> pkt) {
                                             handle_packet(pkt);
                                         });
                // EIO на ведучому — теж кінець сеансу: ведений закрив
                // останній свій дескриптор.
                if (state == Drain::Eof || (state == Drain::Failed && errno == EIO))
                    eof_ = true;
                else if (state == Drain::Failed)
                    return std::unexpected(last_error());
            }
        }

        set_nonblock(STDIN_FILENO, false);
    } catch (const std::system_error& e) {
        return std::unexpected(e.code());
    }

    int status = 0;
    if (::waitpid(child_, &status, 0) == child_ && WIFEXITED(status))
        return WEXITSTATUS(status);
    return 1;
}

}  // namespace tty
