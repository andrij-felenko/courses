#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <unordered_map>
#include <expected>
#include <filesystem>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>
#include <sys/mman.h>

namespace notary {

enum class LicenseClass {
    Permissive,
    WeakCopyleft,
    StrongCopyleft,
    Unknown
};

struct LibraryRule {
    std::string_view license;
    LicenseClass classification;
};

class ScopedMmap {
public:
    ScopedMmap(int fd, size_t size) : size_(size) {
        addr_ = ::mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd, 0);
    }
    ~ScopedMmap() {
        if (addr_ != MAP_FAILED) {
            ::munmap(addr_, size_);
        }
    }
    [[nodiscard]] bool isValid() const noexcept { return addr_ != MAP_FAILED; }
    [[nodiscard]] const uint8_t* data() const noexcept { return static_cast<const uint8_t*>(addr_); }
    [[nodiscard]] size_t size() const noexcept { return size_; }

private:
    void *addr_{MAP_FAILED};
    size_t size_{0};
};

class FirmwareLicenseAuditor {
public:
    FirmwareLicenseAuditor() {
        policy_db_ = {
            {"libc.so.6", {"LGPL-2.1-or-later", LicenseClass::WeakCopyleft}},
            {"libm.so.6", {"LGPL-2.1-or-later", LicenseClass::WeakCopyleft}},
            {"libcrypto.so.3", {"Apache-2.0", LicenseClass::Permissive}},
            {"libssl.so.3", {"Apache-2.0", LicenseClass::Permissive}},
            {"libz.so.1", {"Zlib", LicenseClass::Permissive}},
            {"libsqlite3.so.0", {"Public-Domain", LicenseClass::Permissive}},
            {"libgpl_engine.so.1", {"GPL-3.0-only", LicenseClass::StrongCopyleft}}
        };
    }

    struct AuditReport {
        std::vector<std::string> needed_libs;
        std::vector<std::string> critical_violations;
        bool is_static_binary{false};
    };

    std::expected<AuditReport, std::string> auditBinary(const std::filesystem::path& binary_path) const {
        int fd = ::open(binary_path.c_str(), O_RDONLY);
        if (fd < 0) {
            return std::unexpected("Не вдалося відкрити цільовий двійковий файл");
        }
        auto close_fd = [](int *f) { if (f && *f >= 0) { ::close(*f); delete f; } };
        std::unique_ptr<int, decltype(close_fd)> fd_ptr(new int(fd), close_fd);

        struct stat st{};
        if (::fstat(fd, &st) < 0) {
            return std::unexpected("Помилка читання атрибутів файлу через fstat");
        }

        ScopedMmap mapped_file(fd, st.st_size);
        if (!mapped_file.isValid()) {
            return std::unexpected("Помилка відображення пам'яті через mmap");
        }

        auto bytes = std::span<const uint8_t>(mapped_file.data(), mapped_file.size());
        if (bytes.size() < sizeof(Elf64_Ehdr)) {
            return std::unexpected("Розмір файлу замалий для коректного заголовка ELF");
        }

        const auto *ehdr = reinterpret_cast<const Elf64_Ehdr*>(bytes.data());
        if (std::memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0 || ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
            return std::unexpected("Файл не є валідним 64-бітним образом ELF");
        }

        AuditReport report;
        const auto *phdrs = reinterpret_cast<const Elf64_Phdr*>(bytes.data() + ehdr->e_phoff);
        const Elf64_Dyn *dyn_section = nullptr;
        size_t dyn_bytes = 0;

        for (int i = 0; i < ehdr->e_phnum; ++i) {
            if (phdrs[i].p_type == PT_DYNAMIC) {
                dyn_section = reinterpret_cast<const Elf64_Dyn*>(bytes.data() + phdrs[i].p_offset);
                dyn_bytes = phdrs[i].p_filesz;
                break;
            }
        }

        if (!dyn_section) {
            report.is_static_binary = true;
            return report;
        }

        const char *dynstr_table = nullptr;
        const auto *shdrs = reinterpret_cast<const Elf64_Shdr*>(bytes.data() + ehdr->e_shoff);
        for (int i = 0; i < ehdr->e_shnum; ++i) {
            if (shdrs[i].sh_type == SHT_STRTAB && i != ehdr->e_shstrndx) {
                dynstr_table = reinterpret_cast<const char*>(bytes.data() + shdrs[i].sh_offset);
                break;
            }
        }

        if (!dynstr_table) {
            return std::unexpected("Таблицю рядків .dynstr не знайдено");
        }

        size_t dyn_count = dyn_bytes / sizeof(Elf64_Dyn);
        for (size_t i = 0; i < dyn_count; ++i) {
            if (dyn_section[i].d_tag == DT_NEEDED) {
                std::string_view lib_name(dynstr_table + dyn_section[i].d_un.d_val);
                report.needed_libs.emplace_back(lib_name);

                auto it = policy_db_.find(lib_name);
                if (it != policy_db_.end()) {
                    if (it->second.classification == LicenseClass::StrongCopyleft) {
                        report.critical_violations.push_back(std::string(lib_name) + " (" + std::string(it->second.license) + ")");
                    }
                }
            }
        }

        return report;
    }

private:
    std::unordered_map<std::string_view, LibraryRule> policy_db_;
};

} // namespace notary
