#include <cmath>
#include <iostream>
#include <string>

// Мінімальний тест-каркас у дусі GoogleTest (EXPECT_*), без залежностей.
static int g_fail = 0, g_total = 0;

#define EXPECT_NEAR(got, want, eps) do {                                   \
    ++g_total;                                                             \
    double _g = (got), _w = (want);                                       \
    if (std::fabs(_g - _w) > (eps)) {                                     \
        ++g_fail;                                                          \
        std::cerr << "FAIL " << __func__ << ": got " << _g                 \
                  << ", want " << _w << "\n";                              \
    }                                                                      \
} while (0)

#define EXPECT_EQ_STR(got, want) do {                                      \
    ++g_total;                                                             \
    std::string _g = (got), _w = (want);                                  \
    if (_g != _w) { ++g_fail;                                              \
        std::cerr << "FAIL " << __func__ << ": got [" << _g                \
                  << "], want [" << _w << "]\n"; }                         \
} while (0)
