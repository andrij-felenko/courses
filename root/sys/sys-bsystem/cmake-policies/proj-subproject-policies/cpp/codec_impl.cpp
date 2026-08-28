// third_party/legacy_codec/codec_impl.cpp — еквівалентна C++ реалізація
#include "codec.h"
#include <iostream>
#include <algorithm>

extern "C" int legacy_encode(const char *input, size_t input_len, char *output, size_t max_out) {
    if (!input || !output || max_out < input_len + 1) {
        return -1;
    }
#ifdef CODEC_VERBOSE
    std::cerr << "[codec] Encoding " << input_len << " bytes of stream\n";
#endif
    std::transform(input, input + input_len, output, [](char c) {
        return static_cast<char>(c ^ 0x5A);
    });
    output[input_len] = '\0';
    return static_cast<int>(input_len);
}
