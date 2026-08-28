// src/internal_simd.h
#pragma once
#include <cstddef>
#include <cstdint>

namespace imgproc::internal {

void simd_process_rgb(uint8_t* data, size_t size);

} // namespace imgproc::internal
