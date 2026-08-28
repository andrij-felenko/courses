#pragma once
#include <cstdint>
#include <string_view>

namespace version {

inline constexpr uint32_t Major = 2;
inline constexpr uint32_t Minor = 4;
inline constexpr uint32_t Patch = 1;
inline constexpr uint32_t SecurityCounter = 5U; // Підвищено для апаратного блокування CVE
inline constexpr uint32_t CommitHashPrefix = 0x7a8f9c4bU;
inline constexpr std::string_view String = "2.4.1-hotfix";

} // namespace version
