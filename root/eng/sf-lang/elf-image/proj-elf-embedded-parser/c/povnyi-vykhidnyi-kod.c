#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define EI_NIDENT 16

/* Типи двійкових файлів e_type */
#define ET_NONE   0
#define ET_REL    1
#define ET_EXEC   2
#define ET_DYN    3

/* Архітектури процесорів e_machine */
#define EM_ARM    40
#define EM_RISCV  243

/* Типи сегментів p_type */
#define PT_NULL   0
#define PT_LOAD   1
#define PT_DYNAMIC 2
#define PT_INTERP 3
#define PT_NOTE   4
#define PT_SHLIB  5
#define PT_PHDR   6

/* Прапорці сегментів p_flags */
#define PF_X      0x1
#define PF_W      0x2
#define PF_R      0x4

/* Типи секцій sh_type */
#define SHT_NULL     0
#define SHT_PROGBITS 1
#define SHT_SYMTAB   2
#define SHT_STRTAB   3
#define SHT_RELA     4
#define SHT_HASH     5
#define SHT_DYNAMIC  6
#define SHT_NOTE     7
#define SHT_NOBITS   8
#define SHT_REL      9

/* Прапорці секцій sh_flags */
#define SHF_WRITE     0x1
#define SHF_ALLOC     0x2
#define SHF_EXECINSTR 0x4

#pragma pack(push, 1)
typedef struct {
    uint8_t  e_ident[EI_NIDENT];
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
} Elf32_Ehdr;

typedef struct {
    uint32_t p_type;
    uint32_t p_offset;
    uint32_t p_vaddr;
    uint32_t p_paddr;
    uint32_t p_filesz;
    uint32_t p_memsz;
    uint32_t p_flags;
    uint32_t p_align;
} Elf32_Phdr;

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
} Elf32_Shdr;

typedef struct {
    uint32_t st_name;
    uint32_t st_value;
    uint32_t st_size;
    uint8_t  st_info;
    uint8_t  st_other;
    uint16_t st_shndx;
} Elf32_Sym;
#pragma pack(pop)

/* Безпечний буфер пам'яті */
typedef struct {
    const uint8_t* data;
    size_t size;
} SafeBuffer;

static bool safe_read(const SafeBuffer* buf, size_t offset, void* dst, size_t len) {
    if (!buf || !dst || !buf->data) return false;
    if (offset + len < offset) return false; /* Захист від цілочисельного переповнення */
    if (offset + len > buf->size) return false; /* Захист від виходу за межі буфера */
    memcpy(dst, buf->data + offset, len);
    return true;
}

static const char* get_string(const SafeBuffer* buf, size_t strtab_offset, size_t strtab_size, uint32_t name_offset) {
    if (name_offset >= strtab_size) return "<invalid-string-offset>";
    size_t abs_offset = strtab_offset + name_offset;
    if (abs_offset >= buf->size) return "<invalid-buffer-offset>";
    return (const char*)(buf->data + abs_offset);
}

/* Структура для звіту карти пам'яті */
typedef struct {
    uint32_t flash_total_bytes;
    uint32_t sram_data_bytes;
    uint32_t sram_bss_bytes;
    uint32_t entry_point;
    uint16_t machine_arch;
    bool is_arm_thumb;
} FirmwareMemorySummary;

