#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

int run_rfcomm_server(uint8_t channel) {
    int server_fd = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
    if (server_fd < 0) {
        perror("Помилка створення сокета");
        return -1;
    }

    struct sockaddr_rc loc_addr;
    memset(&loc_addr, 0, sizeof(loc_addr));
    loc_addr.rc_family = AF_BLUETOOTH;
    loc_addr.rc_bdaddr = *BDADDR_ANY;
    loc_addr.rc_channel = channel;

    if (bind(server_fd, (struct sockaddr *)&loc_addr, sizeof(loc_addr)) < 0) {
        perror("Помилка bind на каналі RFCOMM");
        close(server_fd);
        return -1;
    }

    if (listen(server_fd, 1) < 0) {
        perror("Помилка listen");
        close(server_fd);
        return -1;
    }

    printf("RFCOMM сервер слухає канал %u...\n", channel);

    struct sockaddr_rc rem_addr;
    socklen_t opt = sizeof(rem_addr);
    int client_fd = accept(server_fd, (struct sockaddr *)&rem_addr, &opt);
    if (client_fd < 0) {
        perror("Помилка accept");
        close(server_fd);
        return -1;
    }

    char client_mac[18];
    ba2str(&rem_addr.rc_bdaddr, client_mac);
    printf("Клієнт підключився: %s (канал %u)\n", client_mac, rem_addr.rc_channel);

    char buf[1024];
    ssize_t bytes_read = read(client_fd, buf, sizeof(buf) - 1);
    if (bytes_read > 0) {
        buf[bytes_read] = '\0';
        printf("Отримано %zd байтів: %s\n", bytes_read, buf);
        write(client_fd, buf, bytes_read); // Ехо-відповідь назад
    }

    close(client_fd);
    close(server_fd);
    return 0;
}

int run_rfcomm_client(const char *dest_mac, uint8_t channel) {
    int sock = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
    if (sock < 0) {
        perror("Помилка створення клієнтського сокета");
        return -1;
    }

    struct sockaddr_rc addr;
    memset(&addr, 0, sizeof(addr));
    addr.rc_family = AF_BLUETOOTH;
    addr.rc_channel = channel;
    if (str2ba(dest_mac, &addr.rc_bdaddr) < 0) {
        fprintf(stderr, "Некоректний формат MAC-адреси: %s\n", dest_mac);
        close(sock);
        return -1;
    }

    printf("Підключення до %s на каналі %u...\n", dest_mac, channel);
    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Помилка connect");
        close(sock);
        return -1;
    }

    const char *msg = "Hello RFCOMM from C";
    write(sock, msg, strlen(msg));

    char buf[1024];
    ssize_t bytes_read = read(sock, buf, sizeof(buf) - 1);
    if (bytes_read > 0) {
        buf[bytes_read] = '\0';
        printf("Відповідь сервера: %s\n", buf);
    }

    close(sock);
    return 0;
}
