/* Приклад використання C API / системного інтерфейсу читання бази компіляції */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Структура для збереження однієї команди одиниці трансляції */
typedef struct {
    char directory[1024];
    char file[1024];
    char command[4096];
} CompileEntry;

/* Простий лінійний парсер записів бази компіляції */
int parse_simple_compdb(const char* filepath, CompileEntry* entries, int max_entries) {
    FILE* fp = fopen(filepath, "r");
    if (!fp) {
        perror("Не вдалося відкрити compile_commands.json");
        return -1;
    }

    char line[1024];
    int count = 0;
    CompileEntry current;
    memset(&current, 0, sizeof(current));

    while (fgets(line, sizeof(line), fp) && count < max_entries) {
        char* dir_pos = strstr(line, "\"directory\":");
        char* file_pos = strstr(line, "\"file\":");
        char* cmd_pos = strstr(line, "\"command\":");

        if (dir_pos) {
            sscanf(dir_pos, "\"directory\": \"%1023[^\"]\"", current.directory);
        } else if (file_pos) {
            sscanf(file_pos, "\"file\": \"%1023[^\"]\"", current.file);
        } else if (cmd_pos) {
            sscanf(cmd_pos, "\"command\": \"%4095[^\"]\"", current.command);
            /* Завершення опису поточного об'єкта */
            entries[count++] = current;
            memset(&current, 0, sizeof(current));
        }
    }

    fclose(fp);
    return count;
}

int main(int argc, char** argv) {
    const char* db_path = (argc > 1) ? argv[1] : "build/compile_commands.json";
    CompileEntry entries[64];

    int total = parse_simple_compdb(db_path, entries, 64);
    if (total <= 0) {
        fprintf(stderr, "Записів компіляції не знайдено або сталася помилка.\n");
        return 1;
    }

    printf("Успішно завантажено записів: %d\n", total);
    for (int i = 0; i < total; ++i) {
        printf("[%d] Файл: %s\n    Каталог: %s\n", i + 1, entries[i].file, entries[i].directory);
    }

    return 0;
}