bool parse_elf_firmware(const uint8_t* raw_bytes, size_t raw_size, FirmwareMemorySummary* out_summary) {
    if (!raw_bytes || raw_size < sizeof(Elf32_Ehdr) || !out_summary) {
        return false;
    }

    SafeBuffer buf = { .data = raw_bytes, .size = raw_size };
    Elf32_Ehdr ehdr;
    if (!safe_read(&buf, 0, &ehdr, sizeof(Elf32_Ehdr))) {
        return false;
    }

    /* Перевірка магічних байтів ELF */
    if (ehdr.e_ident[0] != 0x7F || ehdr.e_ident[1] != 'E' ||
        ehdr.e_ident[2] != 'L'  || ehdr.e_ident[3] != 'F') {
        fprintf(stderr, "Помилка: Некоректне магічне число ELF!\n");
        return false;
    }

    if (ehdr.e_ident[4] != 1) {
        fprintf(stderr, "Помилка: Підтримуються лише 32-бітні ELF-образи!\n");
        return false;
    }

    memset(out_summary, 0, sizeof(FirmwareMemorySummary));
    out_summary->entry_point = ehdr.e_entry;
    out_summary->machine_arch = ehdr.e_machine;
    out_summary->is_arm_thumb = (ehdr.e_machine == EM_ARM) && (ehdr.e_entry & 1);

    printf("========================================================\n");
    printf("ELF-заголовок валідовано успішно:\n");
    printf("  Архітектура: %s (Код: %u)\n", 
           ehdr.e_machine == EM_ARM ? "ARM 32-bit" : 
           (ehdr.e_machine == EM_RISCV ? "RISC-V" : "Інша"), ehdr.e_machine);
    printf("  Точка входу (e_entry): 0x%08X %s\n", 
           ehdr.e_entry, out_summary->is_arm_thumb ? "[Thumb Mode]" : "");
    printf("  Сегментів (Program Headers): %u\n", ehdr.e_phnum);
    printf("  Секцій (Section Headers):    %u\n", ehdr.e_shnum);
    printf("========================================================\n\n");

    /* 1. Обробка Program Headers (сегменти завантаження) */
    printf("--- Таблиця завантажуваних сегментів (Program Headers) ---\n");
    for (uint16_t i = 0; i < ehdr.e_phnum; ++i) {
        size_t ph_offset = ehdr.e_phoff + (size_t)i * ehdr.e_phentsize;
        Elf32_Phdr phdr;
        if (!safe_read(&buf, ph_offset, &phdr, sizeof(Elf32_Phdr))) {
            fprintf(stderr, "Помилка зчитування Program Header #%u\n", i);
            return false;
        }

        if (phdr.p_type == PT_LOAD) {
            printf("  Сегмент #%u [PT_LOAD]:\n", i);
            printf("    Файлове зміщення: 0x%08X, Розмір у файлі: %u байтів\n", phdr.p_offset, phdr.p_filesz);
            printf("    Фізична адреса (LMA): 0x%08X\n", phdr.p_paddr);
            printf("    Віртуальна адреса (VMA): 0x%08X\n", phdr.p_vaddr);
            printf("    Пам'ять (p_memsz):       %u байтів\n", phdr.p_memsz);
            printf("    Права доступу:          %c%c%c\n",
                   (phdr.p_flags & PF_R) ? 'R' : '-',
                   (phdr.p_flags & PF_W) ? 'W' : '-',
                   (phdr.p_flags & PF_X) ? 'X' : '-');

            if (phdr.p_flags & PF_X) {
                out_summary->flash_total_bytes += phdr.p_filesz;
            } else if (phdr.p_flags & PF_W) {
                out_summary->sram_data_bytes += phdr.p_filesz;
                if (phdr.p_memsz > phdr.p_filesz) {
                    out_summary->sram_bss_bytes += (phdr.p_memsz - phdr.p_filesz);
                }
            }
        }
    }
    printf("\n");

    /* 2. Обробка Section Headers та розбір .shstrtab */
    if (ehdr.e_shnum > 0 && ehdr.e_shstrndx < ehdr.e_shnum) {
        size_t shstrtab_desc_offset = ehdr.e_shoff + (size_t)ehdr.e_shstrndx * ehdr.e_shentsize;
        Elf32_Shdr shstrtab_hdr;
        if (safe_read(&buf, shstrtab_desc_offset, &shstrtab_hdr, sizeof(Elf32_Shdr))) {
            printf("--- Таблиця секцій програми (Section Headers) ---\n");
            for (uint16_t i = 0; i < ehdr.e_shnum; ++i) {
                size_t sh_offset = ehdr.e_shoff + (size_t)i * ehdr.e_shentsize;
                Elf32_Shdr shdr;
                if (safe_read(&buf, sh_offset, &shdr, sizeof(Elf32_Shdr))) {
                    const char* sec_name = get_string(&buf, shstrtab_hdr.sh_offset, shstrtab_hdr.sh_size, shdr.sh_name);
                    printf("  [%02u] %-20s VMA: 0x%08X  Розмір: %6u B  Зміщення: 0x%06X  Тип: %u  Прапорці: 0x%X\n",
                           i, sec_name, shdr.sh_addr, shdr.sh_size, shdr.sh_offset, shdr.sh_type, shdr.sh_flags);
                }
            }
            printf("\n");
        }
    }

    return true;
}

/* Генератор сирого двійкового файлу (.bin) з сегментів PT_LOAD */
bool export_raw_binary(const uint8_t* raw_bytes, size_t raw_size, const char* out_filename) {
    if (!raw_bytes || !out_filename) return false;
    SafeBuffer buf = { .data = raw_bytes, .size = raw_size };
    Elf32_Ehdr ehdr;
    if (!safe_read(&buf, 0, &ehdr, sizeof(Elf32_Ehdr))) return false;

    FILE* f_out = fopen(out_filename, "wb");
    if (!f_out) {
        fprintf(stderr, "Помилка відкриття файлу для запису: %s\n", out_filename);
        return false;
    }

    /* Знаходимо всі сегменти PT_LOAD і записуємо їхні дані послідовно */
    for (uint16_t i = 0; i < ehdr.e_phnum; ++i) {
        size_t ph_offset = ehdr.e_phoff + (size_t)i * ehdr.e_phentsize;
        Elf32_Phdr phdr;
        if (safe_read(&buf, ph_offset, &phdr, sizeof(Elf32_Phdr))) {
            if (phdr.p_type == PT_LOAD && phdr.p_filesz > 0) {
                if (phdr.p_offset + phdr.p_filesz <= raw_size) {
                    fwrite(raw_bytes + phdr.p_offset, 1, phdr.p_filesz, f_out);
                }
            }
        }
    }

    fclose(f_out);
    printf("Сирий двійковий образ успішно експортовано: %s\n", out_filename);
    return true;
}

