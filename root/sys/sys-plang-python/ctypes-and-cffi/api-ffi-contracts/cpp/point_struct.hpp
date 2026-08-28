// point_struct.hpp
#pragma once
#include <cstdint>
#include <array>

struct PointRecord {
    std::int32_t x;
    std::int32_t y;
    double       weight;
    std::uint8_t flags;
};

union FloatIntUnion {
    std::uint32_t           as_uint;
    float                   as_float;
    std::array<std::uint8_t, 4> as_bytes;
};
