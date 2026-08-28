#include <iostream>
#include <fstream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <elf.h>

namespace elf_inspector {

// RAII обгортка для безпечного управління відображенням пам'яті
class MemoryMappedFile {
    void* data_ = nullptr;
    size_t size_ = 0;

public:
    explicit MemoryMappedFile(const char* path) {
        int fd = ::open(path, O_RDONLY);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити файл");
        }

        struct stat st{};
        if (::fstat(fd, &st) < 0) {
            ::close(fd);
            throw std::system_error(errno, std::generic_category(), "Помилка отримання статусу fstat");
        }

        size_ = static_cast<size_t>(st.st_size);
        if (size_ < sizeof(Elf64_Ehdr)) {
            ::close(fd);
            throw std::runtime_error("Розмір файла менший за заголовок ELF");
        }

        data_ = ::mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd, 0);
        ::close(fd); // Дескриптор більше не потрібен після створення mmap

        if (data_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення mmap");
        }
    }

    ~MemoryMappedFile() {
        if (data_ && data_ != MAP_FAILED) {
            ::munmap(data_, size_);
        }
    }

    MemoryMappedFile(const MemoryMappedFile&) = delete;
    MemoryMappedFile& operator=(const MemoryMappedFile&) = delete;

    [[nodiscard]] std::span<const std::byte> bytes() const noexcept {
        return {static_cast<const std::byte*>(data_), size_};
    }
};

std::string_view segment_type_to_string(uint32_t p_type) noexcept {
    switch (p_type) {
        case PT_NULL:         return "PT_NULL";
        case PT_LOAD:         return "PT_LOAD";
        case PT_DYNAMIC:      return "PT_DYNAMIC";
        case PT_INTERP:       return "PT_INTERP";
        case PT_NOTE:         return "PT_NOTE";
        case PT_PHDR:         return "PT_PHDR";
        case PT_TLS:          return "PT_TLS";
        case PT_GNU_EH_FRAME: return "PT_GNU_EH_FRAME";
        case PT_GNU_STACK:    return "PT_GNU_STACK";
        case PT_GNU_RELRO:    return "PT_GNU_RELRO";
        default:              return "UNKNOWN";
    }
}

std::string format_flags(uint32_t flags) {
    std::string res;
    res.reserve(3);
    res += (flags & PF_R) ? 'R' : '-';
    res += (flags & PF_W) ? 'W' : '-';
    res += (flags & PF_X) ? 'E' : '-';
    return res;
}

void parse_and_print(const char* filepath) {
    MemoryMappedFile mapped_file(filepath);
    auto buffer = mapped_file.bytes();

    const auto* ehdr = reinterpret_cast<const Elf64_Ehdr*>(buffer.data());

    if (std::string_view(reinterpret_cast<const char*>(ehdr->e_ident), SELFMAG) != ELFMAG) {
        throw std::runtime_error("Невалідний магічний підпис ELF");
    }

    if (ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
        throw std::runtime_error("Файл не належить до 64-бітного класу ELF");
    }

    std::cout << "=== ELF Аналізатор (C++20): " << filepath << " ===\n";
    std::cout << "Точка входу: 0x" << std::hex << ehdr->e_entry << std::dec << "\n";
    std::cout << "Кількість програмних заголовків: " << ehdr->e_phnum << "\n\n";

    const size_t pht_offset = ehdr->e_phoff;
    const size_t pht_bytes = ehdr->e_phnum * sizeof(Elf64_Phdr);

    if (pht_offset + pht_bytes > buffer.size()) {
        throw std::out_of_range("Таблиця PHT виходить за межі бінарного файлу");
    }

    std::span<const Elf64_Phdr> phdrs(
        reinterpret_cast<const Elf64_Phdr*>(buffer.data() + pht_offset),
        ehdr->e_phnum
    );

    for (const auto& ph : phdrs) {
        std::cout << segment_type_to_string(ph.p_type) << " | "
                  << "Offset: 0x" << std::hex << ph.p_offset << " | "
                  << "VAddr: 0x" << ph.p_vaddr << " | "
                  << "FileSiz: 0x" << ph.p_filesz << " | "
                  << "MemSiz: 0x" << ph.p_memsz << " | "
                  << "Flags: " << format_flags(ph.p_flags) << std::dec << "\n";

        if (ph.p_type == PT_INTERP && (ph.p_offset + ph.p_filesz <= buffer.size())) {
            std::string_view interp(
                reinterpret_cast<const char*>(buffer.data() + ph.p_offset)
            );
            std::cout << "  -> Шлях до динамічного завантажувача: " << interp << "\n";
        }
    }
}

} // namespace elf_inspector

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <path-to-elf>\n";
        return 1;
    }

    try {
        elf_inspector::parse_and_print(argv[1]);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка аналізу: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
