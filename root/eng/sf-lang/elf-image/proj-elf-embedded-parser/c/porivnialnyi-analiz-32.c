#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t p_type;
    uint32_t p_flags;
    uint64_t p_offset;
    uint64_t p_vaddr;
    uint64_t p_paddr;
    uint64_t p_filesz;
    uint64_t p_memsz;
    uint64_t p_align;
} Elf64_Phdr_Custom;

bool parse_elf64_segment(const uint8_t* buffer, size_t offset, size_t file_size, Elf64_Phdr_Custom* out_phdr) {
    if (!buffer || !out_phdr) return false;
    if (offset + sizeof(Elf64_Phdr_Custom) > file_size) return false;
    memcpy(out_phdr, buffer + offset, sizeof(Elf64_Phdr_Custom));
    return true;
}
