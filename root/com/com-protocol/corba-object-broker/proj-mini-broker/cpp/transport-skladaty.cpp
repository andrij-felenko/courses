#include <cerrno>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

bool read_n(int fd, uint8_t* dst, size_t n) {
    size_t got = 0;
    while (got < n) {
        ssize_t k = ::recv(fd, dst + got, n - got, 0);
        if (k == 0) return false;                       // партнер закрив з'єднання
        if (k < 0) { if (errno == EINTR) continue; return false; }
        got += static_cast<size_t>(k);
    }
    return true;
}

bool write_all(int fd, const uint8_t* src, size_t n, size_t* sent) {
    *sent = 0;
    while (*sent < n) {
        ssize_t k = ::send(fd, src + *sent, n - *sent, 0);
        if (k < 0) { if (errno == EINTR) continue; return false; }
        if (k == 0) return false;
        *sent += static_cast<size_t>(k);
    }
    return true;
}

bool recv_message(int fd, std::vector<uint8_t>& msg) {
    msg.assign(12, 0);
    if (!read_n(fd, msg.data(), 12)) return false;
    if (std::memcmp(msg.data(), "MORB", 4) != 0) return false;

    bool swap = ((msg[6] & 1) != 0) != host_is_little();
    uint32_t body;
    std::memcpy(&body, msg.data() + 8, 4);
    if (swap) body = bswap32(body);
    if (body > (1u << 20)) return false;                // стеля: чужий байт не з'їсть пам'ять

    msg.resize(12 + body);                              // заголовок ЛИШАЄТЬСЯ в буфері
    return body == 0 || read_n(fd, msg.data() + 12, body);
}
