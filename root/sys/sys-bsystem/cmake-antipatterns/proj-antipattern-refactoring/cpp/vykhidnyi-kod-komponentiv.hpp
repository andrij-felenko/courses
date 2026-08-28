// include/imgproc/filter.h
#pragma once
#include <vector>
#include <cstdint>

namespace imgproc {

class Filter {
public:
    static void apply_grayscale(std::vector<uint8_t>& image_buffer);
};

} // namespace imgproc
