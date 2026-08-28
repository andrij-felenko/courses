// mini_loader.cpp — Ідіоматичний ELF-завантажувач мовою C++20
#include <iostream>
#include <vector>
#include <memory>
#include <expected>
#include <string_view>
#include <cstring>
#include <limits>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <elf.h>

namespace mini_rtld {

// RAII обгортка для файлового дескриптора
class FileDescriptor {
    int m_fd{-1};
public:
    explicit FileDescriptor(int fd) noexcept : m_fd(fd) {}
    ~FileDescriptor() { if (m_fd >= 0) ::close(m_fd); }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept : m_fd(other.m_fd) { other.m_fd = -1; }
    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

// RAII обгортка для mmap пам'яті
struct MmapDeleter {
    size_t size{0};
    void operator()(void* ptr) const noexcept {
        if (ptr && ptr != MAP_FAILED) {
            ::munmap(ptr, size);
        }
    }
};

using UniqueMappedMemory = std::unique_ptr<void, MmapDeleter>;

enum class LoaderError {
    FileNotFound,
    HeaderReadError,
    InvalidElfMagic,
    MemoryAllocationFailed,
    SegmentReadError,
    RelocationError
};

class ElfLoader {
public:
    static std::expected<int, LoaderError> load_and_execute(std::string_view path) {
        FileDescriptor fd(::open(path.data(), O_RDONLY));
        if (!fd.valid()) {
            return std::unexpected(LoaderError::FileNotFound);
        }

        Elf64_Ehdr ehdr{};
        if (::read(fd.get(), &ehdr, sizeof(ehdr)) != sizeof(ehdr)) {
            return std::unexpected(LoaderError::HeaderReadError);
        }

        if (std::memcmp(ehdr.e_ident, ELFMAG, SELFMAG) != 0) {
            return std::unexpected(LoaderError::InvalidElfMagic);
        }

        std::vector<Elf64_Phdr> phdrs(ehdr.e_phnum);
        if (::lseek(fd.get(), ehdr.e_phoff, SEEK_SET) == -1 ||
            ::read(fd.get(), phdrs.data(), phdrs.size() * sizeof(Elf64_Phdr)) != static_cast<ssize_t>(phdrs.size() * sizeof(Elf64_Phdr))) {
            return std::unexpected(LoaderError::HeaderReadError);
        }

        uintptr_t min_vaddr = std::numeric_limits<uintptr_t>::max();
        uintptr_t max_vaddr = 0;

        for (const auto& phdr : phdrs) {
            if (phdr.p_type == PT_LOAD) {
                min_vaddr = std::min(min_vaddr, static_cast<uintptr_t>(phdr.p_vaddr));
                max_vaddr = std::max(max_vaddr, static_cast<uintptr_t>(phdr.p_vaddr + phdr.p_memsz));
            }
        }

        const size_t total_size = max_vaddr - min_vaddr;
        void* raw_mem = ::mmap(nullptr, total_size, PROT_READ | PROT_WRITE | PROT_EXEC,
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

        if (raw_mem == MAP_FAILED) {
            return std::unexpected(LoaderError::MemoryAllocationFailed);
        }

        UniqueMappedMemory memory(raw_mem, MmapDeleter{total_size});
        const uintptr_t load_base = reinterpret_cast<uintptr_t>(memory.get());
        const uintptr_t delta = load_base - min_vaddr;

        const Elf64_Dyn* dyn_section = nullptr;

        for (const auto& phdr : phdrs) {
            if (phdr.p_type == PT_LOAD) {
                void* seg_dest = reinterpret_cast<void*>(load_base + (phdr.p_vaddr - min_vaddr));
                if (::lseek(fd.get(), phdr.p_offset, SEEK_SET) == -1 ||
                    ::read(fd.get(), seg_dest, phdr.p_filesz) != static_cast<ssize_t>(phdr.p_filesz)) {
                    return std::unexpected(LoaderError::SegmentReadError);
                }
                if (phdr.p_memsz > phdr.p_filesz) {
                    std::memset(reinterpret_cast<char*>(seg_dest) + phdr.p_filesz, 0, phdr.p_memsz - phdr.p_filesz);
                }
            } else if (phdr.p_type == PT_DYNAMIC) {
                dyn_section = reinterpret_cast<const Elf64_Dyn*>(load_base + (phdr.p_vaddr - min_vaddr));
            }
        }

        /* Обробка релокацій у динамічній секцій */
        if (dyn_section) {
            const Elf64_Rela* rela_table = nullptr;
            size_t rela_size = 0;
            size_t rela_ent = sizeof(Elf64_Rela);

            for (const Elf64_Dyn* d = dyn_section; d->d_tag != DT_NULL; ++d) {
                if (d->d_tag == DT_RELA) {
                    rela_table = reinterpret_cast<const Elf64_Rela*>(delta + d->d_un.d_ptr);
                } else if (d->d_tag == DT_RELASZ) {
                    rela_size = d->d_un.d_val;
                } else if (d->d_tag == DT_RELAENT) {
                    rela_ent = d->d_un.d_val;
                }
            }

            if (rela_table && rela_size > 0) {
                const size_t count = rela_size / rela_ent;
                for (size_t i = 0; i < count; ++i) {
                    const auto& rel = rela_table[i];
                    if (ELF64_R_TYPE(rel.r_info) == R_X86_64_RELATIVE) {
                        auto* target = reinterpret_cast<uintptr_t*>(delta + rel.r_offset);
                        *target = delta + rel.r_addend;
                    }
                }
            }
        }

        const uintptr_t entry_point = delta + ehdr.e_entry;
        using EntryFunc = int (*)();
        auto entry = reinterpret_cast<EntryFunc>(entry_point);

        std::cout << "[rtld-cpp] Jumping to entry point at " << std::hex << entry_point << std::dec << "...\n";
        return entry();
    }
};

} // namespace mini_rtld

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <elf_binary>\n";
        return 1;
    }

    auto result = mini_rtld::ElfLoader::load_and_execute(argv[1]);
    if (!result) {
        std::cerr << "Loader failed with error code\n";
        return 1;
    }

    return *result;
}
