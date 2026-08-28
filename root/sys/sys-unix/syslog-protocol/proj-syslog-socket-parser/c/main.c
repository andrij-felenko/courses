/* Практичний Syslog-клієнт та парсер RFC 5424 на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/un.h>

#define SYSLOG_PATH "/dev/log"
#define BUFFER_SIZE 2048

/* Структура для збереження розібраного syslog-повідомлення */
typedef struct {
    int prival;
    int facility;
    int severity;
    int version;
    char timestamp[64];
    char hostname[128];
    char app_name[64];
    char procid[32];
    char msgid[64];
    char msg[1024];
} syslog_message_t;

/* Обчислення поточного часу у форматі ISO 8601 */
static void get_iso8601_time(char *buf, size_t len) {
    time_t now = time(NULL);
    struct tm tm_info;
    localtime_r(&now, &tm_info);
    strftime(buf, len, "%Y-%m-%dT%H:%M:%S%z", &tm_info);
}

/* Відправка розширеного RFC 5424 повідомлення у /dev/log */
int send_syslog_rfc5424(int facility, int severity, const char *app_name, const char *msg) {
    int sock_fd = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (sock_fd < 0) {
        perror("socket");
        return -1;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SYSLOG_PATH, sizeof(addr.sun_path) - 1);

    int prival = (facility * 8) + severity;
    char time_str[64];
    get_iso8601_time(time_str, sizeof(time_str));
    pid_t pid = getpid();

    char payload[BUFFER_SIZE];
    /* Формат RFC 5424: <PRIVAL>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG */
    int len = snprintf(payload, sizeof(payload),
                       "<%d>1 %s localhost %s %d ID47 - %s",
                       prival, time_str, app_name, pid, msg);

    if (len < 0 || len >= (int)sizeof(payload)) {
        close(sock_fd);
        return -1;
    }

    ssize_t sent = sendto(sock_fd, payload, len, 0, (struct sockaddr *)&addr, sizeof(addr));
    close(sock_fd);
    return (sent == len) ? 0 : -1;
}

/* Розбір сирого текстового рядка RFC 5424 */
int parse_syslog_rfc5424(const char *raw, syslog_message_t *out) {
    if (!raw || !out) return -1;
    memset(out, 0, sizeof(syslog_message_t));

    /* Очікується формат: <PRIVAL>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID SD MSG */
    if (raw[0] != '<') return -1;

    const char *ptr = raw + 1;
    out->prival = atoi(ptr);

    /* Розбиваємо PRIVAL на Facility та Severity */
    out->facility = out->prival / 8;
    out->severity = out->prival % 8;

    ptr = strchr(ptr, '>');
    if (!ptr) return -1;
    ptr++; // Переходимо за '>'

    int parsed = sscanf(ptr, "%d %63s %127s %63s %31s %63s",
                        &out->version,
                        out->timestamp,
                        out->hostname,
                        out->app_name,
                        out->procid,
                        out->msgid);

    if (parsed < 6) return -1;

    /* Пропускаємо розібрані поля і шукаємо початок повідомлення */
    const char *msg_ptr = strchr(ptr, '-'); // Пропускаємо Structured-Data (-)
    if (msg_ptr) {
        msg_ptr++;
        if (*msg_ptr == ' ') msg_ptr++;
        strncpy(out->msg, msg_ptr, sizeof(out->msg) - 1);
    }

    return 0;
}

int main(void) {
    printf("--- Відправка RFC 5424 у /dev/log ---\n");
    if (send_syslog_rfc5424(1, 3, "custom_app", "Критична помилка пам'яті!") == 0) {
        printf("Повідомлення успішно відправлено.\n");
    }

    printf("\n--- Парсинг тестового пакету RFC 5424 ---\n");
    const char *sample = "<83>1 2026-08-14T13:36:16+0300 myhost auth_service 4512 ID99 - Пароль користувача скинуто";
    syslog_message_t msg;

    if (parse_syslog_rfc5424(sample, &msg) == 0) {
        printf("PRIVAL: %d (Facility: %d [authpriv], Severity: %d [err])\n",
               msg.prival, msg.facility, msg.severity);
        printf("Версія: %d\nЧас: %s\nХост: %s\nПрограма: %s [PID: %s]\nПовідомлення: %s\n",
               msg.version, msg.timestamp, msg.hostname, msg.app_name, msg.procid, msg.msg);
    }

    return 0;
}
