#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define ELF_MAGIC0       0x7F
#define ELF_MAGIC1       'E'
#define ELF_MAGIC2       'L'
#define ELF_MAGIC3       'F'

#define FLASH_LIMIT_BYTES (512 * 1024)   /* 512 КБ Flash */
#define RAM_LIMIT_BYTES   (128 * 1024)   /* 128 КБ RAM   */

typedef struct {
    uint8_t  e_ident[16];
    uint16_t e_type;
    uint16_t e_machine;
    uint32_t e_version;
    uint32_t e_entry;
    uint32_t e_phoff;
    uint32_t e_shoff;
    uint32_t e_flags;
    uint16_t e_ehsize;
    uint16_t e_phentsize;
    uint16_t e_phnum;
    uint16_t e_shentsize;
    uint16_t e_shnum;
    uint16_t e_shstrndx;
} Elf32_Header;

typedef struct {
    uint32_t sh_name;
    uint32_t sh_type;
    uint32_t sh_flags;
    uint32_t sh_addr;
    uint32_t sh_offset;
    uint32_t sh_size;
    uint32_t sh_link;
    uint32_t sh_info;
    uint32_t sh_addralign;
    uint32_t sh_entsize;
} Elf32_SectionHeader;

static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_образу.elf>\n", argv[0]);
        return 2;
    }

    const char *filepath = argv[1];
    FILE *f = fopen(filepath, "rb");
    if (!f) {
        fprintf(stderr, "ПОМИЛКА: Неможливо відкрити файл '%s'\n", filepath);
        return 1;
    }

    Elf32_Header header;
    if (fread(&header, sizeof(Elf32_Header), 1, f) != 1) {
        fprintf(stderr, "ПОМИЛКА: Не вдалося прочитати заголовок ELF\n");
        fclose(f);
        return 1;
    }

    if (header.e_ident[0] != ELF_MAGIC0 || header.e_ident[1] != ELF_MAGIC1 ||
        header.e_ident[2] != ELF_MAGIC2 || header.e_ident[3] != ELF_MAGIC3) {
        fprintf(stderr, "ВІДХИЛЕНО: Файл не є коректним ELF-артефактом\n");
        fclose(f);
        return 1;
    }

    if (fseek(f, header.e_shoff, SEEK_SET) != 0) {
        fprintf(stderr, "ПОМИЛКА: Не вдалося перейти до таблиці секцій\n");
        fclose(f);
        return 1;
    }

    Elf32_SectionHeader *sh_table = malloc(sizeof(Elf32_SectionHeader) * header.e_shnum);
    if (!sh_table) {
        fprintf(stderr, "ПОМИЛКА: Брак пам'яті для таблиці секцій\n");
        fclose(f);
        return 1;
    }

    if (fread(sh_table, sizeof(Elf32_SectionHeader), header.e_shnum, f) != header.e_shnum) {
        fprintf(stderr, "ПОМИЛКА: Не вдалося прочитати секції ELF\n");
        free(sh_table);
        fclose(f);
        return 1;
    }

    /* Читання таблиці імен секцій */
    Elf32_SectionHeader *str_sh = &sh_table[header.e_shstrndx];
    char *sh_names = malloc(str_sh->sh_size);
    if (!sh_names) {
        free(sh_table);
        fclose(f);
        return 1;
    }

    fseek(f, str_sh->sh_offset, SEEK_SET);
    if (fread(sh_names, 1, str_sh->sh_size, f) != str_sh->sh_size) {
        fprintf(stderr, "ПОМИЛКА: Помилка читання імен секцій\n");
        free(sh_names);
        free(sh_table);
        fclose(f);
        return 1;
    }

    uint32_t flash_used = 0;
    uint32_t ram_used = 0;
    bool has_dirty_metadata = false;

    for (int i = 0; i < header.e_shnum; ++i) {
        const char *name = &sh_names[sh_table[i].sh_name];
        uint32_t size = sh_table[i].sh_size;

        if (strcmp(name, ".text") == 0 || strcmp(name, ".rodata") == 0) {
            flash_used += size;
        } else if (strcmp(name, ".data") == 0) {
            flash_used += size;
            ram_used += size;
        } else if (strcmp(name, ".bss") == 0) {
            ram_used += size;
        }

        /* Перевірка наявності dirty-рядка у секції rodata */
        if (strcmp(name, ".rodata") == 0 && size > 0) {
            uint8_t *rodata_buf = malloc(size);
            if (rodata_buf) {
                fseek(f, sh_table[i].sh_offset, SEEK_SET);
                if (fread(rodata_buf, 1, size, f) == size) {
                    for (size_t k = 0; k + 6 <= size; ++k) {
                        if (memcmp(&rodata_buf[k], "-dirty", 6) == 0) {
                            has_dirty_metadata = true;
                            break;
                        }
                    }
                }
                free(rodata_buf);
            }
        }
    }

    free(sh_names);
    free(sh_table);

    /* Розрахунок CRC32 всього файлу */
    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    uint8_t *full_file = malloc(file_size);
    if (!full_file) {
        fclose(f);
        return 1;
    }
    fread(full_file, 1, file_size, f);
    fclose(f);

    uint32_t image_crc = calculate_crc32(full_file, file_size);
    free(full_file);

    printf("=== ЗВІТ РЕЛІЗНОГО АРТЕФАКТУ: %s ===\n", filepath);
    printf("  Flash: %u / %u байтів (%.1f%%)\n", flash_used, FLASH_LIMIT_BYTES, (float)flash_used * 100.0f / FLASH_LIMIT_BYTES);
    printf("  RAM:   %u / %u байтів (%.1f%%)\n", ram_used, RAM_LIMIT_BYTES, (float)ram_used * 100.0f / RAM_LIMIT_BYTES);
    printf("  CRC32: 0x%08X\n", image_crc);

    if (has_dirty_metadata) {
        fprintf(stderr, "ВІДХИЛЕНО: Знайдено мітку '-dirty'! Образ зібрано з незакоміченими змінами.\n");
        return 1;
    }

    if (flash_used > FLASH_LIMIT_BYTES) {
        fprintf(stderr, "ВІДХИЛЕНО: Перевищено бюджет Flash на %u байтів!\n", flash_used - FLASH_LIMIT_BYTES);
        return 1;
    }

    if (ram_used > RAM_LIMIT_BYTES) {
        fprintf(stderr, "ВІДХИЛЕНО: Перевищено бюджет RAM на %u байтів!\n", ram_used - RAM_LIMIT_BYTES);
        return 1;
    }

    printf("РЕЗУЛЬТАТ: Образ валідний, чистий та придатний до випуску.\n");
    return 0;
}
