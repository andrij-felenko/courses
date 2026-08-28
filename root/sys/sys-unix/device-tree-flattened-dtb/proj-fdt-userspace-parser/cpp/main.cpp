#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <cstdint>
#include <bit>
#include <expected>
#include <stdexcept>

namespace fdt {

constexpr uint32_t FDT_MAGIC      = 0xd00dfeed;
constexpr uint32_t FDT_BEGIN_NODE = 0x00000001;
constexpr uint32_t FDT_END_NODE   = 0x00000002;
constexpr uint32_t FDT_PROP       = 0x00000003;
constexpr uint32_t FDT_NOP        = 0x00000004;
constexpr uint32_t FDT_END        = 0x00000009;

struct Header {
    uint32_t magic;
    uint32_t totalsize;
    uint32_t off_dt_struct;
    uint32_t off_dt_strings;
    uint32_t off_mem_rsvmap;
    uint32_t version;
    uint32_t last_comp_version;
    uint32_t boot_cpuid_phys;
    uint32_t size_dt_strings;
    uint32_t size_dt_struct;
};

// Конвертація з Big-Endian у хостовий порядок байтів
constexpr uint32_t from_be32(uint32_t val) noexcept {
    if constexpr (std::endian::native == std::endian::little) {
        return std::byteswap(val);
    }
    return val;
}

class Parser {
public:
    explicit Parser(std::vector<uint8_t> buffer) : data_(std::move(buffer)) {}

    std::expected<void, std::string> parse() {
        if (data_.size() < sizeof(Header)) {
            return std::unexpected("Буфер занадто малий для заголовка FDT");
        }

        const auto* hdr = reinterpret_cast<const Header*>(data_.data());
        if (from_be32(hdr->magic) != FDT_MAGIC) {
            return std::unexpected("Некоректна сигнатура FDT Header");
        }

        const uint32_t off_struct = from_be32(hdr->off_dt_struct);
        const uint32_t off_strings = from_be32(hdr->off_dt_strings);

        if (off_struct >= data_.size() || off_strings >= data_.size()) {
            return std::unexpected("Зсуви заголовка виходять за межі файлу");
        }

        const auto* pstruct = reinterpret_cast<const uint32_t*>(data_.data() + off_struct);
        const char* pstrings = reinterpret_cast<const char*>(data_.data() + off_strings);

        std::size_t depth = 0;
        bool running = true;

        while (running) {
            uint32_t tag = from_be32(*pstruct++);

            switch (tag) {
            case FDT_BEGIN_NODE: {
                std::string_view name(reinterpret_cast<const char*>(pstruct));
                if (name.empty()) {
                    name = "/";
                }
                print_indent(depth);
                std::cout << "Node: " << name << " {\n";
                depth++;

                std::size_t name_bytes = name.size() + 1;
                std::size_t padded = (name_bytes + 3) & ~3U;
                pstruct += padded / 4;
                break;
            }
            case FDT_END_NODE:
                if (depth > 0) depth--;
                print_indent(depth);
                std::cout << "};\n";
                break;

            case FDT_PROP: {
                uint32_t len = from_be32(*pstruct++);
                uint32_t nameoff = from_be32(*pstruct++);
                std::string_view prop_name(pstrings + nameoff);

                print_indent(depth);
                std::cout << "Property '" << prop_name << "' (len=" << len << ")\n";

                std::size_t padded = (len + 3) & ~3U;
                pstruct += padded / 4;
                break;
            }
            case FDT_NOP:
                break;

            case FDT_END:
                running = false;
                break;

            default:
                return std::unexpected("Знайдено невідомий токен у блоці структур");
            }
        }

        return {};
    }

private:
    static void print_indent(std::size_t depth) {
        for (std::size_t i = 0; i < depth; ++i) {
            std::cout << "  ";
        }
    }

    std::vector<uint8_t> data_;
};

} // namespace fdt

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <file.dtb>\n";
        return 1;
    }

    std::ifstream file(argv[1], std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        std::cerr << "Не вдалося відкрити DTB файл\n";
        return 1;
    }

    const auto size = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<uint8_t> buffer(size);
    if (!file.read(reinterpret_cast<char*>(buffer.data()), size)) {
        std::cerr << "Помилка читання даних\n";
        return 1;
    }

    fdt::Parser parser(std::move(buffer));
    if (auto result = parser.parse(); !result) {
        std::cerr << "Помилка парсингу: " << result.error() << '\n';
        return 1;
    }

    return 0;
}
