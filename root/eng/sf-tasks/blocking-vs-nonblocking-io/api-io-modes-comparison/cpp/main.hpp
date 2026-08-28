#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/tcp.h>
#include <chrono>

// 1. Встановлення таймаутів на блокуючі операції через std::chrono
struct timeval timeout{};
auto sec = std::chrono::seconds(5);
timeout.tv_sec = static_cast<decltype(timeout.tv_sec)>(sec.count());
timeout.tv_usec = 0;

::setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
::setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

// 2. Зміна розмірів буферів ядра
int buf_size = 256 * 1024; // 256 КБ
::setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size));
::setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &buf_size, sizeof(buf_size));

// 3. Вимкнення алгоритму Нейгла (TCP_NODELAY)
int flag = 1;
::setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
