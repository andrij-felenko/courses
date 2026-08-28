int tcp_listen(uint16_t port) {                  // POSIX; у Winsock ті самі виклики,
    int s = ::socket(AF_INET, SOCK_STREAM, 0);   // але інші типи дескриптора й помилок
    int one = 1;
    ::setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    sockaddr_in a{};
    a.sin_family = AF_INET;
    a.sin_port = htons(port);
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    ::bind(s, reinterpret_cast<sockaddr*>(&a), sizeof a);
    ::listen(s, 4);
    return s;
}

int tcp_connect(const char* host, uint16_t port) {
    int s = ::socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in a{};
    a.sin_family = AF_INET;
    a.sin_port = htons(port);
    ::inet_pton(AF_INET, host, &a.sin_addr);
    if (::connect(s, reinterpret_cast<sockaddr*>(&a), sizeof a) != 0) { ::close(s); return -1; }
    return s;
}
