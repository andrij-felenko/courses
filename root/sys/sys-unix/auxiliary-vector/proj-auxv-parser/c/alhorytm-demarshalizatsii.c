#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>

static const char* auxv_type_to_string(uint64_t type) {
    switch (type) {
        case AT_NULL:          return "AT_NULL";
        case AT_IGNORE:        return "AT_IGNORE";
        case AT_EXECFD:        return "AT_EXECFD";
        case AT_PHDR:          return "AT_PHDR";
        case AT_PHENT:         return "AT_PHENT";
        case AT_PHNUM:         return "AT_PHNUM";
        case AT_PAGESZ:        return "AT_PAGESZ";
        case AT_BASE:          return "AT_BASE";
        case AT_FLAGS:         return "AT_FLAGS";
        case AT_ENTRY:         return "AT_ENTRY";
        case AT_NOTELF:        return "AT_NOTELF";
        case AT_UID:           return "AT_UID";
        case AT_EUID:          return "AT_EUID";
        case AT_GID:           return "AT_GID";
        case AT_EGID:          return "AT_EGID";
        case AT_PLATFORM:      return "AT_PLATFORM";
        case AT_HWCAP:         return "AT_HWCAP";
        case AT_CLKTCK:        return "AT_CLKTCK";
        case AT_SECURE:        return "AT_SECURE";
        case AT_BASE_PLATFORM: return "AT_BASE_PLATFORM";
        case AT_RANDOM:        return "AT_RANDOM";
        case AT_HWCAP2:        return "AT_HWCAP2";
        case AT_EXECFN:        return "AT_EXECFN";
        case AT_SYSINFO_EHDR:  return "AT_SYSINFO_EHDR";
        default:               return "AT_UNKNOWN";
    }
}

int parse_proc_auxv(void) {
    int fd = open("/proc/self/auxv", O_RDONLY);
    if (fd < 0) {
        perror("Помилка: не вдалося відкрити /proc/self/auxv");
        return -1;
    }

    Elf64_auxv_t entry;
    ssize_t bytes_read;

    printf("=== ДЕМАРШАЛІЗАЦІЯ /proc/self/auxv (C) ===\n");
    while ((bytes_read = read(fd, &entry, sizeof(entry))) == sizeof(entry)) {
        if (entry.a_type == AT_NULL) {
            printf("[%2lu] %-18s (0x00) -> КІНЕЦЬ ВЕКТОРА\n", (unsigned long)entry.a_type, "AT_NULL");
            break;
        }

        const char* name = auxv_type_to_string(entry.a_type);
        if (entry.a_type == AT_EXECFN || entry.a_type == AT_PLATFORM) {
            printf("[%2lu] %-18s -> %s\n", (unsigned long)entry.a_type, name, (const char*)entry.a_un.a_ptr);
        } else {
            printf("[%2lu] %-18s -> 0x%lx (%lu)\n", 
                   (unsigned long)entry.a_type, name, 
                   (unsigned long)entry.a_un.a_val, 
                   (unsigned long)entry.a_un.a_val);
        }
    }

    close(fd);
    return 0;
}

int main(void) {
    return parse_proc_auxv();
}
