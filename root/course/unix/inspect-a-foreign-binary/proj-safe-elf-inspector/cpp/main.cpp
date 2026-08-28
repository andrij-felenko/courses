#include <elf.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#include <cstring>
#include <expected>
#include <filesystem>
#include <format>
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <vector>

namespace fs = std::filesystem;

class MappedFile {
public:
    static std::expected<MappedFile, std::string> open_readonly(const fs::path &path) {
        int fd = ::open(path.c_str(), O_RDONLY | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::format("Не вдалося відкрити файл: {}", std::strerror(errno)));
        }

        struct stat st{};
        if (::fstat(fd, &st) < 0) {
            ::close(fd);
            return std::unexpected(std::format("Не вдалося отримати атрибути файлу: {}", std::strerror(errno)));
        }

        if (st.st_size == 0) {
            ::close(fd);
            return std::unexpected("Файл має нульовий розмір.");
        }

        auto size = static_cast<size_t>(st.st_size);
        void *addr = ::mmap(nullptr, size, PROT_READ, MAP_PRIVATE, fd, 0);
        ::close(fd); // Дескриптор можна закрити одразу після створення відображення mmap

        if (addr == MAP_FAILED) {
            return std::unexpected(std::format("Збій виклику mmap: {}", std::strerror(errno)));
        }

        return MappedFile(static_cast<const uint8_t *>(addr), size);
    }

    ~MappedFile() noexcept {
        if (data_ != nullptr && size_ > 0) {
            ::munmap(const_cast<uint8_t *>(data_), size_);
        }
    }

    MappedFile(const MappedFile &) = delete;
    MappedFile &operator=(const MappedFile &) = delete;

    MappedFile(MappedFile &&other) noexcept
        : data_(std::exchange(other.data_, nullptr)),
          size_(std::exchange(other.size_, 0)) {}

    MappedFile &operator=(MappedFile &&other) noexcept {
        if (this != &other) {
            if (data_ != nullptr && size_ > 0) {
                ::munmap(const_cast<uint8_t *>(data_), size_);
            }
            data_ = std::exchange(other.data_, nullptr);
            size_ = std::exchange(other.size_, 0);
        }
        return *this;
    }

    [[nodiscard]] std::span<const uint8_t> bytes() const noexcept {
        return {data_, size_};
    }

private:
    MappedFile(const uint8_t *data, size_t size) noexcept : data_(data), size_(size) {}
    const uint8_t *data_{nullptr};
    size_t size_{0};
};

class SafeElfInspector {
public:
    explicit SafeElfInspector(std::span<const uint8_t> buffer) : buf_(buffer) {}

    void inspect() const {
        if (buf_.size() < sizeof(Elf64_Ehdr)) {
            std::cerr << "Помилка: буфер занадто малий для заголовка ELF64.\n";
            return;
        }

        const auto *hdr = reinterpret_cast<const Elf64_Ehdr *>(buf_.data());

        // Перевірка магічних байтів
        if (std::memcmp(hdr->e_ident, ELFMAG, SELFMAG) != 0) {
            std::cerr << "Помилка: сигнатура ELF не збігається.\n";
            return;
        }

        if (hdr->e_ident[EI_CLASS] != ELFCLASS64) {
            std::cerr << "Повідомлення: інспектор підтримує лише 64-бітні образи ELFCLASS64.\n";
            return;
        }

        print_header_passport(hdr);
        inspect_program_headers(hdr);
        inspect_sections(hdr);
        inspect_dynamic_dependencies(hdr);
    }

private:
    std::span<const uint8_t> buf_;

    [[nodiscard]] static std::string_view machine_name(uint16_t m) noexcept {
        switch (m) {
            case EM_X86_64:  return "AMD x86-64";
            case EM_AARCH64: return "ARM AArch64";
            case EM_ARM:     return "ARM 32-bit";
            case EM_RISCV:   return "RISC-V";
            case EM_386:     return "Intel 80386";
            default:         return "Невідома архітектура";
        }
    }

