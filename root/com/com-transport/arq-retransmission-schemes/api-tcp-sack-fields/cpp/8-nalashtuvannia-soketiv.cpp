#include <sys/socket.h>
#include <netinet/tcp.h>
#include <netinet/in.h>
#include <system_error>
#include <chrono>

namespace net {

/* Безпечне налаштування параметрів сокета у сучасному C++ */
void configure_low_latency(int sockfd, std::chrono::milliseconds timeout = std::chrono::milliseconds{1500}) {
    const int enable = 1;

    // 1. Негайна відправка (вимкнення алгоритму Нагла)
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &enable, sizeof(enable)) != 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося встановити TCP_NODELAY");
    }

    // 2. Негайні підтвердження QuickACK
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_QUICKACK, &enable, sizeof(enable)) != 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося встановити TCP_QUICKACK");
    }

    // 3. Граничний таймаут непідтверджених даних
    const auto timeout_ms = static_cast<unsigned int>(timeout.count());
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_USER_TIMEOUT, &timeout_ms, sizeof(timeout_ms)) != 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося встановити TCP_USER_TIMEOUT");
    }
}

} // namespace net
