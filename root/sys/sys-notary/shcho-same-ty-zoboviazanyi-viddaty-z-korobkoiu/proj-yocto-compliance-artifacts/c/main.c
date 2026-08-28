#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 2048

/* Читання файлу ліцензії та запис його вмісту до результуючого буклету */
static int append_license_text(FILE *out, const char *lic_path) {
    FILE *in = fopen(lic_path, "r");
    if (!in) {
        fprintf(stderr, "Помилка: не вдалося відкрити файл ліцензії: %s\n", lic_path);
        return -1;
    }

    char buffer[MAX_LINE];
    while (fgets(buffer, sizeof(buffer), in)) {
        fputs(buffer, out);
    }

    fclose(in);
    return 0;
}

/* Генератор консолідованого буклету Open Source Notices з CSV-маніфесту */
int generate_notices(const char *csv_path, const char *lic_dir, const char *out_path) {
    FILE *csv = fopen(csv_path, "r");
    if (!csv) {
        fprintf(stderr, "Помилка: не вдалося відкрити CSV-маніфест: %s\n", csv_path);
        return -1;
    }

    FILE *out = fopen(out_path, "w");
    if (!out) {
        fclose(csv);
        fprintf(stderr, "Помилка: не вдалося створити вихідний файл: %s\n", out_path);
        return -1;
    }

    fprintf(out, "================================================================================\n");
    fprintf(out, "                    OPEN SOURCE SOFTWARE NOTICES & LICENSES\n");
    fprintf(out, "================================================================================\n\n");

    char line[MAX_LINE];
    int is_header = 1;

    while (fgets(line, sizeof(line), csv)) {
        if (is_header) {
            is_header = 0;
            continue; /* Пропуск заголовка CSV */
        }

        /* Розбір рядка вигляду: "pkg","ver","license","lic_file","src_tar","url" */
        char pkg[128], ver[64], lic[128], lic_file[128];
        char *token = strtok(line, ",\"\r\n");
        if (!token) continue;
        strncpy(pkg, token, sizeof(pkg) - 1);

        token = strtok(NULL, ",\"\r\n");
        if (!token) continue;
        strncpy(ver, token, sizeof(ver) - 1);

        token = strtok(NULL, ",\"\r\n");
        if (!token) continue;
        strncpy(lic, token, sizeof(lic) - 1);

        token = strtok(NULL, ",\"\r\n");
        if (!token) continue;
        strncpy(lic_file, token, sizeof(lic_file) - 1);

        fprintf(out, "--------------------------------------------------------------------------------\n");
        fprintf(out, "Package: %s (version: %s)\n", pkg, ver);
        fprintf(out, "SPDX License: %s\n", lic);
        fprintf(out, "--------------------------------------------------------------------------------\n\n");

        char full_lic_path[512];
        snprintf(full_lic_path, sizeof(full_lic_path), "%s/%s-%s/%s", lic_dir, pkg, ver, lic_file);

        if (append_license_text(out, full_lic_path) != 0) {
            /* Якщо специфічного файлу версії немає, спробуємо знайти загальний */
            snprintf(full_lic_path, sizeof(full_lic_path), "%s/%s/%s", lic_dir, pkg, lic_file);
            append_license_text(out, full_lic_path);
        }
        fprintf(out, "\n\n");
    }

    fclose(csv);
    fclose(out);
    return 0;
}
