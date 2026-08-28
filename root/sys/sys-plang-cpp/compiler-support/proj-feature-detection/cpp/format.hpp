// compat/format.hpp
#pragma once

#include "version_check.hpp"

#if defined(__cpp_lib_format) && (__cpp_lib_format >= 201907L)

    #include <format>

    namespace compat {
        template <typename... Args>
        std::string format(std::format_string<Args...> fmt_str, Args&&... args) {
            return std::format(fmt_str, std::forward<Args>(args)...);
        }
    }

#else

    #include <string>
    #include <sstream>
    #include <utility>

    namespace compat {

        inline void format_helper(std::ostringstream& ss, std::string_view fmt_str) {
            ss << fmt_str;
        }

        template <typename T, typename... Args>
        void format_helper(std::ostringstream& ss, std::string_view fmt_str, T&& val, Args&&... rest) {
            size_t pos = fmt_str.find("{}");
            if (pos != std::string_view::npos) {
                ss << fmt_str.substr(0, pos);
                ss << val;
                format_helper(ss, fmt_str.substr(pos + 2), std::forward<Args>(rest)...);
            } else {
                ss << fmt_str;
            }
        }

        template <typename... Args>
        std::string format(std::string_view fmt_str, Args&&... args) {
            std::ostringstream ss;
            format_helper(ss, fmt_str, std::forward<Args>(args)...);
            return ss.str();
        }

    } // namespace compat

#endif
