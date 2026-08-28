#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>

#define TOMOYO_STAT_PATH "/sys/kernel/security/tomoyo/stat"
#define TOMOYO_DOMAIN_PATH "/sys/kernel/security/tomoyo/domain_policy"
#define BUFFER_SIZE 4096

/* Зчитування та виведення вмісту файлу статистики SecurityFS */
static int read_tomoyo_stat(void) {
    int fd = open(TOMOYO_STAT_PATH, O_RDONLY);
    if (fd < 0) {
        if (errno == ENOENT) {
            fprintf(stderr, "Помилка: TOMOYO LSM не активовано або SecurityFS не змонтовано.\n");
        } else {
            fprintf(stderr, "Помилка відкриття %s: %s\n", TOMOYO_STAT_PATH, strerror(errno));
        }
        return -1;
    }

    char buffer[BUFFER_SIZE];
    ssize_t bytes_read;

    printf("=== Статистика ядра TOMOYO Linux (%s) ===\n", TOMOYO_STAT_PATH);
    while ((bytes_read = read(fd, buffer, sizeof(buffer) - 1)) > 0) {
        buffer[bytes_read] = '\0';
        fputs(buffer, stdout);
    }

    if (bytes_read < 0) {
        fprintf(stderr, "Помилка зчитування даних: %s\n", strerror(errno));
        close(fd);
        return -1;
    }

    close(fd);
    return 0;
}

/* Динамічне додавання правила до domain_policy */
static int append_domain_rule(const char *domain, const char *rule) {
    int fd = open(TOMOYO_DOMAIN_PATH, O_WRONLY | O_APPEND);
    if (fd < 0) {
        fprintf(stderr, "Помилка запису в %s: %s (перевірте manager.conf та root-права)\n",
                TOMOYO_DOMAIN_PATH, strerror(errno));
        return -1;
    }

    char payload[BUFFER_SIZE];
    int len = snprintf(payload, sizeof(payload), "%s\n%s\n", domain, rule);
    if (len < 0 || (size_t)len >= sizeof(payload)) {
        fprintf(stderr, "Помилка: занадто довгий рядок правила.\n");
        close(fd);
        return -1;
    }

    ssize_t written = write(fd, payload, len);
    if (written != len) {
        fprintf(stderr, "Помилка запису правила у SecurityFS: %s\n", strerror(errno));
        close(fd);
        return -1;
    }

    printf("Успішно додано правило [%s] для домену [%s]\n", rule, domain);
    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    if (read_tomoyo_stat() != 0) {
        return EXIT_FAILURE;
    }

    if (argc == 3) {
        const char *target_domain = argv[1];
        const char *target_rule = argv[2];
        if (append_domain_rule(target_domain, target_rule) != 0) {
            return EXIT_FAILURE;
        }
    } else {
        printf("\nВикористання для додавання правила:\n");
        printf("  %s \"<kernel> /usr/sbin/nginx\" \"file read /etc/nginx/nginx.conf\"\n", argv[0]);
    }

    return EXIT_SUCCESS;
}