/* Генератор Intel HEX файлу (.hex) */
bool export_intel_hex(const uint8_t* raw_bytes, size_t raw_size, const char* out_filename) {
    if (!raw_bytes || !out_filename) return false;
    SafeBuffer buf = { .data = raw_bytes, .size = raw_size };
    Elf32_Ehdr ehdr;
    if (!safe_read(&buf, 0, &ehdr, sizeof(Elf32_Ehdr))) return false;

    FILE* f_out = fopen(out_filename, "w");
    if (!f_out) return false;

    uint32_t current_upper_addr = 0xFFFFFFFF;

    for (uint16_t i = 0; i < ehdr.e_phnum; ++i) {
        size_t ph_offset = ehdr.e_phoff + (size_t)i * ehdr.e_phentsize;
        Elf32_Phdr phdr;
        if (safe_read(&buf, ph_offset, &phdr, sizeof(Elf32_Phdr))) {
            if (phdr.p_type == PT_LOAD && phdr.p_filesz > 0) {
                uint32_t target_addr = phdr.p_paddr;
                const uint8_t* seg_data = raw_bytes + phdr.p_offset;
                size_t remaining = phdr.p_filesz;

                while (remaining > 0) {
                    uint32_t upper_addr = (target_addr >> 16) & 0xFFFF;
                    if (upper_addr != current_upper_addr) {
                        /* Запис Extended Linear Address Record (Type 04) */
                        current_upper_addr = upper_addr;
                        uint8_t len = 2;
                        uint16_t offset = 0;
                        uint8_t type = 4;
                        uint8_t hi = (upper_addr >> 8) & 0xFF;
                        uint8_t lo = upper_addr & 0xFF;
                        uint8_t cksum = len + (offset >> 8) + (offset & 0xFF) + type + hi + lo;
                        cksum = (uint8_t)(0x100 - (cksum & 0xFF));
                        fprintf(f_out, ":%02X%04X%02X%02X%02X%02X\n", len, offset, type, hi, lo, cksum);
                    }

                    uint8_t chunk_len = (remaining > 16) ? 16 : (uint8_t)remaining;
                    uint16_t lower_addr = target_addr & 0xFFFF;
                    uint8_t cksum = chunk_len + (lower_addr >> 8) + (lower_addr & 0xFF) + 0; // Type 00 (Data)

                    fprintf(f_out, ":%02X%04X00", chunk_len, lower_addr);
                    for (uint8_t b = 0; b < chunk_len; ++b) {
                        uint8_t val = seg_data[b];
                        cksum += val;
                        fprintf(f_out, "%02X", val);
                    }
                    cksum = (uint8_t)(0x100 - (cksum & 0xFF));
                    fprintf(f_out, "%02X\n", cksum);

                    target_addr += chunk_len;
                    seg_data += chunk_len;
                    remaining -= chunk_len;
                }
            }
        }
    }

    /* Запис End of File Record (Type 01) */
    fprintf(f_out, ":00000001FF\n");
    fclose(f_out);
    printf("Файл Intel HEX успішно згенеровано: %s\n", out_filename);
    return true;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("Використання: %s <firmware.elf> [out.bin] [out.hex]\n", argv[0]);
        return 1;
    }

    FILE* f_in = fopen(argv[1], "rb");
    if (!f_in) {
        perror("Не вдалося відкрити ELF-файл");
        return 1;
    }

    fseek(f_in, 0, SEEK_END);
    long file_size = ftell(f_in);
    fseek(f_in, 0, SEEK_SET);

    if (file_size <= 0) {
        fclose(f_in);
        fprintf(stderr, "Помилка: Файл порожній!\n");
        return 1;
    }

    uint8_t* buffer = (uint8_t*)malloc((size_t)file_size);
    if (!buffer) {
        fclose(f_in);
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    if (fread(buffer, 1, (size_t)file_size, f_in) != (size_t)file_size) {
        free(buffer);
        fclose(f_in);
        fprintf(stderr, "Помилка зчитування вмісту файлу!\n");
        return 1;
    }
    fclose(f_in);

    FirmwareMemorySummary summary;
    if (parse_elf_firmware(buffer, (size_t)file_size, &summary)) {
        printf("--- Підсумок використання пам'яті мікроконтролера ---\n");
        printf("  Flash Memory (Код + Константи + LMA .data): %6u байтів\n", summary.flash_total_bytes);
        printf("  SRAM Data    (Ініціалізовані змінні VMA):    %6u байтів\n", summary.sram_data_bytes);
        printf("  SRAM BSS     (Обнулені змінні в RAM):        %6u байтів\n", summary.sram_bss_bytes);
        printf("  Всього зайнято оперативної пам'яті SRAM:     %6u байтів\n", 
               summary.sram_data_bytes + summary.sram_bss_bytes);
        printf("========================================================\n");

        if (argc >= 3) {
            export_raw_binary(buffer, (size_t)file_size, argv[2]);
        }
        if (argc >= 4) {
            export_intel_hex(buffer, (size_t)file_size, argv[3]);
        }
    }

    free(buffer);
    return 0;
}
