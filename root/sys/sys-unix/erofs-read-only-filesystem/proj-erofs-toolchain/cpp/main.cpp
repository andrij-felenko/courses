#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <expected>
#include <string_view>
#include <iomanip>
#include <span>

constexpr uint32_t EROFS_SUPER_MAGIC = 0xE0F5E1E2;
constexpr std::streamoff EROFS_SUPER_OFFSET = 1024;

#pragma pack(push, 1)
struct ErofsSuperBlockRaw {
    uint32_t magic;
    uint32_t checksum;
    uint32_t feature_compat;
    uint8_t  blkszbits;
    uint8_t  sb_extslots;
    uint16_t root_nid;
    uint64_t inos;
    uint64_t build_time;
    uint32_t build_time_nsec;
    uint32_t blocks;
    uint32_t meta_blkaddr;
    uint32_t xattr_blkaddr;
    uint8_t  uuid[16];
    uint8_t  volume_name[16];
    uint32_t feature_incompat;
};
#pragma pack(pop)

struct ErofsParsedInfo {
    uint32_t magic;
    uint32_t block_size;
    uint32_t total_blocks;
    uint64_t total_bytes;
    uint32_t meta_block_addr;
    uint16_t root_nid;
    uint64_t root_inode_offset;
    uint32_t feature_incompat;
};

std::expected<ErofsParsedInfo, std::string> parse_erofs_image(const std::string& image_path) {
    std::ifstream file(image_path, std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected("Не вдалося відкрити файл образу EROFS");
    }

    file.seekg(EROFS_SUPER_OFFSET, std::ios::beg);
    if (!file.good()) {
        return std::unexpected("Помилка позиціонування у файлі образу");
    }

    ErofsSuperBlockRaw sb{};
    file.read(reinterpret_cast<char*>(&sb), sizeof(sb));
    if (file.gcount() != static_cast<std::streamsize>(sizeof(sb))) {
        return std::unexpected("Не вдалося зчитати повну структуру суперблоку");
    }

    if (sb.magic != EROFS_SUPER_MAGIC) {
        return std::unexpected("Некоректний Magic ID: файл не є образом EROFS");
    }

    uint32_t block_sz = 1U << sb.blkszbits;
    uint64_t total_sz = static_cast<uint64_t>(sb.blocks) * block_sz;
    uint64_t root_offset = static_cast<uint64_t>(sb.meta_blkaddr) * block_sz + static_cast<uint64_t>(sb.root_nid) * 32;

    return ErofsParsedInfo{
        .magic = sb.magic,
        .block_size = block_sz,
        .total_blocks = sb.blocks,
        .total_bytes = total_sz,
        .meta_block_addr = sb.meta_blkaddr,
        .root_nid = sb.root_nid,
        .root_inode_offset = root_offset,
        .feature_incompat = sb.feature_incompat
    };
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <path_to_erofs_img>\n";
        return 1;
    }

    auto result = parse_erofs_image(argv[1]);
    if (!result) {
        std::cerr << "Помилка аналізу: " << result.error() << "\n";
        return 1;
    }

    const auto& info = result.value();
    std::cout << "=== Метадані EROFS Суперблоку (C++ RAII) ===\n"
              << "Сигнатура Magic     : 0x" << std::hex << std::uppercase << info.magic << std::dec << " (Успішно)\n"
              << "Розмір блоку        : " << info.block_size << " байт\n"
              << "Загалом блоків      : " << info.total_blocks << " (" << info.total_bytes << " B)\n"
              << "Адреса метаданих    : блок " << info.meta_block_addr << "\n"
              << "Кореневий NID       : " << info.root_nid << "\n"
              << "Зсув кореневого inode: " << info.root_inode_offset << " байт\n"
              << "Прапорці incompat   : 0x" << std::hex << info.feature_incompat << std::dec << "\n";

    return 0;
}
