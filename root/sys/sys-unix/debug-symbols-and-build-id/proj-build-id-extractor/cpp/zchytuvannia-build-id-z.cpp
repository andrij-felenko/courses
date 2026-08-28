#include <link.h>
#include <iostream>
#include <string_view>
#include <format>
#include <span>

static int callback(dl_phdr_info *info, size_t, void *) {
    std::string_view name = (info->dlpi_name && info->dlpi_name[0]) ? info->dlpi_name : "головний бінарник";
    std::cout << std::format("Завантажений модуль: {} (базова адреса: 0x{:x})\n", name, info->dlpi_addr);
    
    std::span<const Elf64_Phdr> phdrs(info->dlpi_phdr, info->dlpi_phnum);
    for (const auto &phdr : phdrs) {
        if (phdr.p_type == PT_NOTE) {
            const auto *note_addr = reinterpret_cast<const uint8_t *>(info->dlpi_addr + phdr.p_vaddr);
            // Виклик C++ методу вилучення Build ID
        }
    }
    return 0;
}
