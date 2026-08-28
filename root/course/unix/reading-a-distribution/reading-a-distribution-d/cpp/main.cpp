// Ідіоматична реалізація на C++20 з використанням RAII та типів std::span
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <span>
#include <cstring>
#include <elf.h>

int main(int argc, char* argv[])
{
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <elf-binary>\n";
        return 1;
    }

    std::ifstream file(argv[1], std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Помилка відкриття файлу: " << argv[1] << '\n';
        return 1;
    }

    Elf64_Ehdr ehdr{};
    file.read(reinterpret_cast<char*>(&ehdr), sizeof(ehdr));
    if (!file) {
        std::cerr << "Помилка зчитування заголовка ELF\n";
        return 1;
    }

    if (std::memcmp(ehdr.e_ident, ELFMAG, SELFMAG) != 0 || ehdr.e_ident[EI_CLASS] != ELFCLASS64) {
        std::cerr << "Файл не є валідним 64-бітним ELF двійником\n";
        return 1;
    }

    std::vector<Elf64_Phdr> phdrs(ehdr.e_phnum);
    file.seekg(static_cast<std::streamoff>(ehdr.e_phoff));
    file.read(reinterpret_cast<char*>(phdrs.data()), 
              static_cast<std::streamsize>(ehdr.e_phnum * sizeof(Elf64_Phdr)));

    bool found = false;
    for (const auto& phdr : phdrs) {
        if (phdr.p_type == PT_INTERP) {
            std::string interp(phdr.p_filesz, '\0');
            file.seekg(static_cast<std::streamoff>(phdr.p_offset));
            file.read(interp.data(), static_cast<std::streamsize>(phdr.p_filesz));
            // Видаляємо кінцевий нуль-термінатор для чистого виводу
            if (!interp.empty() && interp.back() == '\0') {
                interp.pop_back();
            }
            std::cout << "ELF Інтерпретатор (PT_INTERP): " << interp << '\n';
            found = true;
            break;
        }
    }

    if (!found) {
        std::cout << "Файл статичний або заголовок PT_INTERP відсутній.\n";
    }

    return 0;
}
