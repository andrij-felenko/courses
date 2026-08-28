// compat/ranges.hpp
#pragma once

#include <vector>
#include <algorithm>

#include "version_check.hpp"

namespace compat {

#if defined(__cpp_lib_ranges) && (__cpp_lib_ranges >= 201911L)

    #include <ranges>

    namespace views {
        using namespace std::views;
    }

#else

    namespace views {

        template <typename Container, typename Predicate>
        auto filter(const Container& c, Predicate pred) {
            std::vector<typename Container::value_type> result;
            for (const auto& item : c) {
                if (pred(item)) {
                    result.push_back(item);
                }
            }
            return result;
        }

        template <typename Container, typename TransformFn>
        auto transform(const Container& c, TransformFn fn) {
            using OutType = decltype(fn(*std::begin(c)));
            std::vector<OutType> result;
            result.reserve(c.size());
            for (const auto& item : c) {
                result.push_back(fn(item));
            }
            return result;
        }

    } // namespace views

#endif

} // namespace compat
