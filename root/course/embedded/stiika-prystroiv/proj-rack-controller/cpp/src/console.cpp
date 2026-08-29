#include "console.hpp"

#include <algorithm>
#include <array>
#include <format>

#include <fcntl.h>
#include <sys/select.h>
#include <termios.h>

Console::Console(int slotId, int mirrorFd) : mirrorFd_{mirrorFd}
{
    const auto path = std::format("/dev/dut-slot-{:02d}-uart", slotId);

    fd_.reset(::open(path.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK | O_CLOEXEC));
    if (!fd_) {
        throwErrno(std::format("не відкривається {}", path));
    }

    configureRaw(slotId);
    flushInput(); // геть усе, що осіло в черзі від попереднього прогону

    log_.reserve(kLogCap);
}

void Console::configureRaw(int slotId)
{
    termios tty{};
    if (::tcgetattr(fd_.get(), &tty) != 0) {
        throwErrno("tcgetattr");
    }

    ::cfsetispeed(&tty, B115200);
    ::cfsetospeed(&tty, B115200);

    // 8N1, приймач увімкнено, модемні лінії ігноруємо: DTR/RTS на налагоджувальній
    // консолі часто заведені на скидання плати, і чекати на DCD немає сенсу.
    tty.c_cflag = static_cast<tcflag_t>((tty.c_cflag & ~static_cast<tcflag_t>(CSIZE)) | CS8);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~static_cast<tcflag_t>(PARENB | PARODD | CSTOPB | CRTSCTS);

    // Сирий режим: без рядкового буфера, без ехо, без сигналів від ^C у потоці.
    tty.c_lflag &= ~static_cast<tcflag_t>(ICANON | ECHO | ECHOE | ECHONL | ISIG | IEXTEN);
    tty.c_iflag &= ~static_cast<tcflag_t>(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK |
                                          ISTRIP | INLCR | IGNCR | ICRNL);
    tty.c_oflag &= ~static_cast<tcflag_t>(OPOST);

    // VMIN=0, VTIME=0 — read() віддає що є й повертається негайно; чеканням
    // керує select(), а не драйвер терміналу.
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 0;

    if (::tcsetattr(fd_.get(), TCSANOW, &tty) != 0) {
        throwErrno("tcsetattr");
    }

    // tcsetattr каже «добре», якщо застосував ХОЧ ЩОСЬ. Дешеві мости USB-UART
    // мовчки підміняють швидкість — звіряємо, що саме вийшло.
    termios check{};
    if (::tcgetattr(fd_.get(), &check) != 0 || ::cfgetospeed(&check) != B115200) {
        throw std::runtime_error{std::format("слот {:02d}: порт не прийняв 115200", slotId)};
    }
}

void Console::flushInput() noexcept
{
    ::tcflush(fd_.get(), TCIFLUSH);
}

void Console::mirror(std::span<const char> data) noexcept
{
    if (mirrorFd_ < 0) {
        return;
    }
    while (!data.empty()) {
        const ssize_t n = ::write(mirrorFd_, data.data(), data.size());
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return; // дзеркало не критичне: лог у пам'яті лишається цілим
        }
        data = data.subspan(static_cast<std::size_t>(n));
    }
}

void Console::appendToLog(std::span<const char> data)
{
    if (data.size() > kLogCap) {
        data = data.last(kLogCap); // один кусок більший за буфер — беремо хвіст
    }
    if (log_.size() + data.size() > kLogCap) {
        const std::size_t drop = log_.size() + data.size() - kLogCap;
        log_.erase(0, drop);
        searchFrom_ = searchFrom_ > drop ? searchFrom_ - drop : 0;
        trimmed_ = true;
    }
    // std::string тримає довжину, тож нульові байти з перехідних рівнів живлення
    // не рвуть лог і не заважають пошуку — на відміну від C-рядка.
    log_.append(data.data(), data.size());
}

std::size_t Console::pump(std::chrono::milliseconds slice)
{
    fd_set readFds;
    FD_ZERO(&readFds);
    FD_SET(fd_.get(), &readFds);

    timeval tv{};
    tv.tv_sec = static_cast<time_t>(slice.count() / 1000);
    tv.tv_usec = static_cast<suseconds_t>((slice.count() % 1000) * 1000);

    const int rc = ::select(fd_.get() + 1, &readFds, nullptr, nullptr, &tv);
    if (rc < 0) {
        if (errno == EINTR) {
            return 0; // сигнал: рішення про зупинку ухвалює цикл вище
        }
        throwErrno("select на консолі слота");
    }
    if (rc == 0) {
        return 0; // у порту тиша
    }

    std::array<char, 512> chunk{};
    const ssize_t n = ::read(fd_.get(), chunk.data(), chunk.size());
    if (n < 0) {
        if (errno == EAGAIN || errno == EINTR) {
            return 0;
        }
        throwErrno("read з консолі слота");
    }
    if (n == 0) {
        // select сказав «готовий», а даних немає. Раз таке буває на межі кадру,
        // але вперте повторення означає, що моста USB-UART від'єднали.
        if (++emptyReads_ >= kEmptyReadsLimit) {
            throw std::runtime_error{"консоль слота зникла — від'єднали міст USB-UART?"};
        }
        return 0;
    }

    emptyReads_ = 0;
    const std::span<const char> data{chunk.data(), static_cast<std::size_t>(n)};
    mirror(data); // стрім наживо, ще до розбору
    appendToLog(data);
    return data.size();
}

std::string_view Console::expect(std::string_view pattern, std::chrono::milliseconds timeout)
{
    if (pattern.empty()) {
        throw std::invalid_argument{"порожній шаблон очікування"};
    }

    // Шукаємо лише в тому, що прийде далі, плюс хвіст завдовжки з шаблон: так
    // збіг не загубиться на межі кусків, а старе не дасть хибного попадання.
    const auto rewind = [&] {
        searchFrom_ = log_.size() >= pattern.size() ? log_.size() - (pattern.size() - 1) : 0;
    };
    rewind();

    const auto deadline = std::chrono::steady_clock::now() + timeout;
    for (;;) {
        if (const auto hit = log_.find(pattern, searchFrom_); hit != std::string::npos) {
            return std::string_view{log_}.substr(hit);
        }
        if (gStopRequested) {
            throw std::runtime_error{"очікування перервано сигналом"};
        }

        const auto now = std::chrono::steady_clock::now();
        if (now >= deadline) {
            throw ConsoleTimeout{std::format("плата не сказала \"{}\" за {} мс", pattern,
                                             timeout.count())};
        }

        // Дрібний квант, щоб сигнал зупинки не чекав до кінця таймауту.
        const auto slice = std::min(
            std::chrono::duration_cast<std::chrono::milliseconds>(deadline - now),
            std::chrono::milliseconds{50});

        rewind();
        pump(slice);
    }
}

void Console::drain(std::chrono::milliseconds duration)
{
    const auto deadline = std::chrono::steady_clock::now() + duration;
    while (!gStopRequested) {
        const auto now = std::chrono::steady_clock::now();
        if (now >= deadline) {
            return;
        }
        pump(std::min(std::chrono::duration_cast<std::chrono::milliseconds>(deadline - now),
                      std::chrono::milliseconds{50}));
    }
}
