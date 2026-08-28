#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <iomanip>
#include <expected>
#include <string_view>
#include <format>

constexpr std::size_t SETUP_HEADER_OFFSET = 0x01F1;
constexpr uint32_t HDRS_MAGIC = 0x53726448; /* "HdrS" */

struct alignas(1) SetupHeader {
    uint8_t  setup_sects;
    uint16_t root_flags;
    uint32_t syssize;
    uint16_t ram_size;
    uint16_t vid_mode;
    uint16_t root_dev;
    uint16_t boot_flag;
    uint16_t jump;
    uint32_t header;
    uint16_t version;
    uint32_t realmode_swtch;
    uint16_t start_sys_seg;
    uint16_t kernel_version;
    uint8_t  type_of_loader;
    uint8_t  loadflags;
    uint16_t setup_move_size;
    uint32_t code32_start;
    uint32_t ramdisk_image;
    uint32_t ramdisk_size;
    uint32_t bootsect_kludge;
    uint16_t heap_end_ptr;
    uint8_t  ext_loader_ver;
    uint8_t  ext_loader_type;
    uint32_t cmd_line_ptr;
    uint32_t initrd_addr_max;
};

class VmlinuzHeaderParser {
public:
    static std::expected<SetupHeader, std::string> parse_file(const std::string& path) {
        std::ifstream file(path, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected(std::format("Не вдалося відкрити файл: {}", path));
        }

        file.seekg(SETUP_HEADER_OFFSET, std::ios::beg);
        if (!file) {
            return std::unexpected("Помилка позиціонування на зсув setup_header");
        }

        SetupHeader header{};
        file.read(reinterpret_cast<char*>(&header), sizeof(SetupHeader));
        if (!file) {
            return std::unexpected("Помилка зчитування структури SetupHeader");
        }

        if (header.header != HDRS_MAGIC) {
            return std::unexpected(std::format("Невалідний заголовок ядра: magic 0x{:08X}", header.header));
        }

        return header;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << std::format("Використання: {} <шлях_до_vmlinuz>\n", argv[0]);
        return 1;
    }

    auto result = VmlinuzHeaderParser::parse_file(argv[1]);
    if (!result) {
        std::cerr << std::format("Помилка: {}\n", result.error());
        return 1;
    }

    const auto& hdr = result.value();
    uint8_t major = hdr.version >> 8;
    uint8_t minor = hdr.version & 0xFF;

    std::cout << "=== Інспекція заголовка vmlinuz (C++23 Modern RAII) ===\n";
    std::cout << std::format("Сигнатура:             HdrS (0x{:08X})\n", hdr.header);
    std::cout << std::format("Версія протоколу:      {}.{:02d} (0x{:04X})\n", major, minor, hdr.version);
    std::cout << std::format("Точка входу (code32):  0x{:08X}\n", hdr.code32_start);
    std::cout << std::format("Максимальна адреса initrd: 0x{:08X}\n", hdr.initrd_addr_max);
    std::cout << std::format("Прапори завантаження:  0x{:02X}\n", hdr.loadflags);

    return 0;
}
