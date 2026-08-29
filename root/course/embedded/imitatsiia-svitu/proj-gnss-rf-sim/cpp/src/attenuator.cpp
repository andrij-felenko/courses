#include "attenuator.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cmath>
#include <cstring>
#include <format>
#include <iostream>
#include <thread>
#include <utility>

#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

namespace gnss {
namespace {

constexpr double kAckTimeoutMs = 250.0;
constexpr int    kMaxRetries   = 3;

double now_ms() noexcept
{
    using namespace std::chrono;
    return duration<double, std::milli>{steady_clock::now().time_since_epoch()}.count();
}

std::string errno_text(std::string_view what)
{
    return std::format("{}: {}", what, std::strerror(errno));
}

bool configure(int fd)
{
    termios tio{};
    if (tcgetattr(fd, &tio) != 0) return false;

    cfmakeraw(&tio);                     // прилад чекає байти, а не рядки термінала
    cfsetispeed(&tio, B115200);
    cfsetospeed(&tio, B115200);
    tio.c_cflag |= CLOCAL | CREAD;
    tio.c_cflag &= ~static_cast<tcflag_t>(CRTSCTS | PARENB | CSTOPB);
    tio.c_cc[VMIN]  = 0;
    tio.c_cc[VTIME] = 0;                 // читання неблокуюче, чекає автомат

    if (tcsetattr(fd, TCSANOW, &tio) != 0) return false;
    tcflush(fd, TCIOFLUSH);
    return true;
}

}  // namespace

std::expected<SerialPort, std::string> SerialPort::open(std::string_view device)
{
    const std::string path{device};
    const int fd = ::open(path.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) return std::unexpected(errno_text(path));
    if (!configure(fd)) {
        auto message = errno_text("налаштування порту");
        ::close(fd);
        return std::unexpected(std::move(message));
    }
    return SerialPort{fd};
}

SerialPort::SerialPort(SerialPort&& other) noexcept : fd_{std::exchange(other.fd_, -1)} {}

SerialPort& SerialPort::operator=(SerialPort&& other) noexcept
{
    if (this != &other) {
        if (fd_ >= 0) ::close(fd_);
        fd_ = std::exchange(other.fd_, -1);
    }
    return *this;
}

SerialPort::~SerialPort()
{
    if (fd_ >= 0) ::close(fd_);
}

std::expected<std::size_t, std::string> SerialPort::write_some(std::span<const char> data) noexcept
{
    const ssize_t written = ::write(fd_, data.data(), data.size());
    if (written >= 0) return static_cast<std::size_t>(written);
    if (errno == EAGAIN || errno == EWOULDBLOCK) return std::size_t{0};
    return std::unexpected(errno_text("write"));
}

std::expected<std::size_t, std::string> SerialPort::read_some(std::span<char> buffer) noexcept
{
    const ssize_t got = ::read(fd_, buffer.data(), buffer.size());
    if (got >= 0) return static_cast<std::size_t>(got);
    if (errno == EAGAIN || errno == EWOULDBLOCK) return std::size_t{0};
    return std::unexpected(errno_text("read"));
}

void SerialPort::flush_input() noexcept
{
    tcflush(fd_, TCIFLUSH);
}

std::expected<Attenuator, std::string> Attenuator::connect(std::string_view device)
{
    auto port = SerialPort::open(device);
    if (!port) return std::unexpected(port.error());

    // Синхронний обмін лише тут: на етапі відкриття чекати ще можна.
    static constexpr std::string_view kQuery = "*IDN?\n";
    if (auto sent = port->write_some(kQuery); !sent) return std::unexpected(sent.error());

    std::string answer;
    const double until = now_ms() + 1000.0;
    while (now_ms() < until && answer.find('\n') == std::string::npos) {
        std::array<char, 64> chunk{};
        auto got = port->read_some(chunk);
        if (!got) return std::unexpected(got.error());
        if (*got > 0) answer.append(chunk.data(), *got);
        else std::this_thread::sleep_for(std::chrono::milliseconds{5});
    }
    if (answer.empty()) return std::unexpected("атенюатор мовчить на *IDN?");
    std::cerr << std::format("атенюатор: {}\n", answer.substr(0, answer.find_first_of("\r\n")));

    Attenuator attenuator{std::move(*port)};

    // Стартуємо з максимального загасання: доки рівень не порахований, вхідний
    // малошумний підсилювач приймача не повинен бачити нічого.
    attenuator.current_db_ = 0.0;
    if (auto ok = attenuator.request(kMaxAttenuationDb); !ok) return std::unexpected(ok.error());
    while (attenuator.busy()) {
        attenuator.poll();
        if (attenuator.failed()) return std::unexpected("атенюатор не став у безпечний рівень");
    }
    return attenuator;
}

Attenuator::~Attenuator()
{
    if (state_ == State::Failed) return;
    // Останній рух — знову в максимум, щоб від'єднання не лишило приймач
    // під повним рівнем із SDR.
    const std::string safe = std::format(":ATT:VAL {:.2f}\n", kMaxAttenuationDb);
    (void)port_.write_some(safe);
}

std::expected<void, std::string> Attenuator::request(double db)
{
    if (state_ == State::Failed) return std::unexpected("атенюатор непрацездатний");
    if (state_ != State::Idle)   return std::unexpected("попередня команда ще в дорозі");

    db = std::clamp(db, 0.0, kMaxAttenuationDb);
    db = std::round(db / kAttenuationStepDb) * kAttenuationStepDb;   // прилад крокує по 0.25 дБ
    if (std::abs(db - current_db_) < kAttenuationStepDb / 2.0) return {};

    pending_db_ = db;
    // «;*OPC?» змушує прилад підтвердити, що крок відпрацював — без цього ми не
    // знаємо, коли рівень справді змінився.
    tx_ = std::format(":ATT:VAL {:.2f};*OPC?\n", db);
    tx_sent_ = 0;
    rx_.clear();
    retries_ = 0;
    state_ = State::Sending;
    return {};
}

void Attenuator::restart_command()
{
    tx_sent_ = 0;
    rx_.clear();
    port_.flush_input();
    state_ = State::Sending;
}

void Attenuator::poll()
{
    if (state_ == State::Idle || state_ == State::Failed) return;

    if (state_ == State::Sending) {
        while (tx_sent_ < tx_.size()) {
            auto written = port_.write_some(std::span{tx_}.subspan(tx_sent_));
            if (!written) {
                std::cerr << written.error() << '\n';
                state_ = State::Failed;
                return;
            }
            if (*written == 0) return;        // буфер драйвера повний, доб'ємо потім
            tx_sent_ += *written;
        }
        ++commands_;
        deadline_ms_ = now_ms() + kAckTimeoutMs;
        state_ = State::WaitingAck;
    }

    if (state_ == State::WaitingAck) {
        for (;;) {
            std::array<char, 64> chunk{};
            auto got = port_.read_some(chunk);
            if (!got) {
                std::cerr << got.error() << '\n';
                state_ = State::Failed;
                return;
            }
            if (*got == 0) break;
            rx_.append(chunk.data(), *got);

            if (const auto nl = rx_.find('\n'); nl != std::string::npos) {
                const std::string_view answer{rx_.data(), nl};
                if (answer.find('1') != std::string_view::npos) {
                    current_db_ = pending_db_;
                    state_ = State::Idle;
                } else {
                    std::cerr << std::format("атенюатор відповів «{}» замість підтвердження\n",
                                             answer);
                    state_ = State::Failed;
                }
                return;
            }
            if (rx_.size() > 256) rx_.clear();     // сміття без переводу рядка
        }

        if (now_ms() > deadline_ms_) {
            ++timeouts_;
            if (++retries_ >= kMaxRetries) {
                std::cerr << std::format("атенюатор не підтвердив {:.2f} дБ після {} спроб\n",
                                         pending_db_, kMaxRetries);
                state_ = State::Failed;
            } else {
                restart_command();
            }
        }
    }
}

}  // namespace gnss
