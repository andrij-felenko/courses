// Налаштування сокета за допомогою типізованої обгортки з обробкою помилок
void configure_tcp_keepalive(int fd, std::chrono::seconds idle, std::chrono::seconds interval, int count) {
    const int keepalive = 1;
    const auto idle_sec = static_cast<int>(idle.count());
    const auto intvl_sec = static_cast<int>(interval.count());

    if (::setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося увімкнути SO_KEEPALIVE");
    }
    ::setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle_sec, sizeof(idle_sec));
    ::setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl_sec, sizeof(intvl_sec));
    ::setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &count, sizeof(count));
}
