#include <getopt.h>
#include <array>
#include <string_view>

// Типобезпечна таблиця опцій у C++20
inline constexpr std::array<option, 5> LongOptions{{
    {"output",  required_argument, nullptr, 'o'},
    {"verbose", no_argument,       nullptr, 'v'},
    {"color",   optional_argument, nullptr, 'c'},
    {"help",    no_argument,       nullptr, 'h'},
    {nullptr, 0, nullptr, 0}
}};
