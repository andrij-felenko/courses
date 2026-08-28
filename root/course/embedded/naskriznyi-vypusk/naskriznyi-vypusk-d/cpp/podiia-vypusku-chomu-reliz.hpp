#pragma once
#include <cstdint>
#include <string_view>

namespace version {

inline constexpr uint32_t Major = 2;
inline constexpr uint32_t Minor = 4;
inline constexpr uint32_t Patch = 0;
inline constexpr uint32_t CommitHash = 0x7a8f9c4b;
inline constexpr std::string_view String = "2.4.0";

} // namespace version
