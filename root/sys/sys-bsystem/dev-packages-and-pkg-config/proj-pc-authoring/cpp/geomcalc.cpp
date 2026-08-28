// src/geomcalc.cpp
#include "geomcalc.hpp"
#include <cmath>
#include <zlib.h>

namespace geom {

double triangle_area(Point a, Point b, Point c) noexcept {
    return 0.5 * std::abs(a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
}

std::expected<std::vector<unsigned char>, ExportError> 
export_compressed_report(std::span<const Point> points) {
    if (points.empty()) {
        return std::unexpected(ExportError::EmptyInput);
    }

    const size_t raw_bytes = points.size_bytes();
    uLongf max_dest_len = compressBound(static_cast<uLong>(raw_bytes));
    std::vector<unsigned char> compressed(max_dest_len);

    uLongf actual_len = max_dest_len;
    int z_res = compress(compressed.data(), &actual_len, 
                         reinterpret_cast<const Bytef*>(points.data()), 
                         static_cast<uLong>(raw_bytes));
                         
    if (z_res != Z_OK) {
        return std::unexpected(ExportError::CompressionFailed);
    }

    compressed.resize(actual_len);
    return compressed;
}

} // namespace geom
