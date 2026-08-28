#include <iostream>
#include <fstream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <optional>
#include <iomanip>
#include <cstdint>
#include <cstring>

namespace elf {

inline constexpr std::size_t IdentSize = 16;

enum class FileType : std::uint16_t {
    None = 0,
    Relocatable = 1,
    Executable = 2,
    SharedObject = 3
};

enum class MachineArchitecture : std::uint16_t {
    Arm = 40,
    RiscV = 243
};

enum class SegmentType : std::uint32_t {
    Null = 0,
    Load = 1,
    Dynamic = 2,
    Interp = 3,
    Note = 4
};

enum class SectionType : std::uint32_t {
    Null = 0,
    ProgBits = 1,
    SymTab = 2,
    StrTab = 3,
    Rela = 4,
    NoBits = 8,
    Rel = 9
};

namespace flags {
    inline constexpr std::uint32_t Execute = 0x1;
    inline constexpr std::uint32_t Write   = 0x2;
    inline constexpr std::uint32_t Read    = 0x4;
}

#pragma pack(push, 1)
struct Header32 {
    std::array<std::uint8_t, IdentSize> ident;
    FileType type;
    MachineArchitecture machine;
    std::uint32_t version;
    std::uint32_t entry_address;
    std::uint32_t ph_offset;
    std::uint32_t sh_offset;
    std::uint32_t flags;
    std::uint16_t header_size;
    std::uint16_t ph_entry_size;
    std::uint16_t ph_count;
    std::uint16_t sh_entry_size;
    std::uint16_t sh_count;
    std::uint16_t sh_str_index;

    [[nodiscard]] constexpr bool is_valid(std::size_t file_size) const noexcept {
        if (file_size < sizeof(Header32)) return false;
        if (ident[0] != 0x7F || ident[1] != 'E' || ident[2] != 'L' || ident[3] != 'F') {
            return false;
        }
        return ident[4] == 1 && version == 1;
    }
};

struct ProgramHeader32 {
    SegmentType type;
    std::uint32_t offset;
    std::uint32_t vaddr;
    std::uint32_t paddr;
    std::uint32_t file_size;
    std::uint32_t memory_size;
    std::uint32_t flags;
    std::uint32_t align;
};

struct SectionHeader32 {
    std::uint32_t name_offset;
    SectionType type;
    std::uint32_t flags;
    std::uint32_t address;
    std::uint32_t offset;
    std::uint32_t size;
    std::uint32_t link;
    std::uint32_t info;
    std::uint32_t address_align;
    std::uint32_t entry_size;
};
#pragma pack(pop)

struct FirmwareSummary {
    std::uint32_t flash_usage{0};
    std::uint32_t sram_data_usage{0};
    std::uint32_t sram_bss_usage{0};
    std::uint32_t entry_point{0};
    MachineArchitecture architecture{MachineArchitecture::Arm};
    bool is_thumb_mode{false};
};

class ElfParser {
public:
    explicit ElfParser(std::span<const std::uint8_t> buffer) noexcept : buffer_(buffer) {}

