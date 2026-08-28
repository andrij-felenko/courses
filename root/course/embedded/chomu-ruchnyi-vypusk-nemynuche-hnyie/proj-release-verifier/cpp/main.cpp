#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <string>
#include <span>
#include <cstdint>
#include <expected>
#include <algorithm>

constexpr uint8_t ELF_MAGIC0 = 0x7F;
constexpr uint8_t ELF_MAGIC1 = 'E';
constexpr uint8_t ELF_MAGIC2 = 'L';
constexpr uint8_t ELF_MAGIC3 = 'F';

constexpr uint32_t FLASH_LIMIT_BYTES = 512 * 1024;
constexpr uint32_t RAM_LIMIT_BYTES   = 128 * 1024;

#pragma pack(push, 1)
struct Elf32_Header {
    uint8_t  e_ident[16];
    uint16_t e_type;
    uint16_t e_machine;
    uint32_t e_version;
    uint32_t e_entry;
    uint32_t e_phoff;
    uint32_t e_shoff;
    uint32_t e_flags;
    uint16_t e_ehsize;
    uint16_t e_phentsize;
    uint16_t e_phnum;
    uint16_t e_shentsize;
    uint16_t e_shnum;
    uint16_t e_shstrndx;
};

struct Elf32_SectionHeader {
    uint32_t sh_name;
    uint32_t sh_type;
    uint32_t sh_flags;
    uint32_t sh_addr;
    uint32_t sh_offset;
    uint32_t sh_size;
    uint32_t sh_link;
    uint32_t sh_info;
    uint32_t sh_addralign;
    uint32_t sh_entsize;
};
#pragma pack(pop)

struct ArtifactStats {
    uint32_t flash_used{0};
    uint32_t ram_used{0};
    uint32_t crc32{0};
    bool is_dirty{false};
};

[[nodiscard]] constexpr uint32_t compute_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

[[nodiscard]] std::expected<ArtifactStats, std::string> inspect_elf(std::span<const uint8_t> file_bytes) {
    if (file_bytes.size() < sizeof(Elf32_Header)) {
        return std::unexpected("Файл занадто малий для заголовка ELF");
    }

    const auto& header = *reinterpret_cast<const Elf32_Header*>(file_bytes.data());
    if (header.e_ident[0] != ELF_MAGIC0 || header.e_ident[1] != ELF_MAGIC1 ||
        header.e_ident[2] != ELF_MAGIC2 || header.e_ident[3] != ELF_MAGIC3) {
        return std::unexpected("Некоректний ELF-магічний підпис");
    }

    if (header.e_shoff + header.e_shnum * sizeof(Elf32_SectionHeader) > file_bytes.size()) {
        return std::unexpected("Таблиця секцій виходить за межі файлу");
    }

    const auto* sh_table = reinterpret_cast<const Elf32_SectionHeader*>(file_bytes.data() + header.e_shoff);
    if (header.e_shstrndx >= header.e_shnum) {
        return std::unexpected("Некоректний індекс таблиці імен секцій");
    }

    const auto& str_sh = sh_table[header.e_shstrndx];
    if (str_sh.sh_offset + str_sh.sh_size > file_bytes.size()) {
        return std::unexpected("Таблиця імен секцій виходить за межі файлу");
    }

    const char* sh_names = reinterpret_cast<const char*>(file_bytes.data() + str_sh.sh_offset);

    ArtifactStats stats{};
    stats.crc32 = compute_crc32(file_bytes);

    for (size_t i = 0; i < header.e_shnum; ++i) {
        const auto& sh = sh_table[i];
        if (sh.sh_name >= str_sh.sh_size) continue;
        
        std::string_view name(sh_names + sh.sh_name);
        uint32_t size = sh.sh_size;

        if (name == ".text" || name == ".rodata") {
            stats.flash_used += size;
        } else if (name == ".data") {
            stats.flash_used += size;
            stats.ram_used += size;
        } else if (name == ".bss") {
            stats.ram_used += size;
        }

        if (name == ".rodata" && sh.sh_offset + size <= file_bytes.size()) {
            std::string_view rodata(reinterpret_cast<const char*>(file_bytes.data() + sh.sh_offset), size);
            if (rodata.find("-dirty") != std::string_view::npos) {
                stats.is_dirty = true;
            }
        }
    }

    return stats;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_образу.elf>\n";
        return 2;
    }

    std::ifstream file(argv[1], std::ios::binary | std::ios::ate);
    if (!file) {
        std::cerr << "ПОМИЛКА: Неможливо відкрити файл '" << argv[1] << "'\n";
        return 1;
    }

    const auto file_size = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<uint8_t> buffer(file_size);
    if (!file.read(reinterpret_cast<char*>(buffer.data()), file_size)) {
        std::cerr << "ПОМИЛКА: Не вдалося прочитати вміст файлу\n";
        return 1;
    }

    auto result = inspect_elf(buffer);
    if (!result) {
        std::cerr << "ВІДХИЛЕНО: " << result.error() << "\n";
        return 1;
    }

    const auto& stats = *result;
    std::cout << "=== ЗВІТ РЕЛІЗНОГО АРТЕФАКТУ: " << argv[1] << " ===\n";
    std::cout << "  Flash: " << stats.flash_used << " / " << FLASH_LIMIT_BYTES << " байтів\n";
    std::cout << "  RAM:   " << stats.ram_used << " / " << RAM_LIMIT_BYTES << " байтів\n";
    std::cout << "  CRC32: 0x" << std::hex << stats.crc32 << std::dec << "\n";

    if (stats.is_dirty) {
        std::cerr << "ВІДХИЛЕНО: Знайдено мітку '-dirty'! Образ містить незакомічені зміни.\n";
        return 1;
    }

    if (stats.flash_used > FLASH_LIMIT_BYTES || stats.ram_used > RAM_LIMIT_BYTES) {
        std::cerr << "ВІДХИЛЕНО: Пробито апаратний бюджет пам'яті!\n";
        return 1;
    }

    std::cout << "РЕЗУЛЬТАТ: Образ верифіковано успішно.\n";
    return 0;
}
