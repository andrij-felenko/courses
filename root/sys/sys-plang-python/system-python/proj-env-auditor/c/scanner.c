/* scanner.c — Аудит маркерів PEP 668 та каталогів dist-packages */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/stat.h>

#define MAX_PATH 4096
#define BUFFER_SIZE 2048

static int check_file_exists(const char *path) {
    struct stat st;
    return (stat(path, &st) == 0 && S_ISREG(st.st_mode));
}

static void read_pep668_message(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) return;
    
    char line[BUFFER_SIZE];
    printf("Файл маркер: %s\n", path);
    printf("--- Вміст EXTERNALLY-MANAGED ---\n");
    while (fgets(line, sizeof(line), f)) {
        fputs(line, stdout);
    }
    printf("--------------------------------\n");
    fclose(f);
}

int main(int argc, char *argv[]) {
    const char *candidates[] = {
        "/usr/lib/python3.12/EXTERNALLY-MANAGED",
        "/usr/lib64/python3.12/EXTERNALLY-MANAGED",
        "/usr/lib/python3.11/EXTERNALLY-MANAGED",
        "/usr/lib64/python3.11/EXTERNALLY-MANAGED",
        "/usr/lib/python3/EXTERNALLY-MANAGED",
        NULL
    };

    printf("=== POSIX C АУДИТОР PEP 668 ===\n");
    int found = 0;
    for (int i = 0; candidates[i] != NULL; ++i) {
        if (check_file_exists(candidates[i])) {
            printf("[ЗНАЙДЕНО] Системне оточення заблоковано PEP 668.\n");
            read_pep668_message(candidates[i]);
            found = 1;
            break;
        }
    }

    if (!found) {
        printf("[ВІДСУТНІЙ] Маркер EXTERNALLY-MANAGED не знайдено за стандартними шляхами.\n");
    }

    return 0;
}
