#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Читання 32-бітного цілого числа з формати Big-Endian у Little-Endian
static uint32_t read_uint32_be(const uint8_t *buf) {
    return ((uint32_t)buf[0] << 24) |
           ((uint32_t)buf[1] << 16) |
           ((uint32_t)buf[2] << 8)  |
            (uint32_t)buf[3];
}

// Перевірка, чи є бокс контейнером для вкладених боксів
static int is_container_box(const char *type) {
    return (strcmp(type, "moov") == 0 ||
            strcmp(type, "trak") == 0 ||
            strcmp(type, "mdia") == 0 ||
            strcmp(type, "minf") == 0 ||
            strcmp(type, "stbl") == 0);
}

// Рекурсивний розбір боксів у пам'яті
static void parse_mp4_boxes(const uint8_t *buffer, size_t offset, size_t max_offset, int depth) {
    while (offset + 8 <= max_offset) {
        uint32_t box_size = read_uint32_be(buffer + offset);
        char type_str[5] = {0};
        memcpy(type_str, buffer + offset + 4, 4);

        if (box_size == 0) {
            // Розмір 0 означає, що бокс тягнеться до кінця файлу
            box_size = (uint32_t)(max_offset - offset);
        } else if (box_size < 8) {
            // Некоректна довжина заголовка боксу
            break;
        }

        if (offset + box_size > max_offset) {
            printf("Помилка: бокс %s виходить за межі буфера\n", type_str);
            break;
        }

        // Вивід відступів для візуалізації дерева
        for (int i = 0; i < depth; i++) {
            printf("  ");
        }
        printf("Box: [%s] Size: %u, Offset: %zu\n", type_str, box_size, offset);

        // Якщо це контейнерний бокс, заходимо всередину його тіла
        if (is_container_box(type_str)) {
            parse_mp4_boxes(buffer, offset + 8, offset + box_size, depth + 1);
        }

        offset += box_size;
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Використання: %s <шлях_до_файлу.mp4>\n", argv[0]);
        return 1;
    }

    FILE *file = fopen(argv[1], "rb");
    if (!file) {
        perror("Не вдалося відкрити файл");
        return 1;
    }

    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    if (file_size < 8) {
        printf("Занадто малий файл MP4\n");
        fclose(file);
        return 1;
    }

    uint8_t *buffer = (uint8_t *)malloc(file_size);
    if (!buffer) {
        printf("Помилка виділення пам'яті\n");
        fclose(file);
        return 1;
    }

    if (fread(buffer, 1, file_size, file) != (size_t)file_size) {
        printf("Помилка зчитання файлу\n");
        free(buffer);
        fclose(file);
        return 1;
    }
    fclose(file);

    printf("=== Дерево боксів ISOBMFF / MP4 ===\n");
    parse_mp4_boxes(buffer, 0, (size_t)file_size, 0);

    free(buffer);
    return 0;
}
