#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <iomanip>
#include <filesystem>
#include <system_error>
#include <elf.h>

class AuxvProcParser {
public:
    static constexpr std::string_view type_to_string(uint64_t type) noexcept {
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
            case AT_UID:           return "AT_UID";
            case AT_EUID:          return "AT_EUID";
            case AT_GID:           return "AT_GID";
            case AT_EGID:          return "AT_EGID";
            case AT_PLATFORM:      return "AT_PLATFORM";
            case AT_HWCAP:         return "AT_HWCAP";
            case AT_CLKTCK:        return "AT_CLKTCK";
            case AT_SECURE:        return "AT_SECURE";
            case AT_RANDOM:        return "AT_RANDOM";
            case AT_HWCAP2:        return "AT_HWCAP2";
            case AT_EXECFN:        return "AT_EXECFN";
            case AT_SYSINFO_EHDR:  return "AT_SYSINFO_EHDR";
            default:               return "AT_UNKNOWN";
        }
    }

    static void parse() {
        std::ifstream file("/proc/self/auxv", std::ios::binary);
        if (!file.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити /proc/self/auxv");
        }

        std::cout << "=== ДЕМАРШАЛІЗАЦІЯ /proc/self/auxv (C++) ===\n";

        Elf64_auxv_t entry{};
        while (file.read(reinterpret_cast<char*>(&entry), sizeof(entry))) {
            if (entry.a_type == AT_NULL) {
                std::cout << "[" << std::setw(2) << entry.a_type << "] " 
                          << std::left << std::setw(18) << "AT_NULL" 
                          << " -> КІНЕЦЬ ВЕКТОРА\n";
                break;
            }

            const auto name = type_to_string(entry.a_type);
            std::cout << "[" << std::setw(2) << entry.a_type << "] " 
                      << std::left << std::setw(18) << name << " -> ";

            if (entry.a_type == AT_EXECFN || entry.a_type == AT_PLATFORM) {
                const char* str_ptr = reinterpret_cast<const char*>(entry.a_un.a_ptr);
                std::cout << (str_ptr ? str_ptr : "null") << "\n";
            } else {
                std::cout << "0x" << std::hex << entry.a_un.a_val 
                          << std::dec << " (" << entry.a_un.a_val << ")\n";
            }
        }
    }
};

int main() {
    try {
        AuxvProcParser::parse();
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
