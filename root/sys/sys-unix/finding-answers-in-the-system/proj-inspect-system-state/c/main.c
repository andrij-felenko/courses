#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

/* Читання значення конкретного ключа з /proc/self/status */
static int read_proc_status_field(const char *key, char *out_val, size_t out_len) {
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) {
        return -1;
    }

    char line[256];
    size_t key_len = strlen(key);
    int found = 0;

    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, key, key_len) == 0 && line[key_len] == ':') {
            char *p = line + key_len + 1;
            while (*p == ' ' || *p == '\t') {
                p++;
            }
            /* Видаляємо завершальний перенос рядка */
            char *nl = strchr(p, '\n');
            if (nl) {
                *nl = '\0';
            }
            strncpy(out_val, p, out_len - 1);
            out_val[out_len - 1] = '\0';
            found = 1;
            break;
        }
    }

    fclose(f);
    return found ? 0 : -1;
}

/* Читання аргументів процесу з /proc/self/cmdline (розділені \0) */
static void print_proc_cmdline(void) {
    int fd = open("/proc/self/cmdline", O_RDONLY);
    if (fd < 0) {
        perror("open(/proc/self/cmdline)");
        return;
    }

    char buf[1024];
    ssize_t bytes_read = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (bytes_read <= 0) {
        printf("  [cmdline]: (порожній або недоступний)\n");
        return;
    }

    printf("  [cmdline]: ");
    ssize_t i = 0;
    while (i < bytes_read) {
        printf("[%s] ", &buf[i]);
        i += strlen(&buf[i]) + 1;
    }
    printf("\n");
}

/* Читання одного атрибута sysfs */
static int read_sysfs_attr(const char *path, char *out_buf, size_t max_len) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    ssize_t n = read(fd, out_buf, max_len - 1);
    close(fd);

    if (n <= 0) {
        return -1;
    }

    out_buf[n] = '\0';
    char *nl = strchr(out_buf, '\n');
    if (nl) {
        *nl = '\0';
    }
    return 0;
}

/* Читання одного повідомлення з кільцевого буфера /dev/kmsg */
static void read_single_kmsg(void) {
    int fd = open("/dev/kmsg", O_RDONLY | O_NONBLOCK);
    if (fd < 0) {
        if (errno == EACCES) {
            printf("  [/dev/kmsg]: Потрібні привілеї CAP_SYSLOG або root для читання\n");
        } else {
            perror("open(/dev/kmsg)");
        }
        return;
    }

    char buf[2048];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (n > 0) {
        buf[n] = '\0';
        /* Формат запису: "рівень,номер_послідовності,мікросекунди,прапорці;текст_повідомлення\n" */
        char *semicolon = strchr(buf, ';');
        if (semicolon) {
            *semicolon = '\0';
            char *msg = semicolon + 1;
            char *nl = strchr(msg, '\n');
            if (nl) *nl = '\0';

            int priority = 0;
            unsigned long long seq = 0, timestamp_us = 0;
            sscanf(buf, "%d,%llu,%llu", &priority, &seq, &timestamp_us);

            printf("  [/dev/kmsg]: рівень=%d, послідовність=%llu, час=%.3fs -> \"%s\"\n",
                   priority & 7, seq, (double)timestamp_us / 1000000.0, msg);
        }
    } else if (errno == EAGAIN) {
        printf("  [/dev/kmsg]: Буфер повідомлень порожній\n");
    }
}

int main(void) {
    printf("=== Інспекція багатошарового системного стану ===\n\n");

    /* 1. procfs: процесний стан */
    printf("1. Процесний шар (/proc/self/):\n");
    char rss[64] = "N/A", threads[64] = "N/A";
    read_proc_status_field("VmRSS", rss, sizeof(rss));
    read_proc_status_field("Threads", threads, sizeof(threads));
    printf("  [status] Резидентна пам'ять (VmRSS): %s\n", rss);
    printf("  [status] Кількість потоків:           %s\n", threads);
    print_proc_cmdline();

    /* 2. sysfs: стан мережевого інтерфейсу */
    printf("\n2. Апаратний / пристроєвий шар (/sys/class/net/lo/):\n");
    char operstate[32] = "N/A", mtu[32] = "N/A";
    read_sysfs_attr("/sys/class/net/lo/operstate", operstate, sizeof(operstate));
    read_sysfs_attr("/sys/class/net/lo/mtu", mtu, sizeof(mtu));
    printf("  [interface] Стан lo (operstate): %s\n", operstate);
    printf("  [interface] MTU lo:              %s байтів\n", mtu);

    /* 3. run: перевірка рантайм-стану */
    printf("\n3. Летючий рантайм-стан (/run/):\n");
    if (access("/run/systemd/system", F_OK) == 0) {
        printf("  [runtime] Виявлено активний екземпляр systemd у /run/systemd/system\n");
    } else {
        printf("  [runtime] systemd не виявлено або /run змонтовано без прав доступу\n");
    }

    /* 4. Телеметрія ядра: kmsg */
    printf("\n4. Телеметрія кільцевого буфера ядра (/dev/kmsg):\n");
    read_single_kmsg();

    return 0;
}
