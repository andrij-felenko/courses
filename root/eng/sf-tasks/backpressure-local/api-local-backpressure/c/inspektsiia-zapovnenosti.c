#include <sys/ioctl.h>
#include <linux/sockios.h>
#include <unistd.h>
#include <stdio.h>

/* Отримання поточного стану черг сокета ядра */
int get_socket_queue_depth(int sock_fd, int *rx_bytes, int *tx_bytes) {
    /* Кількість байтів, готових до читання у вхідному буфері ядра */
    if (ioctl(sock_fd, FIONREAD, rx_bytes) == -1) {
        return -1;
    }
    /* Кількість байтів, які ще не надіслані у вихідному буфері ядра */
    if (ioctl(sock_fd, SIOCOUTQ, tx_bytes) == -1) {
        return -1;
    }
    return 0;
}
