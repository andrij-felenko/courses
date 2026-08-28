#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Структура облікового запису /etc/passwd
typedef struct {
    char *username;
    unsigned int uid;
    unsigned int gid;
    char *homedir;
    char *shell;
} UserRecord;

// Порядковий потоковий парсер формату з роздільником ':'
int parse_passwd_stream(FILE *stream) {
    char *line = NULL;
    size_t len = 0;
    ssize_t read_bytes;

    while ((read_bytes = getline(&line, &len, stream)) != -1) {
        // Видалення завершального переносу рядка \n
        if (read_bytes > 0 && line[read_bytes - 1] == '\n') {
            line[read_bytes - 1] = '\0';
        }

        // Пропуск коментарів та порожніх рядків
        if (line[0] == '#' || line[0] == '\0') {
            continue;
        }

        char *cursor = line;
        char *username = strsep(&cursor, ":");
        char *password = strsep(&cursor, ":"); // Пропуск хешу пароля
        char *uid_str  = strsep(&cursor, ":");
        char *gid_str  = strsep(&cursor, ":");
        char *gecos    = strsep(&cursor, ":"); // Пропуск коментаря
        char *homedir  = strsep(&cursor, ":");
        char *shell    = strsep(&cursor, ":");

        if (username && uid_str && gid_str && homedir && shell) {
            unsigned int uid = (unsigned int)strtoul(uid_str, NULL, 10);
            unsigned int gid = (unsigned int)strtoul(gid_str, NULL, 10);

            // Фільтрація користувачів з UID >= 1000
            if (uid >= 1000) {
                printf("Користувач: %-15s UID: %-5u Home: %-20s Shell: %s\n",
                       username, uid, homedir, shell);
            }
        }
        (void)password;
        (void)gecos;
    }

    free(line);
    return 0;
}
