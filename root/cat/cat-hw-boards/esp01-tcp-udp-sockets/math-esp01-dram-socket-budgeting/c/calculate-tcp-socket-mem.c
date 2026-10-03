#include <stdbool.h>
#include <stddef.h>

#define S_TCP_PCB 160
#define S_HDR 56
#define M_RESERVE 8192

// Обчислення необхідної пам'яті під TCP сокет
size_t calculate_tcp_socket_mem(size_t tcp_wnd, size_t mss) {
    size_t n_pbuf = (tcp_wnd + mss - 1) / mss;
    return S_TCP_PCB + tcp_wnd + n_pbuf * S_HDR;
}

// Перевірка безпеки відкриття нового сокета
bool can_open_tcp_socket(size_t free_heap, size_t tcp_wnd, size_t mss) {
    size_t required_mem = calculate_tcp_socket_mem(tcp_wnd, mss);
    if (free_heap < M_RESERVE) {
        return false;
    }
    return (free_heap - M_RESERVE) >= required_mem;
}