    [[nodiscard]] std::optional<FirmwareSummary> parse() const {
        if (buffer_.size() < sizeof(Header32)) {
            std::cerr << "Помилка: Розмір буфера менший за заголовок ELF!\n";
            return std::nullopt;
        }

        const auto* header = reinterpret_cast<const Header32*>(buffer_.data());
        if (!header->is_valid(buffer_.size())) {
            std::cerr << "Помилка: Двійковий файл не є валідним ELF32!\n";
            return std::nullopt;
        }

        FirmwareSummary summary{};
        summary.entry_point = header->entry_address;
        summary.architecture = header->machine;
        summary.is_thumb_mode = (header->machine == MachineArchitecture::Arm) &&
                                (header->entry_address & 1U);

        std::cout << "========================================================\n"
                  << "ELF32 Образ розпізнано успішно:\n"
                  << "  Точка входу: 0x" << std::hex << std::uppercase << std::setw(8) << std::setfill('0')
                  << header->entry_address << (summary.is_thumb_mode ? " [Thumb]" : "") << std::dec << "\n"
                  << "  Кількість сегментів: " << header->ph_count << "\n"
                  << "  Кількість секцій:    " << header->sh_count << "\n"
                  << "========================================================\n\n";

        // Обробка сегментів
        std::cout << "--- Таблиця завантажуваних сегментів ---\n";
        for (std::size_t i = 0; i < header->ph_count; ++i) {
            const auto ph_off = header->ph_offset + (i * header->ph_entry_size);
            if (ph_off + sizeof(ProgramHeader32) > buffer_.size()) break;

            const auto* phdr = reinterpret_cast<const ProgramHeader32*>(buffer_.data() + ph_off);
            if (phdr->type == SegmentType::Load) {
                std::cout << "  Сегмент #" << i << " [PT_LOAD]:\n"
                          << "    LMA Flash: 0x" << std::hex << std::setw(8) << std::setfill('0') << phdr->paddr << "\n"
                          << "    VMA RAM:   0x" << std::setw(8) << std::setfill('0') << phdr->vaddr << std::dec << "\n"
                          << "    Розмір у файлі: " << phdr->file_size << " B, Розмір у пам'яті: " << phdr->memory_size << " B\n";

                if (phdr->flags & flags::Execute) {
                    summary.flash_usage += phdr->file_size;
                } else if (phdr->flags & flags::Write) {
                    summary.sram_data_usage += phdr->file_size;
                    if (phdr->memory_size > phdr->file_size) {
                        summary.sram_bss_usage += (phdr->memory_size - phdr->file_size);
                    }
                }
            }
        }
        std::cout << "\n";

        // Обробка секцій та таблиці рядків
        if (header->sh_count > 0 && header->sh_str_index < header->sh_count) {
            const auto strtab_desc_off = header->sh_offset + (header->sh_str_index * header->sh_entry_size);
            if (strtab_desc_off + sizeof(SectionHeader32) <= buffer_.size()) {
                const auto* strtab_hdr = reinterpret_cast<const SectionHeader32*>(buffer_.data() + strtab_desc_off);
                const char* strtab_ptr = reinterpret_cast<const char*>(buffer_.data() + strtab_hdr->offset);

                std::cout << "--- Секції програми ---\n";
                for (std::size_t i = 0; i < header->sh_count; ++i) {
                    const auto sh_off = header->sh_offset + (i * header->sh_entry_size);
                    if (sh_off + sizeof(SectionHeader32) > buffer_.size()) break;

                    const auto* shdr = reinterpret_cast<const SectionHeader32*>(buffer_.data() + sh_off);
                    std::string_view sec_name = (shdr->name_offset < strtab_hdr->size) ?
                                                (strtab_ptr + shdr->name_offset) : "<invalid>";

                    std::cout << "  [" << std::setw(2) << std::setfill('0') << i << "] "
                              << std::left << std::setw(20) << std::setfill(' ') << sec_name
                              << " VMA: 0x" << std::hex << std::setw(8) << std::setfill('0') << shdr->address
                              << " Розмір: " << std::dec << std::setw(6) << std::setfill(' ') << shdr->size << " B\n";
                }
                std::cout << "\n";
            }
        }

        return summary;
    }

    bool export_binary(std::string_view filename) const {
        std::ofstream out(std::string(filename), std::ios::binary);
        if (!out) return false;

        const auto* header = reinterpret_cast<const Header32*>(buffer_.data());
        for (std::size_t i = 0; i < header->ph_count; ++i) {
            const auto ph_off = header->ph_offset + (i * header->ph_entry_size);
            if (ph_off + sizeof(ProgramHeader32) > buffer_.size()) break;

            const auto* phdr = reinterpret_cast<const ProgramHeader32*>(buffer_.data() + ph_off);
            if (phdr->type == SegmentType::Load && phdr->file_size > 0) {
                if (phdr->offset + phdr->file_size <= buffer_.size()) {
                    out.write(reinterpret_cast<const char*>(buffer_.data() + phdr->offset), phdr->file_size);
                }
            }
        }
        std::cout << "Експорт плоского .bin файлу завершено: " << filename << "\n";
        return true;
    }

