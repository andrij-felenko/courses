// src/filter.cpp
#include "imgproc/filter.h"
#include "internal_simd.h"
#include <iostream>

namespace imgproc {

void Filter::apply_grayscale(std::vector<uint8_t>& image_buffer) {
    internal::simd_process_rgb(image_buffer.data(), image_buffer.size());
    std::cout << "Фільтр успішно застосовано до " << image_buffer.size() << " байтів." << std::endl;
}

} // namespace imgproc
