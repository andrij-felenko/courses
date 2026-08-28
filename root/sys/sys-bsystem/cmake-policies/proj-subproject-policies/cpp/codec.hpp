// third_party/legacy_codec/codec.hpp — C++ інтерфейс-обгортка
#pragma once
#include <string_view>
#include <span>
#include <vector>
#include <cstdint>

extern "C" {
#include "codec.h"
}

namespace legacy {
inline std::vector<char> encode(std::string_view input) {
    std::vector<char> buffer(input.size() * 2 + 16);
    int written = legacy_encode(input.data(), input.size(), buffer.data(), buffer.size());
    if (written >= 0) {
        buffer.resize(static_cast<size_t>(written));
    } else {
        buffer.clear();
    }
    return buffer;
}
} // namespace legacy
