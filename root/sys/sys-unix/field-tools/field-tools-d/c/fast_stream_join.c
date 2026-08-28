/* fast_stream_join.c — Потокове реляційне з'єднання двох відсортованих списків */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DELIM '\t'

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s file1.tsv file2.tsv\n", argv[0]);
        return EXIT_FAILURE;
    }

    FILE *f1 = fopen(argv[1], "re");
    FILE *f2 = fopen(argv[2], "re");
    if (!f1 || !f2) {
        perror("Помилка відкриття файлів");
        if (f1) fclose(f1);
        if (f2) fclose(f2);
        return EXIT_FAILURE;
    }

    char *line1 = NULL, *line2 = NULL;
    size_t cap1 = 0, cap2 = 0;
    ssize_t len1 = 0, len2 = 0;

    /* Зчитування перших рядків */
    len1 = getline(&line1, &cap1, f1);
    len2 = getline(&line2, &cap2, f2);

    /* Двовказівниковий марш O(N + M) */
    while (len1 > 0 && len2 > 0) {
        /* Прибираємо символ переносу рядка */
        if (line1[len1 - 1] == '\n') line1[--len1] = '\0';
        if (line2[len2 - 1] == '\n') line2[--len2] = '\0';

        /* Копії рядків для виділення ключів без пошкодження вихідного тексту */
        char key1_buf[256], key2_buf[256];
        char *d1 = memchr(line1, DELIM, len1);
        char *d2 = memchr(line2, DELIM, len2);

        size_t k1_len = d1 ? (size_t)(d1 - line1) : (size_t)len1;
        size_t k2_len = d2 ? (size_t)(d2 - line2) : (size_t)len2;

        snprintf(key1_buf, sizeof(key1_buf), "%.*s", (int)k1_len, line1);
        snprintf(key2_buf, sizeof(key2_buf), "%.*s", (int)k2_len, line2);

        int cmp = strcmp(key1_buf, key2_buf);
        if (cmp == 0) {
            /* Спільний ключ: виводимо ключ, залишок файлу 1, залишок файлу 2 */
            const char *val1 = d1 ? d1 + 1 : "";
            const char *val2 = d2 ? d2 + 1 : "";
            printf("%s\t%s\t%s\n", key1_buf, val1, val2);

            len1 = getline(&line1, &cap1, f1);
            len2 = getline(&line2, &cap2, f2);
        } else if (cmp < 0) {
            /* Ключ 1 менший — просуваємо файл 1 */
            len1 = getline(&line1, &cap1, f1);
        } else {
            /* Ключ 2 менший — просуваємо файл 2 */
            len2 = getline(&line2, &cap2, f2);
        }
    }

    free(line1);
    free(line2);
    fclose(f1);
    fclose(f2);
    return EXIT_SUCCESS;
}
