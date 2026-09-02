#include "serial_link.h"

#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

#include <cerrno>
#include <iostream>
#include <stdexcept>
#include <system_error>
#include <thread>

namespace {

speed_t toSpeed(unsigned baud) {
    switch (baud) {
        case 57600: return B57600;
        case 115200: return B115200;
        default:
            throw std::invalid_argument("радіомодем налаштовуємо лише на 57600 або 115200 бод");
    }
}

// Дескриптор закриється сам, якщо конструктор упаде посеред налаштування термінала.
struct FdGuard {
    int fd;
    ~FdGuard() { if (fd >= 0) ::close(fd); }
    int release() { int f = fd; fd = -1; return f; }
};

}  // namespace

double LinkStats::lossPercent() const {
    const std::uint64_t total = received + lost;
    return total == 0 ? 0.0 : 100.0 * static_cast<double>(lost) / static_cast<double>(total);
}

SerialLink::SerialLink(const std::string& device, unsigned baud) {
    FdGuard guard{::open(device.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK)};
    if (guard.fd < 0) {
        throw std::system_error(errno, std::generic_category(), "не відкрився порт " + device);
    }

    termios tio{};
    if (::tcgetattr(guard.fd, &tio) != 0) {
        throw std::system_error(errno, std::generic_category(), "tcgetattr");
    }
    ::cfmakeraw(&tio);            // жодної обробки символів: у порт іде двійковий кадр
    tio.c_cflag |= CLOCAL | CREAD;
    tio.c_cflag &= ~CRTSCTS;      // SiK-модеми апаратного керування потоком не мають
    tio.c_cc[VMIN] = 0;           // read() повертається негайно, навіть коли байтів немає
    tio.c_cc[VTIME] = 0;
    if (::cfsetispeed(&tio, toSpeed(baud)) != 0 || ::cfsetospeed(&tio, toSpeed(baud)) != 0) {
        throw std::system_error(errno, std::generic_category(), "cfsetspeed");
    }
    if (::tcsetattr(guard.fd, TCSANOW, &tio) != 0) {
        throw std::system_error(errno, std::generic_category(), "tcsetattr");
    }
    ::tcflush(guard.fd, TCIOFLUSH);  // викидаємо все, що модем нашумів до нашого старту

    fd_ = guard.release();
}

SerialLink::~SerialLink() {
    if (fd_ >= 0) ::close(fd_);
}

std::vector<mavlink_message_t> SerialLink::receive() {
    std::vector<mavlink_message_t> out;
    std::uint8_t buf[512];

    for (;;) {
        const ssize_t n = ::read(fd_, buf, sizeof buf);
        if (n < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) break;  // байтів більше немає
            throw std::system_error(errno, std::generic_category(), "read з порту");
        }
        if (n == 0) break;

        for (ssize_t i = 0; i < n; ++i) {
            mavlink_message_t msg;
            mavlink_status_t status;
            if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status) == 1) {
                lockVersion(msg.magic);
                trackSeq(msg);
                out.push_back(msg);
            }
        }
        stats_.parse_errors = mavlink_get_channel_status(MAVLINK_COMM_0)->parse_error;

        if (static_cast<std::size_t>(n) < sizeof buf) break;  // драйвер вичерпано
    }
    return out;
}

void SerialLink::send(const mavlink_message_t& msg) {
    std::uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    const std::uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);

    std::size_t off = 0;
    while (off < len) {
        const ssize_t n = ::write(fd_, buf + off, len - off);
        if (n < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // FIFO модема забито: ефір ще не звільнився після попередньої пачки.
                std::this_thread::sleep_for(std::chrono::milliseconds(2));
                continue;
            }
            throw std::system_error(errno, std::generic_category(), "write у порт");
        }
        off += static_cast<std::size_t>(n);
    }
    ++stats_.sent;
}

void SerialLink::lockVersion(std::uint8_t magic) {
    const MavVersion seen = (magic == MAVLINK_STX) ? MavVersion::V2 : MavVersion::V1;
    if (seen == version_) return;
    // Побачивши v2, передавач фіксуємо на v2 назавжди: поодинокий кадр v1
    // від стороннього компонента не має скидати нас на старий діалект.
    if (version_ == MavVersion::V2 && seen == MavVersion::V1) return;

    version_ = seen;
    mavlink_status_t* chan = mavlink_get_channel_status(MAVLINK_COMM_0);
    if (seen == MavVersion::V2) {
        chan->flags &= ~MAVLINK_STATUS_FLAG_OUT_MAVLINK1;
        std::cout << "[link] борт говорить MAVLink 2 (0xFD) — передавач переведено на v2\n";
    } else {
        chan->flags |= MAVLINK_STATUS_FLAG_OUT_MAVLINK1;
        std::cout << "[link] борт говорить MAVLink 1 (0xFE) — відповідаємо в діалекті v1\n";
    }
}

void SerialLink::trackSeq(const mavlink_message_t& msg) {
    const std::uint16_t key = static_cast<std::uint16_t>(msg.sysid) << 8 | msg.compid;
    ++stats_.received;

    const auto it = last_seq_.find(key);
    if (it != last_seq_.end()) {
        // Втрачені = (seq - попередній - 1) mod 256.
        const std::uint8_t gap = static_cast<std::uint8_t>(msg.seq - it->second - 1);
        stats_.lost += gap;
        it->second = msg.seq;
    } else {
        last_seq_.emplace(key, msg.seq);
    }
}

void SerialLink::resetStatsWindow() {
    stats_.received = 0;
    stats_.lost = 0;
}
