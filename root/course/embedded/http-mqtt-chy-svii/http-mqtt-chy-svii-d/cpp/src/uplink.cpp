// uplink.cpp — сокет, ARQ stop-and-wait і спул відкладених кадрів.
#include "uplink.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <netdb.h>
#include <netinet/in.h>
#include <poll.h>
#include <system_error>
#include <unistd.h>

#include "codec.hpp"

namespace telemetry {

namespace {

// Сокет ми навмисно не connect()-имо: показуємо, що на голому UDP чужа
// датаграма прилітає в той самий буфер, і відсіяти її — робота прикладного
// рівня. Порівнюємо родину, порт і адресу, а не байти sockaddr цілком:
// у sockaddr_in є padding, який ніхто не зобов'язаний заповнювати однаково.
bool samePeer(const sockaddr_storage& a, const sockaddr_storage& b) noexcept
{
    if (a.ss_family != b.ss_family) {
        return false;
    }
    if (a.ss_family == AF_INET) {
        const auto& x = reinterpret_cast<const sockaddr_in&>(a);
        const auto& y = reinterpret_cast<const sockaddr_in&>(b);
        return x.sin_port == y.sin_port && x.sin_addr.s_addr == y.sin_addr.s_addr;
    }
    if (a.ss_family == AF_INET6) {
        const auto& x = reinterpret_cast<const sockaddr_in6&>(a);
        const auto& y = reinterpret_cast<const sockaddr_in6&>(b);
        return x.sin6_port == y.sin6_port &&
               std::memcmp(&x.sin6_addr, &y.sin6_addr, sizeof x.sin6_addr) == 0;
    }
    return false;
}

std::uint16_t seqOf(const Frame& frame) noexcept
{
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(frame[2]) |
                                      (std::to_integer<std::uint16_t>(frame[3]) << 8));
}

}  // namespace

std::string_view describe(NetError error) noexcept
{
    switch (error) {
    case NetError::Resolve: return "ім'я сервера не розв'язалося";
    case NetError::Open:    return "сокет не відкрився";
    case NetError::Send:    return "датаграма не пішла";
    case NetError::Receive: return "збій на прийомі";
    case NetError::Timeout: return "відповіді не було";
    }
    return "невідома помилка";
}

// --- UdpSocket ---------------------------------------------------------

UdpSocket::UdpSocket(int fd, const sockaddr_storage& peer, socklen_t peer_len) noexcept
    : fd_{fd}, peer_{peer}, peer_len_{peer_len}
{
}

UdpSocket::UdpSocket(UdpSocket&& other) noexcept
    : fd_{other.fd_}, peer_{other.peer_}, peer_len_{other.peer_len_}
{
    other.fd_ = -1;   // володіння перейшло; чужий деструктор нічого не закриє
}

UdpSocket& UdpSocket::operator=(UdpSocket&& other) noexcept
{
    if (this != &other) {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = other.fd_;
        peer_ = other.peer_;
        peer_len_ = other.peer_len_;
        other.fd_ = -1;
    }
    return *this;
}

UdpSocket::~UdpSocket()
{
    if (fd_ >= 0) {
        ::close(fd_);
    }
}

std::expected<UdpSocket, NetError>
UdpSocket::to(std::string_view host, std::string_view port)
{
    addrinfo hints{};
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_protocol = IPPROTO_UDP;

    // getaddrinfo бере рядки з нулем на кінці, тому копіюємо один раз тут.
    const std::string host_z{host};
    const std::string port_z{port};

    addrinfo* found = nullptr;
    // DNS коштує окремий оберт по мережі. У прошивці розв'язану адресу кладуть
    // у NVS і повторюють запит хіба що після кількох невдач поспіль.
    if (::getaddrinfo(host_z.c_str(), port_z.c_str(), &hints, &found) != 0) {
        return std::unexpected(NetError::Resolve);
    }

    // Список адрес звільняємо в будь-якому разі — за це відповідає guard.
    struct Guard {
        addrinfo* list;
        ~Guard() { ::freeaddrinfo(list); }
    } guard{found};

    for (const addrinfo* ai = found; ai != nullptr; ai = ai->ai_next) {
        const int fd = ::socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
        if (fd < 0) {
            continue;
        }
        sockaddr_storage peer{};
        std::memcpy(&peer, ai->ai_addr, ai->ai_addrlen);
        return UdpSocket{fd, peer, ai->ai_addrlen};
    }
    return std::unexpected(NetError::Open);
}

