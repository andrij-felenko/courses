#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static uint32_t generate_crc32_entry(uint32_t byte, uint32_t polynomial) {
    uint32_t crc = byte;
    for (int bit = 0; bit < 8; ++bit) {
        if (crc & 1U) {
            crc = (crc >> 1U) ^ polynomial;
        } else {
            crc = crc >> 1U;
        }
    }
    return crc;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_вихідного_файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    FILE *out = fopen(argv[1], "w");
    if (!out) {
        perror("Не вдалося відкрити вихідний файл для запису");
        return EXIT_FAILURE;
    }

    const uint32_t polynomial = 0xEDB88320U; // Стандартний поліном IEEE 802.3

    fprintf(out, "/* Автоматично згенеровано утилітою table_gen на хості. Не редагувати! */\n");
    fprintf(out, "#include <stdint.h>\n\n");
    fprintf(out, "const uint32_t g_crc32_lookup[256] = {\n");

    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t entry = generate_crc32_entry(i, polynomial);
        fprintf(out, "    0x%08XU%s%s", entry, (i < 255) ? "," : "", (i % 8 == 7) ? "\n" : " ");
    }

    fprintf(out, "};\n");
    fclose(out);
    return EXIT_SUCCESS;
}
