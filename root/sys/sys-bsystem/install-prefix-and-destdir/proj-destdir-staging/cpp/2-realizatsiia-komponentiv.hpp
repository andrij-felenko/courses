// include/calc/math_ops.h
#pragma once

#if defined(_WIN32)
  #if defined(calc_EXPORTS)
    #define CALC_API __declspec(dllexport)
  #else
    #define CALC_API __declspec(dllimport)
  #endif
#else
  #define CALC_API __attribute__((visibility("default")))
#endif

extern "C" {
    CALC_API int calc_add(int a, int b);
    CALC_API int calc_mul(int a, int b);
}