std::expected<void, NetError> UdpSocket::send(std::span<const std::byte> frame) const
{
    const auto sent = ::sendto(fd_, frame.data(), frame.size(), 0,
                               reinterpret_cast<const sockaddr*>(&peer_), peer_len_);
    if (sent != static_cast<ssize_t>(frame.size())) {
        return std::unexpected(NetError::Send);
    }
    return {};
}

std::expected<std::span<std::byte>, NetError>
UdpSocket::receive(std::span<std::byte> buffer, std::chrono::milliseconds timeout) const
{
    const auto deadline = std::chrono::steady_clock::now() + timeout;

    for (;;) {
        const auto left = std::chrono::duration_cast<std::chrono::milliseconds>(
            deadline - std::chrono::steady_clock::now());
        if (left <= 0ms) {
            return std::unexpected(NetError::Timeout);
        }

        pollfd pfd{.fd = fd_, .events = POLLIN, .revents = 0};
        const int ready = ::poll(&pfd, 1, static_cast<int>(left.count()));
        if (ready < 0) {
            if (errno == EINTR) {
                continue;   // прокинулися від сигналу — дочекуємо залишок
            }
            return std::unexpected(NetError::Receive);
        }
        if (ready == 0) {
            return std::unexpected(NetError::Timeout);
        }

        sockaddr_storage from{};
        socklen_t from_len = sizeof from;
        const auto got = ::recvfrom(fd_, buffer.data(), buffer.size(), 0,
                                    reinterpret_cast<sockaddr*>(&from), &from_len);
        if (got < 0) {
            if (errno == EINTR) {
                continue;
            }
            return std::unexpected(NetError::Receive);
        }
        if (!samePeer(from, peer_)) {
            continue;   // сканер портів або сусідній вузол
        }
        return buffer.first(static_cast<std::size_t>(got));
    }
}

// --- Uplink ------------------------------------------------------------

Uplink::Uplink(UdpSocket socket, std::string spool_path, std::uint16_t first_seq)
    : socket_{std::move(socket)}, spool_path_{std::move(spool_path)}, seq_{first_seq}
{
}

// Одна транзакція: до kArqAttempts відправок того самого кадру.
// Номер кадру не міняється — сервер бачить повтор і не задвоює запис.
bool Uplink::sendWithRetries(const Frame& frame)
{
    const std::uint16_t seq = seqOf(frame);

    for (int attempt = 1; attempt <= kArqAttempts; ++attempt) {
        const auto started = std::chrono::steady_clock::now();
        const auto elapsed = [&] {
            return std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now() - started);
        };

        if (auto sent = socket_.send(frame); !sent) {
            tx_ += elapsed();
            // Мережі зараз немає взагалі; повторювати негайно немає сенсу.
            std::cerr << "uplink: " << describe(sent.error()) << '\n';
            return false;
        }

        bool acked = false;
        const auto deadline = std::chrono::steady_clock::now() + kArqTimeout;
        std::array<std::byte, 64> buffer{};

        for (;;) {
            const auto left = std::chrono::duration_cast<std::chrono::milliseconds>(
                deadline - std::chrono::steady_clock::now());
            if (left <= 0ms) {
                break;
            }
            const auto datagram = socket_.receive(buffer, left);
            if (!datagram) {
                break;   // тиша або збій сокета
            }
            const auto ack = decodeAck(*datagram);
            if (!ack) {
                continue;          // не підтвердження
            }
            if (*ack != seq) {
                continue;          // запізніле ACK попередньої спроби
            }
            acked = true;
            break;
        }

        tx_ += elapsed();
        if (acked) {
            return true;
        }
        std::cerr << "uplink: кадр #" << seq << " без ACK, спроба "
                  << attempt << " з " << kArqAttempts << '\n';
    }
    return false;
}

