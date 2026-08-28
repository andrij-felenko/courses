// src/internal_simd.cpp
#include "internal_simd.h"

namespace imgproc::internal {

void simd_process_rgb(uint8_t* data, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        data[i] = static_cast<uint8_t>(data[i] * 0.9f);
    }
}

} // namespace imgproc::internal