    [[nodiscard]] uint64_t vaddr_to_file_offset(const Elf64_Ehdr *hdr, uint64_t vaddr) const noexcept {
        if (hdr->e_type == ET_DYN && vaddr < buf_.size()) {
            return vaddr;
        }

        if (hdr->e_phoff + (hdr->e_phnum * sizeof(Elf64_Phdr)) > buf_.size()) {
            return 0;
        }

        const auto *ph = reinterpret_cast<const Elf64_Phdr *>(buf_.data() + hdr->e_phoff);
        for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
            if (ph[i].p_type == PT_LOAD) {
                if (vaddr >= ph[i].p_vaddr && vaddr < (ph[i].p_vaddr + ph[i].p_filesz)) {
                    return ph[i].p_offset + (vaddr - ph[i].p_vaddr);
                }
            }
        }
        return 0;
    }

    void print_header_passport(const Elf64_Ehdr *hdr) const {
        std::cout << "=== ПАСПОРТ БІНАРНИКА ===\n"
                  << std::format("Клас:              ELF64\n")
                  << std::format("Порядок байтів:    {}\n", hdr->e_ident[EI_DATA] == ELFDATA2LSB ? "Little-Endian (LSB)" : "Big-Endian (MSB)")
                  << std::format("Архітектура:       {} (0x{:04x})\n", machine_name(hdr->e_machine), hdr->e_machine)
                  << std::format("Тип файлу:         {}\n", hdr->e_type == ET_EXEC ? "ET_EXEC (Статично розміщений виконуваний файл)" :
                                                            hdr->e_type == ET_DYN ? "ET_DYN (Position-Independent Executable або Shared Object)" : "Інший")
                  << std::format("Точка входу:       0x{:016x}\n", hdr->e_entry);
    }

    void inspect_program_headers(const Elf64_Ehdr *hdr) const {
        if (hdr->e_phoff + (hdr->e_phnum * sizeof(Elf64_Phdr)) > buf_.size()) {
            std::cerr << "Помилка: Program Headers виходять за межі файлу.\n";
            return;
        }

        const auto *ph = reinterpret_cast<const Elf64_Phdr *>(buf_.data() + hdr->e_phoff);
        std::string_view interp_path;
        bool nx_enabled = true;
        bool relro_found = false;

        for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
            if (ph[i].p_type == PT_INTERP) {
                if (ph[i].p_offset + ph[i].p_filesz <= buf_.size()) {
                    interp_path = reinterpret_cast<const char *>(buf_.data() + ph[i].p_offset);
                }
            } else if (ph[i].p_type == PT_GNU_STACK) {
                if ((ph[i].p_flags & PF_X) != 0) {
                    nx_enabled = false;
                }
            } else if (ph[i].p_type == PT_GNU_RELRO) {
                relro_found = true;
            }
        }

        std::cout << "\n=== ЗАХИСНІ МЕХАНІЗМИ ТА ІНТЕРПРЕТАТОР ===\n"
                  << std::format("Тип зв'язування:   {}\n", interp_path.empty() ? "Статичне (Statically linked)" : "Динамічне (Dynamically linked)");
        if (!interp_path.empty()) {
            std::cout << std::format("Інтерпретатор:     {}\n", interp_path);
        }
        std::cout << std::format("NX (No-Execute):   {}\n", nx_enabled ? "Увімкнено (Стек без прав виконання)" : "ВИМКНЕНО (Небезпечний виконуваний стек!)")
                  << std::format("RELRO:             {}\n", relro_found ? "Присутній (PT_GNU_RELRO)" : "Відсутній");
    }

    void inspect_sections(const Elf64_Ehdr *hdr) const {
        if (hdr->e_shoff == 0 || (hdr->e_shoff + (hdr->e_shnum * sizeof(Elf64_Shdr)) > buf_.size())) {
            std::cout << "Символи:           stripped (Таблиця секцій відсутня або пошкоджена)\n";
            return;
        }

        const auto *sh = reinterpret_cast<const Elf64_Shdr *>(buf_.data() + hdr->e_shoff);
        bool has_symtab = false;

        if (hdr->e_shstrndx < hdr->e_shnum) {
            const auto *shstrtab = reinterpret_cast<const char *>(buf_.data() + sh[hdr->e_shstrndx].sh_offset);
            for (uint16_t i = 0; i < hdr->e_shnum; ++i) {
                std::string_view name(shstrtab + sh[i].sh_name);
                if (name == ".symtab") {
                    has_symtab = true;
                    break;
                }
            }
        }

        std::cout << std::format("Символи:           {}\n", has_symtab ? "not stripped (Повна таблиця .symtab наявна)" : "stripped (Налагоджувальні символи вичищено)");
    }

    void inspect_dynamic_dependencies(const Elf64_Ehdr *hdr) const {
        const auto *ph = reinterpret_cast<const Elf64_Phdr *>(buf_.data() + hdr->e_phoff);
        const Elf64_Phdr *dyn_ph = nullptr;

        for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
            if (ph[i].p_type == PT_DYNAMIC) {
                dyn_ph = &ph[i];
                break;
            }
        }

        if (!dyn_ph || dyn_ph->p_offset + dyn_ph->p_filesz > buf_.size()) {
            return;
        }

        std::cout << "\n=== ДИНАМІЧНІ ЗАЛЕЖНОСТІ (DT_NEEDED) ===\n";
        const auto *dyn = reinterpret_cast<const Elf64_Dyn *>(buf_.data() + dyn_ph->p_offset);
        size_t count = dyn_ph->p_filesz / sizeof(Elf64_Dyn);

        uint64_t strtab_vaddr = 0;
        for (size_t i = 0; i < count && dyn[i].d_tag != DT_NULL; ++i) {
            if (dyn[i].d_tag == DT_STRTAB) {
                strtab_vaddr = dyn[i].d_un.d_ptr;
                break;
            }
        }

        uint64_t strtab_offset = strtab_vaddr != 0 ? vaddr_to_file_offset(hdr, strtab_vaddr) : 0;
        if (strtab_offset == 0 || strtab_offset >= buf_.size()) {
            std::cout << "  [Увага: не вдалося розв'язати таблицю .dynstr]\n";
            return;
        }

        const auto *dynstr = reinterpret_cast<const char *>(buf_.data() + strtab_offset);
        bool found_any = false;

        for (size_t i = 0; i < count && dyn[i].d_tag != DT_NULL; ++i) {
            if (dyn[i].d_tag == DT_NEEDED) {
                uint64_t idx = dyn[i].d_un.d_val;
                if (strtab_offset + idx < buf_.size()) {
                    std::cout << std::format("  * Потрібна бібліотека: {}\n", dynstr + idx);
                    found_any = true;
                }
            } else if (dyn[i].d_tag == DT_RUNPATH) {
                uint64_t idx = dyn[i].d_un.d_val;
                if (strtab_offset + idx < buf_.size()) {
                    std::cout << std::format("  * Вшитий RUNPATH:     {}\n", dynstr + idx);
                }
            } else if (dyn[i].d_tag == DT_RPATH) {
                uint64_t idx = dyn[i].d_un.d_val;
                if (strtab_offset + idx < buf_.size()) {
                    std::cout << std::format("  * Вшитий RPATH:       {} (Застарілий)\n", dynstr + idx);
                }
            }
        }

        if (!found_any) {
            std::cout << "  (Залежностей DT_NEEDED не виявлено)\n";
        }
    }
};

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << std::format("Використання: {} <шлях-до-бінарника>\n", argv[0]);
        return EXIT_FAILURE;
    }

    auto mapped = MappedFile::open_readonly(argv[1]);
    if (!mapped) {
        std::cerr << std::format("Помилка ініціалізації: {}\n", mapped.error());
        return EXIT_FAILURE;
    }

    SafeElfInspector inspector(mapped->bytes());
    inspector.inspect();

    return EXIT_SUCCESS;
}
