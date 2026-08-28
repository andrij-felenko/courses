/* modem_controller.c — Повна C-реалізація ініціалізації PDP-контексту */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/select.h>

#define MODEM_BUFFER_SIZE 1024
#define DEFAULT_TIMEOUT_MS 5000

typedef struct {
    int serial_fd;
    char assigned_ip[64];
    int last_cme_error;
} modem_t;

static bool serial_write(int fd, const char *cmd) {
    size_t len = strlen(cmd);
    ssize_t written = write(fd, cmd, len);
    return (written == (ssize_t)len);
}

static bool wait_for_response(int fd, char *buffer, size_t max_len, int timeout_ms) {
    size_t total_read = 0;
    memset(buffer, 0, max_len);

    while (timeout_ms > 0) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(fd, &read_fds);

        struct timeval tv;
        tv.tv_sec = timeout_ms / 1000;
        tv.tv_usec = (timeout_ms % 1000) * 1000;

        int res = select(fd + 1, &read_fds, NULL, NULL, &tv);
        if (res > 0 && FD_ISSET(fd, &read_fds)) {
            ssize_t n = read(fd, buffer + total_read, max_len - total_read - 1);
            if (n > 0) {
                total_read += (size_t)n;
                buffer[total_read] = '\0';
                if (strstr(buffer, "\r\nOK\r\n") != NULL || strstr(buffer, "\r\nERROR\r\n") != NULL ||
                    strstr(buffer, "+CME ERROR:") != NULL) {
                    return true;
                }
            }
        } else {
            break; /* Таймаут */
        }
        timeout_ms -= 50;
    }
    return (total_read > 0);
}

bool modem_send_cmd(modem_t *modem, const char *cmd, char *out_resp, size_t out_max, int timeout_ms) {
    char full_cmd[256];
    snprintf(full_cmd, sizeof(full_cmd), "%s\r\n", cmd);

    if (!serial_write(modem->serial_fd, full_cmd)) {
        return false;
    }

    char local_buf[MODEM_BUFFER_SIZE];
    bool ok = wait_for_response(modem->serial_fd, local_buf, sizeof(local_buf), timeout_ms);
    if (!ok) {
        return false;
    }

    if (out_resp && out_max > 0) {
        strncpy(out_resp, local_buf, out_max - 1);
        out_resp[out_max - 1] = '\0';
    }

    if (strstr(local_buf, "\r\nOK\r\n") != NULL) {
        return true;
    }

    char *err_pos = strstr(local_buf, "+CME ERROR: ");
    if (err_pos) {
        modem->last_cme_error = atoi(err_pos + 12);
    }
    return false;
}

bool modem_init_pdp(modem_t *modem, const char *apn, const char *pdp_type) {
    char response[MODEM_BUFFER_SIZE];

    /* 1. Перевірка базової реакції модема */
    if (!modem_send_cmd(modem, "AT", response, sizeof(response), 1000)) {
        return false;
    }

    /* 2. Увімкнення розширеного звітування про помилки (+CME ERROR) */
    modem_send_cmd(modem, "AT+CMEE=1", NULL, 0, 1000);

    /* 3. Перевірка готовності SIM-карти */
    if (!modem_send_cmd(modem, "AT+CPIN?", response, sizeof(response), 3000)) {
        return false;
    }
    if (strstr(response, "+CPIN: READY") == NULL) {
        return false; /* SIM заблокована або відсутня */
    }

    /* 4. Очікування реєстрації в мережі LTE (CEREG stat=1 або stat=5) */
    bool registered = false;
    for (int attempts = 0; attempts < 15; attempts++) {
        if (modem_send_cmd(modem, "AT+CEREG?", response, sizeof(response), 2000)) {
            if (strstr(response, ",1") != NULL || strstr(response, ",5") != NULL) {
                registered = true;
                break;
            }
        }
        sleep(1);
    }
    if (!registered) {
        return false; /* Реєстрацію не отримано */
    }

    /* 5. Конфігурація PDP-контексту cid=1 */
    char cgdcont_cmd[256];
    snprintf(cgdcont_cmd, sizeof(cgdcont_cmd), "AT+CGDCONT=1,\"%s\",\"%s\"", pdp_type, apn);
    if (!modem_send_cmd(modem, cgdcont_cmd, response, sizeof(response), 3000)) {
        return false;
    }

    /* 6. Активація PDP-контексту cid=1 */
    if (!modem_send_cmd(modem, "AT+CGACT=1,1", response, sizeof(response), 10000)) {
        return false;
    }

    /* 7. Зчитування призначеної IP-адреси */
    if (modem_send_cmd(modem, "AT+CGPADDR=1", response, sizeof(response), 3000)) {
        char *ip_start = strstr(response, "+CGPADDR: 1,\"");
        if (ip_start) {
            ip_start += 13;
            char *ip_end = strchr(ip_start, '\"');
            if (ip_end) {
                size_t ip_len = (size_t)(ip_end - ip_start);
                strncpy(modem->assigned_ip, ip_start, ip_len);
                modem->assigned_ip[ip_len] = '\0';
                return true;
            }
        }
    }
    return false;
}