    bool export_hex(std::string_view filename) const {
        std::ofstream out(std::string(filename));
        if (!out) return false;

        const auto* header = reinterpret_cast<const Header32*>(buffer_.data());
        std::uint32_t current_upper = 0xFFFFFFFF;

        for (std::size_t i = 0; i < header->ph_count; ++i) {
            const auto ph_off = header->ph_offset + (i * header->ph_entry_size);
            if (ph_off + sizeof(ProgramHeader32) > buffer_.size()) break;

            const auto* phdr = reinterpret_cast<const ProgramHeader32*>(buffer_.data() + ph_off);
            if (phdr->type == SegmentType::Load && phdr->file_size > 0) {
                std::uint32_t target_addr = phdr->paddr;
                const auto* data_ptr = buffer_.data() + phdr->offset;
                std::size_t remaining = phdr->file_size;

                while (remaining > 0) {
                    const std::uint32_t upper_addr = (target_addr >> 16) & 0xFFFF;
                    if (upper_addr != current_upper) {
                        current_upper = upper_addr;
                        const auto hi = static_cast<std::uint8_t>((upper_addr >> 8) & 0xFF);
                        const auto lo = static_cast<std::uint8_t>(upper_addr & 0xFF);
                        auto cksum = static_cast<std::uint8_t>(2 + 4 + hi + lo);
                        cksum = static_cast<std::uint8_t>(0x100 - (cksum & 0xFF));

                        out << ":02000004"
                            << std::hex << std::uppercase << std::setw(2) << std::setfill('0') << static_cast<int>(hi)
                            << std::setw(2) << std::setfill('0') << static_cast<int>(lo)
                            << std::setw(2) << std::setfill('0') << static_cast<int>(cksum) << "\n";
                    }

                    const auto chunk_len = static_cast<std::uint8_t>(std::min<std::size_t>(remaining, 16));
                    const auto lower_addr = static_cast<std::uint16_t>(target_addr & 0xFFFF);
                    std::uint8_t cksum = chunk_len + (lower_addr >> 8) + (lower_addr & 0xFF) + 0x00;

                    out << ":" << std::hex << std::uppercase
                        << std::setw(2) << std::setfill('0') << static_cast<int>(chunk_len)
                        << std::setw(4) << std::setfill('0') << lower_addr << "00";

                    for (std::size_t b = 0; b < chunk_len; ++b) {
                        const auto val = data_ptr[b];
                        cksum += val;
                        out << std::setw(2) << std::setfill('0') << static_cast<int>(val);
                    }

                    cksum = static_cast<std::uint8_t>(0x100 - (cksum & 0xFF));
                    out << std::setw(2) << std::setfill('0') << static_cast<int>(cksum) << "\n";

                    target_addr += chunk_len;
                    data_ptr += chunk_len;
                    remaining -= chunk_len;
                }
            }
        }

        out << ":00000001FF\n";
        std::cout << "Генерацію Intel HEX файлу завершено: " << filename << "\n";
        return true;
    }

private:
    std::span<const std::uint8_t> buffer_;
};

} // namespace elf

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Використання: " << argv[0] << " <firmware.elf> [output.bin] [output.hex]\n";
        return 1;
    }

    std::ifstream file(argv[1], std::ios::binary | std::ios::ate);
    if (!file) {
        std::cerr << "Помилка: Не вдалося відкрити вхідний файл " << argv[1] << "\n";
        return 1;
    }

    const auto file_size = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<std::uint8_t> buffer(static_cast<std::size_t>(file_size));
    if (!file.read(reinterpret_cast<char*>(buffer.data()), file_size)) {
        std::cerr << "Помилка читання файлу!\n";
        return 1;
    }

    elf::ElfParser parser(buffer);
    const auto summary = parser.parse();
    if (summary) {
        std::cout << "--- Підсумок використання пам'яті (C++20) ---\n"
                  << "  Flash Memory (Код + LMA .data): " << summary->flash_usage << " байтів\n"
                  << "  SRAM Data    (.data у RAM):     " << summary->sram_data_usage << " байтів\n"
                  << "  SRAM BSS     (.bss у RAM):      " << summary->sram_bss_usage << " байтів\n"
                  << "  Всього зайнято оперативної RAM: "
                  << (summary->sram_data_usage + summary->sram_bss_usage) << " байтів\n"
                  << "========================================================\n";

        if (argc >= 3) {
            parser.export_binary(argv[2]);
        }
        if (argc >= 4) {
            parser.export_hex(argv[3]);
        }
    }

    return 0;
}
