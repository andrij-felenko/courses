// Приклад на C++20 (із перевіркою помилок через std::error_code)
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <system_error>
#include <iostream>

void enable_tls_ulp(int sock_fd) {
    if (::setsockopt(sock_fd, SOL_TCP, TCP_ULP, "tls", sizeof("tls")) < 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося встановити TCP_ULP tls");
    }
}