// --- спул: те, що не пішло в ефір, чекає на диску (у прошивці — в NVS) ---

std::span<Frame> Uplink::loadSpool(std::size_t& dropped)
{
    dropped = 0;

    std::ifstream file{spool_path_, std::ios::binary};
    if (!file) {
        return {};   // спулу немає — і добре
    }

    file.seekg(0, std::ios::end);
    const auto size = static_cast<std::size_t>(file.tellg());
    const std::size_t frames = size / kTelemetrySize;
    const std::size_t skip = frames > kSpoolCapacity ? frames - kSpoolCapacity : 0;
    dropped = skip;   // переповнення: найстаріші виміри втрачаємо свідомо

    file.seekg(static_cast<std::streamoff>(skip * kTelemetrySize), std::ios::beg);
    const std::size_t want = frames - skip;
    file.read(reinterpret_cast<char*>(spool_.data()),
              static_cast<std::streamsize>(want * kTelemetrySize));

    const auto got = static_cast<std::size_t>(file.gcount()) / kTelemetrySize;
    return std::span{spool_}.first(got);
}

void Uplink::storeSpool(std::span<const Frame> frames) const
{
    if (frames.empty()) {
        std::error_code ec;
        std::filesystem::remove(spool_path_, ec);
        return;
    }
    std::ofstream file{spool_path_, std::ios::binary | std::ios::trunc};
    if (!file) {
        std::cerr << "uplink: спул не відкрився на запис\n";
        return;
    }
    file.write(reinterpret_cast<const char*>(frames.data()),
               static_cast<std::streamsize>(frames.size() * kTelemetrySize));
}

std::size_t Uplink::flushSpool()
{
    std::size_t dropped = 0;
    auto pending = loadSpool(dropped);
    if (dropped > 0) {
        std::cerr << "uplink: спул переповнено, втрачено " << dropped << " кадрів\n";
    }
    if (pending.empty()) {
        if (dropped > 0) {
            storeSpool({});
        }
        return 0;
    }

    std::size_t sent = 0;
    while (sent < pending.size() && sendWithRetries(pending[sent])) {
        ++sent;
    }

    // Решту лишаємо на наступний сеанс — канал знову мовчить.
    storeSpool(pending.subspan(sent));
    return sent;
}

bool Uplink::send(const Sample& sample)
{
    Frame frame{};
    const auto encoded = encodeTelemetry(sample, seq_, frame);
    if (!encoded) {
        std::cerr << "uplink: кадр не склався — " << describe(encoded.error()) << '\n';
        return false;
    }

    // Номер росте навіть тоді, коли кадр не пішов: сервер по розривах у
    // послідовності бачить, скільки вимірів не доїхало взагалі.
    ++seq_;

    if (sendWithRetries(frame)) {
        return true;
    }

    std::size_t dropped = 0;
    auto pending = loadSpool(dropped);
    std::size_t count = pending.size();
    if (count == kSpoolCapacity) {
        // Місця більше немає: викидаємо найстаріший кадр. Свіжий вимір
        // цінніший за торішній — це рішення, а не аварія.
        std::shift_left(spool_.begin(), spool_.begin() + static_cast<std::ptrdiff_t>(count), 1);
        --count;
        ++dropped;
    }
    spool_[count++] = frame;
    storeSpool(std::span{spool_}.first(count));

    if (dropped > 0) {
        std::cerr << "uplink: спул переповнено, втрачено " << dropped << " кадрів\n";
    }
    return false;
}

}  // namespace telemetry
