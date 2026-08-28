#pragma once

#include <cstddef>
#include <cstdint>
#include <system_error>
#include <span>
#include <expected>

namespace math::matrix {

enum class perm_errc {
    success             = 0,
    null_pointer        = 1,
    invalid_dimension   = 2,
    out_of_memory       = 3,
    integer_overflow    = 4,
    unsupported_alg     = 5
};

enum class algorithm {
    auto_select = 0,
    naive       = 1,
    ryser_gray  = 2,
    glynn       = 3
};

struct config {
    algorithm   alg{algorithm::auto_select};
    std::size_t num_threads{0};
    bool        use_simd{true};
};

} // namespace math::matrix
