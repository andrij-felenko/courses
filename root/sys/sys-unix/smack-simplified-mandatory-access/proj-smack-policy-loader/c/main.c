#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/xattr.h>

#define SMACK_LOAD2_PATH "/sys/fs/smackfs/load2"
#define SMACK_ACCESS_PATH "/sys/fs/smackfs/access2"
#define SMACK_XATTR_NAME "security.SMACK64"

/* Завантаження нового правила доступу у /sys/fs/smackfs/load2 */
static int load_smack_rule(const char *subject, const char *object, const char *access) {
    char rule_buf[768];
    int fd = -1;
    ssize_t bytes_written;
    int len;

    /* Формуємо рядок правила у сучасному форматі load2: "Subject Object Access" */
    len = snprintf(rule_buf, sizeof(rule_buf), "%s %s %s\n", subject, object, access);
    if (len < 0 || len >= (int)sizeof(rule_buf)) {
        fprintf(stderr, "Помилка: правило SMACK не вміщається у буфер\n");
        return -1;
    }

    fd = open(SMACK_LOAD2_PATH, O_WRONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити " SMACK_LOAD2_PATH " (перевірте привілеї або монтування smackfs)");
        return -1;
    }

    bytes_written = write(fd, rule_buf, (size_t)len);
    if (bytes_written < 0) {
        perror("Помилка запису правила у load2");
        close(fd);
        return -1;
    }

    close(fd);
    printf("[C] Успішно завантажено правило: %s %s %s\n", subject, object, access);
    return 0;
}

/* Призначення розширеного атрибута SMACK64 на файл */
static int set_smack_label(const char *filepath, const char *label) {
    size_t label_len = strlen(label);

    /* Зверніть увагу: нульовий байт '\0' НЕ включається у значення xattr для SMACK */
    if (setxattr(filepath, SMACK_XATTR_NAME, label, label_len, 0) < 0) {
        perror("Помилка setxattr security.SMACK64");
        return -1;
    }

    printf("[C] Файлу '%s' успішно призначено мітку '%s'\n", filepath, label);
    return 0;
}

/* Перевірка дозволу доступу через /sys/fs/smackfs/access2 */
static int check_smack_access(const char *subject, const char *object, const char *access_request) {
    char query_buf[768];
    char reply_buf[16];
    int fd = -1;
    ssize_t n;
    int len;

    len = snprintf(query_buf, sizeof(query_buf), "%s %s %s", subject, object, access_request);
    if (len < 0 || len >= (int)sizeof(query_buf)) {
        return -1;
    }

    fd = open(SMACK_ACCESS_PATH, O_RDWR);
    if (fd < 0) {
        perror("Помилка відкриття " SMACK_ACCESS_PATH);
        return -1;
    }

    if (write(fd, query_buf, (size_t)len) < 0) {
        perror("Помилка запису запиту в access");
        close(fd);
        return -1;
    }

    lseek(fd, 0, SEEK_SET);
    n = read(fd, reply_buf, sizeof(reply_buf) - 1);
    close(fd);

    if (n <= 0) {
        fprintf(stderr, "Помилка читання відповіді з access\n");
        return -1;
    }

    reply_buf[n] = '\0';
    /* Повернення '1' означає дозвіл, '0' — відмову */
    int granted = (reply_buf[0] == '1');
    printf("[C] Результат перевірки доступу (%s -> %s [%s]): %s\n",
           subject, object, access_request, granted ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО");
    return granted ? 1 : 0;
}

int main(int argc, char *argv[]) {
    const char *test_file = "/tmp/smack_test_data.txt";
    
    /* 1. Створюємо тестовий файл */
    int fd = open(test_file, O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (fd < 0) {
        perror("Не вдалося створити тестовий файл");
        return EXIT_FAILURE;
    }
    write(fd, "Test Data", 9);
    close(fd);

    /* 2. Призначення мітки об'єкта */
    if (set_smack_label(test_file, "UserData") < 0) {
        return EXIT_FAILURE;
    }

    /* 3. Завантаження правила у ядро */
    if (load_smack_rule("WebBrowser", "UserData", "rw") < 0) {
        return EXIT_FAILURE;
    }

    /* 4. Перевірка доступу */
    check_smack_access("WebBrowser", "UserData", "r");
    check_smack_access("WebBrowser", "UserData", "x");

    return EXIT_SUCCESS;
}
