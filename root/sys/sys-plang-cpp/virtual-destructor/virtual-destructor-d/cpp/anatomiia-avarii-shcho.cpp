#include <vector>
#include <cstdint>
#include <iostream>

struct PacketHandler {
    void process() { /* обробка базового кадру */ }
    ~PacketHandler() = default; // Невіртуальний деструктор!
};

struct TlsSecureHandler : PacketHandler {
    int socket_fd{-1};
    std::vector<uint8_t> session_keys;
    uint8_t* ring_buffer{nullptr};

    TlsSecureHandler(int fd, std::size_t buf_size)
        : socket_fd(fd), session_keys(256, 0xAA), ring_buffer(new uint8_t[buf_size]) {}

    ~TlsSecureHandler() {
        delete[] ring_buffer;
        // закриття дескриптора сокета
    }
};
