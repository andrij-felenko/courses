// include/geomcalc.hpp
#pragma once

#include <cstddef>
#include <span>
#include <vector>
#include <expected>

namespace geom {

struct Point {
    double x{0.0};
    double y{0.0};
};

enum class ExportError {
    BufferTooSmall,
    CompressionFailed,
    EmptyInput
};

// Обчислює площу трикутника за трьома точками
double triangle_area(Point a, Point b, Point c) noexcept;

// Генерує стиснений бінарний звіт
std::expected<std::vector<unsigned char>, ExportError> 
export_compressed_report(std::span<const Point> points);

} // namespace geom
