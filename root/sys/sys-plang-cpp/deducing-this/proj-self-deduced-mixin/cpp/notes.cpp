// notes.cpp — усе, що нижче, лежить у цьому файлі в такому ж порядку
#include <algorithm>
#include <concepts>
#include <iostream>
#include <memory>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

#if !defined(__cpp_explicit_this_parameter) || __cpp_explicit_this_parameter < 202110L
#  error "нема явного параметра об'єкта: треба GCC 14+, Clang 18+ або MSVC 19.32+"
#endif
#if !defined(__cpp_lib_forward_like) || __cpp_lib_forward_like < 202207L
#  error "нема std::forward_like: треба стандартна бібліотека C++23"
#endif
