#include "udp_link.h"

#include <cerrno>
#include <stdexcept>
#include <system_error>

#include <arpa/inet.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

[[noreturn]] void throwErrno(const char* what) {
    throw std::system_error(errno, std::system_category(), what);
}

} // namespace

UdpLink::UdpLink(const std::string& bind_host, std::uint16_t bind_port) {
    m_fd = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (m_fd < 0) {
        throwErrno("socket");
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = ::htons(bind_port);
    if (::inet_pton(AF_INET, bind_host.c_str(), &addr.sin_addr) != 1) {
        ::close(m_fd);
        m_fd = -1;
        throw std::invalid_argument("некоректна IPv4-адреса: " + bind_host);
    }

    const int reuse = 1;
    ::setsockopt(m_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    if (::bind(m_fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        const int err = errno;
        ::close(m_fd);
        m_fd = -1;
        throw std::system_error(err, std::system_category(), "bind " + bind_host);
    }

    const int flags = ::fcntl(m_fd, F_GETFL, 0);
    if (flags < 0 || ::fcntl(m_fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        const int err = errno;
        ::close(m_fd);
        m_fd = -1;
        throw std::system_error(err, std::system_category(), "fcntl O_NONBLOCK");
    }
}

UdpLink::~UdpLink() {
    if (m_fd >= 0) {
        ::close(m_fd);
    }
}

std::size_t UdpLink::receive(std::span<std::uint8_t> out, int timeout_ms) {
    pollfd pfd{};
    pfd.fd = m_fd;
    pfd.events = POLLIN;

    const int ready = ::poll(&pfd, 1, timeout_ms);
    if (ready < 0) {
        if (errno == EINTR) {
            return 0;
        }
        throwErrno("poll");
    }
    if (ready == 0) {
        return 0;
    }

    sockaddr_in from{};
    socklen_t from_len = sizeof(from);
    const ssize_t n = ::recvfrom(m_fd, out.data(), out.size(), 0,
                                 reinterpret_cast<sockaddr*>(&from), &from_len);
    if (n < 0) {
        // ECONNREFUSED прилітає сюди від ICMP на наш попередній sendto: апарат
        // просто ще не піднявся. Це не привід валити станцію.
        if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR || errno == ECONNREFUSED) {
            return 0;
        }
        throwErrno("recvfrom");
    }

    if (!m_has_peer ||
        from.sin_addr.s_addr != m_peer.sin_addr.s_addr ||
        from.sin_port != m_peer.sin_port) {
        m_peer = from;
        m_has_peer = true;
        m_peer_fresh = true;
    }
    return static_cast<std::size_t>(n);
}

void UdpLink::send(std::span<const std::uint8_t> frame) {
    if (!m_has_peer || frame.empty()) {
        return;  // ще не знаємо, кому писати
    }

    const ssize_t n = ::sendto(m_fd, frame.data(), frame.size(), 0,
                               reinterpret_cast<const sockaddr*>(&m_peer), sizeof(m_peer));
    if (n < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR ||
            errno == ECONNREFUSED || errno == ENETUNREACH || errno == EHOSTUNREACH) {
            return;  // кадр загубився — автомат сам його повторить
        }
        throwErrno("sendto");
    }
}

std::string UdpLink::peerName() const {
    if (!m_has_peer) {
        return "(невідомо)";
    }
    char text[INET_ADDRSTRLEN]{};
    ::inet_ntop(AF_INET, &m_peer.sin_addr, text, sizeof(text));
    return std::string(text) + ":" + std::to_string(::ntohs(m_peer.sin_port));
}

bool UdpLink::takePeerUpdate() noexcept {
    const bool fresh = m_peer_fresh;
    m_peer_fresh = false;
    return fresh;
}
