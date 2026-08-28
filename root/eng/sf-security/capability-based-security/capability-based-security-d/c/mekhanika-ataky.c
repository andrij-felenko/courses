#include <fcntl.h>
#include <unistd.h>
#include <string.h>

/* Код привілейованого заступника (виконується з UID 0) */
void handle_client_request(const char *user_chosen_path, const char *data) {
    /* 1. Запис результатів клієнта */
    int fd_out = open(user_chosen_path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd_out >= 0) {
        write(fd_out, data, strlen(data));
        close(fd_out);
    }

    /* 2. Запис внутрішнього системного білінгу від власного імені */
    int fd_bill = open("/var/log/service.bill", O_WRONLY | O_APPEND);
    if (fd_bill >= 0) {
        write(fd_bill, "BILLING_RECORD: +1 operation\n", 29);
        close(fd_bill);
    }
}
