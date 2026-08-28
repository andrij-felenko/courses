// uki_parser.cpp — Ідіоматичний парсер PE/COFF секцій UKI мовою C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <span >
#include <memory>
#include <optional>
#include <cstdint>
#include <cstring>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

namespace uki {

constexpr uint16_t DOS_MAGIC = 0x5A4D;
constexpr uint32_t NT_MAGIC  = 0x00004550;

#pragma pack(push, 1)
struct DosHeader {
    uint16_t e_magic;
    uint8_t  e_res[58];
    uint32_t e_lfanew;
};

struct FileHeader {
    uint16_t Machine;
    uint16_t NumberOfSections;
    uint32_t TimeDateStamp;
    uint32_t PointerToSymbolTable;
    uint32_t NumberOfSymbols;
    uint16_t SizeOfOptionalHeader;
    uint16_t Characteristics;
};

struct NtHeaders64 {
    uint32_t Signature;
    FileHeader FileHeader;
};

struct SectionHeader {
    uint8_t  Name[8];
    uint32_t VirtualSize;
    uint32_t VirtualAddress;
    uint32_t SizeOfRawData;
    uint32_t PointerToRawData;
    uint32_t PointerToRelocations;
    uint32_t PointerToLinenumbers;
    uint16_t NumberOfRelocations;
    uint16_t NumberOfLinenumbers;
    uint32_t Characteristics;
};
#pragma pack(pop)

// RAII обгортка для безпечного керування пам'яттю mmap
class MappedFile {
public:
    explicit MappedFile(const std::string& path) {
        int fd = ::open(path.c_str(), O_RDONLY);
        if (fd < 0) return;

        struct stat st{};
        if (::fstat(fd, &st) == 0 && st.st_size > 0) {
            size_ = static_cast<size_t>(st.st_size);
            void* addr = ::mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd, 0);
            if (addr != MAP_FAILED) {
                data_ = static_cast<const std::byte*>(addr);
            }
        }
        ::close(fd);
    }

    ~MappedFile() {
        if (data_ && size_ > 0) {
            ::munmap(const_cast<void*>(static_cast<const void*>(data_)), size_);
        }
    }

    MappedFile(const MappedFile&) = delete;
    MappedFile& operator=(const MappedFile&) = delete;

    [[nodiscard]] std::span<const std::byte> bytes() const noexcept {
        return {data_, size_};
    }

    [[nodiscard]] bool valid() const noexcept { return data_ != nullptr; }

private:
    const std::byte* data_{nullptr};
    size_t size_{0};
};

class UkiInspector {
public:
    explicit UkiInspector(std::span<const std::byte> buffer) : buffer_(buffer) {}

    void print_report() const {
        if (buffer_.size() < sizeof(DosHeader)) {
            std::cerr << "Буфер занадто малий для DOS заголовка\n";
            return;
        }

        const auto* dos = reinterpret_cast<const DosHeader*>(buffer_.data());
        if (dos->e_magic != DOS_MAGIC) {
            std::cerr << "Файл не містить сигнатури MZ\n";
            return;
        }

        if (dos->e_lfanew + sizeof(NtHeaders64) > buffer_.size()) {
            std::cerr << "Некоректний зсув PE заголовка\n";
            return;
        }

        const auto* nt = reinterpret_cast<const NtHeaders64*>(buffer_.data() + dos->e_lfanew);
        if (nt->Signature != NT_MAGIC) {
            std::cerr << "Файл не містить сигнатури PE\\0\\0\n";
            return;
        }

        const uint16_t count = nt->FileHeader.NumberOfSections;
        size_t sec_offset = dos->e_lfanew + sizeof(uint32_t) + sizeof(FileHeader) + 
                            nt->FileHeader.SizeOfOptionalHeader;

        std::cout << "Знайдено PE-секцій: " << count << "\n";
        std::cout << "-----------------------------------------------------\n";

        for (uint16_t i = 0; i < count; ++i) {
            if (sec_offset + sizeof(SectionHeader) > buffer_.size()) break;
            const auto* sec = reinterpret_cast<const SectionHeader*>(buffer_.data() + sec_offset);

            char name_buf[9] = {0};
            std::memcpy(name_buf, sec->Name, 8);
            std::string_view name(name_buf);

            std::cout << "[" << (i + 1) << "] Секція: " << name 
                      << " | Зміщення: 0x" << std::hex << sec->PointerToRawData 
                      << std::dec << " | Розмір: " << sec->SizeOfRawData << " B\n";

            if (name == ".cmdline" || name == ".osrel") {
                if (sec->PointerToRawData + sec->SizeOfRawData <= buffer_.size()) {
                    std::string_view text_val(
                        reinterpret_cast<const char*>(buffer_.data() + sec->PointerToRawData),
                        sec->SizeOfRawData
                    );
                    std::cout << "     Вміст (" << name << "):\n     \"" << text_val << "\"\n";
                }
            }

            sec_offset += sizeof(SectionHeader);
        }
    }

private:
    std::span<const std::byte> buffer_;
};

} // namespace uki

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Використання: " << argv[0] << " <path-to-uki.efi>\n";
        return 1;
    }

    uki::MappedFile file(argv[1]);
    if (!file.valid()) {
        std::cerr << "Не вдалося відкрити або відобразити файл\n";
        return 1;
    }

    uki::UkiInspector inspector(file.bytes());
    inspector.print_report();

    return 0;
}
