#include <iostream>
#include <string_view>
#include <span>
#include <expected>
#include <chrono>
#include <cstring>
#include <sys/auxv.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <elf.h>

class VdsoParser {
public:
    using ClockGetTimeFn = int (*)(clockid_t, struct timespec*);

    // Фабричний метод створення парсера з валідацією auxv
    static std::expected<VdsoParser, std::string_view> create() noexcept {
        uintptr_t base = getauxval(AT_SYSINFO_EHDR);
        if (!base) {
            return std::unexpected("vDSO address missing in Auxiliary Vector");
        }
        return VdsoParser(base);
    }

    // Безпечний пошук символу vDSO без винятків
    [[nodiscard]] std::expected<ClockGetTimeFn, std::string_view> findSymbol(std::string_view sym_name) const noexcept {
        const auto* ehdr = reinterpret_cast<const Elf64_Ehdr*>(m_base);
        
        if (std::memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
            return std::unexpected("Invalid ELF header magic in vDSO");
        }

        const auto* phdr = reinterpret_cast<const Elf64_Phdr*>(m_base + ehdr->e_phoff);
        const Elf64_Dyn* dyn = nullptr;

        for (size_t i = 0; i < ehdr->e_phnum; ++i) {
            if (phdr[i].p_type == PT_DYNAMIC) {
                dyn = reinterpret_cast<const Elf64_Dyn*>(m_base + phdr[i].p_offset);
                break;
            }
        }

        if (!dyn) return std::unexpected("PT_DYNAMIC segment not found");

        const Elf64_Sym* symtab = nullptr;
        const char* strtab = nullptr;

        for (const auto* d = dyn; d->d_tag != DT_NULL; ++d) {
            if (d->d_tag == DT_SYMTAB) {
                symtab = reinterpret_cast<const Elf64_Sym*>(m_base + d->d_un.d_ptr);
            } else if (d->d_tag == DT_STRTAB) {
                strtab = reinterpret_cast<const char*>(m_base + d->d_un.d_ptr);
            }
        }

        if (!symtab || !strtab) return std::unexpected("Dynamic symbol table or string table missing");

        for (size_t i = 0; symtab[i].st_name != 0 || i == 0; ++i) {
            if (i > 0 && symtab[i].st_name != 0) {
                std::string_view name{strtab + symtab[i].st_name};
                if (name == sym_name) {
                    auto fn_addr = m_base + symtab[i].st_value;
                    return reinterpret_cast<ClockGetTimeFn>(fn_addr);
                }
            }
        }

        return std::unexpected("Requested symbol not found in vDSO");
    }

    [[nodiscard]] uintptr_t baseAddress() const noexcept { return m_base; }

private:
    explicit VdsoParser(uintptr_t base) noexcept : m_base(base) {}
    uintptr_t m_base;
};

int main() {
    auto parser_res = VdsoParser::create();
    if (!parser_res) {
        std::cerr << "Error: " << parser_res.error() << '\n';
        return 1;
    }

    const auto& parser = *parser_res;
    std::cout << "[+] vDSO base address: 0x" << std::hex << parser.baseAddress() << std::dec << '\n';

    constexpr std::string_view target_symbol = "__vdso_clock_gettime";
    auto fn_res = parser.findSymbol(target_symbol);

    if (!fn_res) {
        std::cerr << "Error finding symbol: " << fn_res.error() << '\n';
        return 1;
    }

    auto vdso_clock_gettime = *fn_res;
    std::cout << "[+] Found " << target_symbol << " at: " << reinterpret_cast<void*>(vdso_clock_gettime) << '\n';

    constexpr int iterations = 5000000;
    struct timespec ts{};

    // Бенчмарк vDSO викликів
    auto t0 = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iterations; ++i) {
        vdso_clock_gettime(CLOCK_REALTIME, &ts);
    }
    auto t1 = std::chrono::high_resolution_clock::now();

    // Бенчмарк прямого системного виклику syscall
    auto t2 = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iterations; ++i) {
        syscall(SYS_clock_gettime, CLOCK_REALTIME, &ts);
    }
    auto t3 = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double, std::milli> vdso_ms = t1 - t0;
    std::chrono::duration<double, std::milli> syscall_ms = t3 - t2;

    std::cout << "\n=== Performance Results (" << iterations << " calls) ===\n";
    std::cout << "vDSO time:     " << vdso_ms.count() << " ms (" << (vdso_ms.count() * 1e6 / iterations) << " ns/call)\n";
    std::cout << "Syscall time:  " << syscall_ms.count() << " ms (" << (syscall_ms.count() * 1e6 / iterations) << " ns/call)\n";
    std::cout << "Speedup ratio: " << (syscall_ms.count() / vdso_ms.count()) << "x faster\n";

    return 0;
}
