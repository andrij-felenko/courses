// include/image.hpp — чистий публічний інтерфейс (C++)
#pragma once
#include <vector>
#include <cstdint>
#include <string_view>
#include <expected>

namespace img {

struct ImageBuffer {
    uint32_t width{0};
    uint32_t height{0};
    std::vector<uint8_t> pixels;
};

class Processor {
public:
    static std::expected<ImageBuffer, std::string> load_from_file(std::string_view path);
};

} // namespace img
