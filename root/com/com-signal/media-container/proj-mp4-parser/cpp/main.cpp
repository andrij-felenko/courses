#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <span>
#include <cstdint>
#include <array>

// RAII-клас для безпечного парсингу MP4-файлів у стилі C++20
class Mp4BoxParser {
public:
    struct BoxInfo {
        std::string type;
        uint32_t size;
        size_t offset;
        int depth;
    };

    static std::uint32_t readUint32BE(std::span<const std::uint8_t> data, size_t offset) {
        return (static_cast<std::uint32_t>(data[offset]) << 24) |
               (static_cast<std::uint32_t>(data[offset + 1]) << 16) |
               (static_cast<std::uint32_t>(data[offset + 2]) << 8)  |
                static_cast<std::uint32_t>(data[offset + 3]);
    }

    static bool isContainer(std::string_view type) {
        static constexpr std::array<std::string_view, 5> containers = {
            "moov", "trak", "mdia", "minf", "stbl"
        };
        for (const auto& c : containers) {
            if (c == type) return true;
        }
        return false;
    }

    explicit Mp4BoxParser(std::vector<std::uint8_t> buffer) 
        : buffer_(std::move(buffer)) {}

    std::vector<BoxInfo> parse() const {
        std::vector<BoxInfo> result;
        parseRecursive(std::span<const std::uint8_t>(buffer_), 0, buffer_.size(), 0, result);
        return result;
    }

private:
    std::vector<std::uint8_t> buffer_;

    void parseRecursive(std::span<const std::uint8_t> data, 
                        size_t offset, 
                        size_t maxOffset, 
                        int depth, 
                        std::vector<BoxInfo>& outBoxes) const {
        while (offset + 8 <= maxOffset) {
            uint32_t boxSize = readUint32BE(data, offset);
            std::string typeStr(reinterpret_cast<const char*>(data.data() + offset + 4), 4);

            if (boxSize == 0) {
                boxSize = static_cast<uint32_t>(maxOffset - offset);
            } else if (boxSize < 8) {
                break;
            }

            if (offset + boxSize > maxOffset) {
                break;
            }

            outBoxes.push_back({typeStr, boxSize, offset, depth});

            if (isContainer(typeStr)) {
                parseRecursive(data, offset + 8, offset + boxSize, depth + 1, outBoxes);
            }

            offset += boxSize;
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <файл.mp4>\n";
        return 1;
    }

    std::ifstream file(argv[1], std::ios::binary | std::ios::ate);
    if (!file) {
        std::cerr << "Помилка відкриття файлу: " << argv[1] << "\n";
        return 1;
    }

    const auto fileSize = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<std::uint8_t> buffer(fileSize);
    if (!file.read(reinterpret_cast<char*>(buffer.data()), fileSize)) {
        std::cerr << "Помилка зчитання даних\n";
        return 1;
    }

    Mp4BoxParser parser(std::move(buffer));
    const auto boxes = parser.parse();

    std::cout << "=== Дерево боксів ISOBMFF / MP4 (C++20) ===\n";
    for (const auto& box : boxes) {
        for (int i = 0; i < box.depth; ++i) std::cout << "  ";
        std::cout << "Box: [" << box.type << "] Size: " << box.size 
                  << ", Offset: " << box.offset << "\n";
    }

    return 0;
}
