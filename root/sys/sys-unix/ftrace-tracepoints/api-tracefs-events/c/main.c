#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void parse_event_format(const char *path) {
    FILE *f = fopen(path, "re");
    if (!f) {
        perror("Помилка відкриття format файлу");
        return;
    }

    char line[256];
    printf("Розбір структури події: %s\n", path);
    while (fgets(line, sizeof(line), f)) {
        char field_name[64];
        int offset = 0, size = 0, is_signed = 0;
        
        if (strstr(line, "field:") && !strstr(line, "common_")) {
            char *field_start = strstr(line, "field:") + 6;
            char *semicolon = strchr(field_start, ';');
            if (semicolon) {
                *semicolon = '\0';
                sscanf(semicolon + 1, "\toffset:%d;\tsize:%d;\tsigned:%d;",
                       &offset, &size, &is_signed);
                printf("  Поле: %-25s | Зміщення: %3d | Розмір: %2d байт | Знак: %d\n",
                       field_start, offset, size, is_signed);
            }
        }
    }
    fclose(f);
}

int main(void) {
    parse_event_format("/sys/kernel/tracing/events/sched/sched_switch/format");
    return 0;
}
