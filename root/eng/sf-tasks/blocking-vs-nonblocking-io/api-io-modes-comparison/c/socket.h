#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/tcp.h>

/* 1. Встановлення таймаутів на блокуючі операції (альтернатива O_NONBLOCK) */
struct timeval timeout;
timeout.tv_sec = 5;  /* 5 секунд */
timeout.tv_usec = 0;

setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

/* 2. Зміна розмірів буферів ядра */
int buf_size = 256 * 1024; /* 256 КБ */
setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size));
setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &buf_size, sizeof(buf_size));

/* 3. Вимкнення алгоритму Нейгла для мінімізації затримок (TCP_NODELAY) */
int flag = 1;
setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
