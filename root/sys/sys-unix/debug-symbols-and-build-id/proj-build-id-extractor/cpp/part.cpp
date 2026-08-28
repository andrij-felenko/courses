#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <format>
#include <span>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <elf.h>

#ifndef NT_GNU_BUILD_ID
#define NT_GNU_BUILD_ID 3
#endif

// RAII-обгортка над покажчиком mmap для безпечного звільнення ресурсу
class MemoryMappedFile {
public:
    static std::expected<MemoryMappedFile, std::string> open(std::string_view path) {
        int fd = ::open(path.data(), O_RDONLY);
        if (fd < 0) {
            return std::unexpected(std::format("Не вдалося відкрити файл: {}", std::strerror(errno)));
        }

        struct stat st{};
        if (::fstat(fd, &st) < 0 || st.st_size < static_cast<off_t>(sizeof(Elf64_Ehdr))) {
            ::close(fd);
            return std::unexpected("Файл замалий або пошкоджений");
        }

        void *addr = ::mmap(nullptr, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
        ::close(fd);

        if (addr == MAP_FAILED) {
            return std::unexpected(std::format("Помилка mmap: {}", std::strerror(errno)));
        }

        return MemoryMappedFile(static_cast<const uint8_t *>(addr), static_cast<size_t>(st.st_size));
    }

    ~MemoryMappedFile() {
        if (data_ != nullptr) {
            ::munmap(const_cast<uint8_t *>(data_), size_);
        }
    }

    MemoryMappedFile(const MemoryMappedFile &) = delete;
    MemoryMappedFile &operator=(const MemoryMappedFile &) = delete;

    MemoryMappedFile(MemoryMappedFile &&other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    MemoryMappedFile &operator=(MemoryMappedFile &&other) noexcept {
        if (this != &other) {
            if (data_) ::munmap(const_cast<uint8_t *>(data_), size_);
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::span<const uint8_t> bytes() const noexcept {
        return {data_, size_};
    }

private:
    MemoryMappedFile(const uint8_t *data, size_t size) : data_(data), size_(size) {}
    const uint8_t *data_{nullptr};
    size_t size_{0};
};

struct DebugMetadata {
    std::optional<std::string> build_id;
    std::optional<std::string> debuglink_name;
    std::optional<uint32_t> debuglink_crc;
};

// Парсер структури ELF64
class ElfInspector {
public:
    static std::expected<DebugMetadata, std::string> inspect(std::span<const uint8_t> buffer) {
        if (buffer.size() < sizeof(Elf64_Ehdr)) {
            return std::unexpected("Розмір буфера менший за розмір Elf64_Ehdr");
        }

        const auto *ehdr = reinterpret_cast<const Elf64_Ehdr *>(buffer.data());
        if (std::memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
            return std::unexpected("Сигнатура файлу не відповідає стандарту ELF");
        }

        if (ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
            return std::unexpected("Підтримуються лише 64-бітні бінарники (ELFCLASS64)");
        }

        if (ehdr->e_shoff == 0 || ehdr->e_shoff + ehdr->e_shnum * sizeof(Elf64_Shdr) > buffer.size()) {
            return std::unexpected("Таблиця секцій SHT виходить за межі файлу");
        }

        const auto *shdrs = reinterpret_cast<const Elf64_Shdr *>(buffer.data() + ehdr->e_shoff);
        const auto &shstrtab_hdr = shdrs[ehdr->e_shstrndx];
        const char *shstrtab = reinterpret_cast<const char *>(buffer.data() + shstrtab_hdr.sh_offset);

        DebugMetadata meta;

        for (size_t i = 0; i < ehdr->e_shnum; ++i) {
            std::string_view sec_name = shstrtab + shdrs[i].sh_name;

            if (shdrs[i].sh_type == SHT_NOTE && sec_name == ".note.gnu.build-id") {
                auto note_span = buffer.subspan(shdrs[i].sh_offset, shdrs[i].sh_size);
                meta.build_id = parse_build_id_note(note_span);
            } else if (sec_name == ".gnu_debuglink" && shdrs[i].sh_size >= 5) {
                auto sec_span = buffer.subspan(shdrs[i].sh_offset, shdrs[i].sh_size);
                const char *raw_str = reinterpret_cast<const char *>(sec_span.data());
                size_t name_len = ::strnlen(raw_str, sec_span.size() - 4);
                meta.debuglink_name = std::string(raw_str, name_len);

                uint32_t crc = 0;
                std::memcpy(&crc, sec_span.data() + sec_span.size() - 4, sizeof(uint32_t));
                meta.debuglink_crc = crc;
            }
        }

        return meta;
    }

private:
    static size_t align_up(size_t val, size_t alignment) noexcept {
        return (val + alignment - 1) & ~(alignment - 1);
    }

    static std::optional<std::string> parse_build_id_note(std::span<const uint8_t> note_span) {
        size_t offset = 0;
        while (offset + sizeof(Elf64_Nhdr) <= note_span.size()) {
            const auto *nhdr = reinterpret_cast<const Elf64_Nhdr *>(note_span.data() + offset);
            offset += sizeof(Elf64_Nhdr);

            std::string_view name(reinterpret_cast<const char *>(note_span.data() + offset), nhdr->n_namesz);
            offset = align_up(offset + nhdr->n_namesz, 4);

            const uint8_t *desc = note_span.data() + offset;
            offset = align_up(offset + nhdr->n_descsz, 4);

            if (offset > note_span.size()) {
                break;
            }

            if (nhdr->n_type == NT_GNU_BUILD_ID && nhdr->n_namesz == 4 && name.starts_with("GNU")) {
                std::string hex_str;
                hex_str.reserve(nhdr->n_descsz * 2);
                for (size_t j = 0; j < nhdr->n_descsz; ++j) {
                    hex_str += std::format("{:02x}", desc[j]);
                }
                return hex_str;
            }
        }
        return std::nullopt;
    }
};

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << std::format("Використання: {} <шлях-до-elf-бінарника>\n", argv[0]);
        return EXIT_FAILURE;
    }

    auto mapped_res = MemoryMappedFile::open(argv[1]);
    if (!mapped_res) {
        std::cerr << std::format("Помилка: {}\n", mapped_res.error());
        return EXIT_FAILURE;
    }

    auto meta_res = ElfInspector::inspect(mapped_res->bytes());
    if (!meta_res) {
        std::cerr << std::format("Помилка аналізу ELF: {}\n", meta_res.error());
        return EXIT_FAILURE;
    }

    const auto &meta = *meta_res;
    std::cout << std::format("Аналіз бінарника: {}\n", argv[1]);

    if (meta.build_id) {
        std::cout << std::format("  [✓] Build ID:       {}\n", *meta.build_id);
        std::cout << std::format("      Канонічний шлях: /usr/lib/debug/.build-id/{}/{}.debug\n",
                                 meta.build_id->substr(0, 2), meta.build_id->substr(2));
    } else {
        std::cout << "  [✗] Build ID:       відсутній\n";
    }

    if (meta.debuglink_name && meta.debuglink_crc) {
        std::cout << std::format("  [✓] gnu_debuglink:  {} (CRC32: 0x{:08x})\n",
                                 *meta.debuglink_name, *meta.debuglink_crc);
    } else {
        std::cout << "  [✗] gnu_debuglink:  відсутній\n";
    }

    return EXIT_SUCCESS;
}
