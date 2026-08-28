/* uki_parser.c — Низькорівневий аналіз PE/COFF секцій UKI мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>

#define DOS_MAGIC 0x5A4D     /* "MZ" */
#define NT_MAGIC  0x00004550 /* "PE\0\0" */

#pragma pack(push, 1)
typedef struct {
    uint16_t e_magic;
    uint8_t  e_res[58];
    uint32_t e_lfanew;
} DosHeader;

typedef struct {
    uint16_t Machine;
    uint16_t NumberOfSections;
    uint32_t TimeDateStamp;
    uint32_t PointerToSymbolTable;
    uint32_t NumberOfSymbols;
    uint16_t SizeOfOptionalHeader;
    uint16_t Characteristics;
} FileHeader;

typedef struct {
    uint32_t Signature;
    FileHeader FileHeader;
} NtHeaders64;

typedef struct {
    uint8_t  Name[8];
    uint32_t VirtualSize;
    uint32_t VirtualAddress;
    uint32_t SizeOfRawData;
    uint32_t PointerToRawData;
    uint32_t PointerToRelocations;
    uint32_t PointerToLinenumbers;
    uint16_t NumberOfRelocations;
    uint16_t NumberOfLinenumbers;
    uint32_t Characteristics;
} SectionHeader;
#pragma pack(pop)

static void parse_uki_sections(const uint8_t *map, size_t size) {
    if (size < sizeof(DosHeader)) {
        fprintf(stderr, "Помилка: файл занадто малий для DOS-заголовка\n");
        return;
    }

    const DosHeader *dos = (const DosHeader *)map;
    if (dos->e_magic != DOS_MAGIC) {
        fprintf(stderr, "Помилка: відсутній сигнатура MZ\n");
        return;
    }

    if (dos->e_lfanew + sizeof(NtHeaders64) > size) {
        fprintf(stderr, "Помилка: некоректне зміщення PE-заголовка\n");
        return;
    }

    const NtHeaders64 *nt = (const NtHeaders64 *)(map + dos->e_lfanew);
    if (nt->Signature != NT_MAGIC) {
        fprintf(stderr, "Помилка: відсутня сигнатура PE\\0\\0\n");
        return;
    }

    uint16_t num_sections = nt->FileHeader.NumberOfSections;
    uint32_t sec_offset = dos->e_lfanew + sizeof(uint32_t) + sizeof(FileHeader) + 
                         nt->FileHeader.SizeOfOptionalHeader;

    printf("Знайдено PE-секцій: %u\n", num_sections);
    printf("-----------------------------------------------------\n");

    for (uint16_t i = 0; i < num_sections; i++) {
        if (sec_offset + sizeof(SectionHeader) > size) break;
        const SectionHeader *sec = (const SectionHeader *)(map + sec_offset);
        
        char name[9] = {0};
        memcpy(name, sec->Name, 8);

        printf("[%02u] Секція: %-8s | Файлове зміщення: 0x%08X | Розмір: %u B\n",
               i + 1, name, sec->PointerToRawData, sec->SizeOfRawData);

        /* Друк вмісту текстових секцій .cmdline та .osrel */
        if (strcmp(name, ".cmdline") == 0 || strcmp(name, ".osrel") == 0) {
            if (sec->PointerToRawData + sec->SizeOfRawData <= size) {
                printf("     Вміст (%s):\n     \"%.*s\"\n", 
                       name, (int)sec->SizeOfRawData, (const char *)(map + sec->PointerToRawData));
            }
        }

        sec_offset += sizeof(SectionHeader);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <path-to-uki.efi>\n", argv[0]);
        return 1;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити файл");
        return 1;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("Помилка отримання розміру");
        close(fd);
        return 1;
    }

    uint8_t *map = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) {
        perror("Помилка mmap");
        close(fd);
        return 1;
    }

    parse_uki_sections(map, st.st_size);

    munmap(map, st.st_size);
    close(fd);
    return 0;
}
