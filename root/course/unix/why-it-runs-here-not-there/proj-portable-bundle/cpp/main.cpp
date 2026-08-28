#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>
#include <sys/mman.h>

// RAII обгортка для безпечного відображення файлу через mmap
class MappedFile {
public:
    static std::expected<MappedFile, std::string> open_file(std::string_view path) {
        int fd = ::open(path.data(), O_RDONLY);
        if (fd < 0) {
            return std::unexpected("Не вдалося відкрити файл: " + std::string(path));
        }

        struct stat st{};
        if (::fstat(fd, &st) < 0) {
            ::close(fd);
            return std::unexpected("Помилка fstat для файлу: " + std::string(path));
        }

        void *ptr = ::mmap(nullptr, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
        ::close(fd);

        if (ptr == MAP_FAILED) {
            return std::unexpected("Помилка відображення пам'яті mmap");
        }

        return MappedFile(ptr, st.st_size);
    }

    ~MappedFile() {
        if (data_ != nullptr && size_ > 0) {
            ::munmap(data_, size_);
        }
    }

    MappedFile(const MappedFile &) = delete;
    MappedFile &operator=(const MappedFile &) = delete;

    MappedFile(MappedFile &&other) noexcept : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    [[nodiscard]] std::span<const uint8_t> bytes() const {
        return {static_cast<const uint8_t *>(data_), size_};
    }

private:
    MappedFile(void *data, size_t size) : data_(data), size_(size) {}
    void *data_{nullptr};
    size_t size_{0};
};

// Інспекція структури динамічної секції ELF
std::expected<void, std::string> inspect_elf(std::string_view filepath) {
    auto file_res = MappedFile::open_file(filepath);
    if (!file_res) {
        return std::unexpected(file_res.error());
    }

    auto span = file_res->bytes();
    if (span.size() < sizeof(Elf64_Ehdr)) {
        return std::unexpected("Розмір файлу замалий для заголовка ELF");
    }

    const auto *ehdr = reinterpret_cast<const Elf64_Ehdr *>(span.data());
    if (std::string_view(reinterpret_cast<const char *>(ehdr->e_ident), SELFMAG) != ELFMAG) {
        return std::unexpected("Файл не містить валідного підпису ELF");
    }

    if (ehdr->e_shoff + ehdr->e_shnum * sizeof(Elf64_Shdr) > span.size()) {
        return std::unexpected("Пошкоджена таблиця секцій ELF");
    }

    const auto *sections = reinterpret_cast<const Elf64_Shdr *>(span.data() + ehdr->e_shoff);
    const Elf64_Shdr *dyn_shdr = nullptr;

    for (int i = 0; i < ehdr->e_shnum; ++i) {
        if (sections[i].sh_type == SHT_DYNAMIC) {
            dyn_shdr = &sections[i];
            break;
        }
    }

    if (!dyn_shdr) {
        std::cout << "Бінарник є статичним або не містить секції .dynamic\n";
        return {};
    }

    const auto &str_shdr = sections[dyn_shdr->sh_link];
    const char *dynstr = reinterpret_cast<const char *>(span.data() + str_shdr.sh_offset);
    const auto *dyn_entries = reinterpret_cast<const Elf64_Dyn *>(span.data() + dyn_shdr->sh_offset);
    size_t count = dyn_shdr->sh_size / sizeof(Elf64_Dyn);

    bool has_rpath = false;
    bool has_runpath = false;

    for (size_t i = 0; i < count; ++i) {
        if (dyn_entries[i].d_tag == DT_RPATH) {
            has_rpath = true;
            std::cout << "[!] Знайдено DT_RPATH: " << (dynstr + dyn_entries[i].d_un.d_val) << "\n";
        } else if (dyn_entries[i].d_tag == DT_RUNPATH) {
            has_runpath = true;
            std::cout << "[✓] Знайдено DT_RUNPATH: " << (dynstr + dyn_entries[i].d_un.d_val) << "\n";
        }
    }

    if (!has_runpath && !has_rpath) {
        std::cout << "[-] У бінарнику відсутні записи RPATH / RUNPATH\n";
    }

    return {};
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <elf_binary>\n";
        return 1;
    }

    auto res = inspect_elf(argv[1]);
    if (!res) {
        std::cerr << "Помилка: " << res.error() << "\n";
        return 1;
    }
    return 0;
}
