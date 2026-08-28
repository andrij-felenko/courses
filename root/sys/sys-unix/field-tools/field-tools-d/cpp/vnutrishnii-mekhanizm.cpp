// Гарячий цикл табличної трансляції байтів на C++20
#include <array>
#include <vector>
#include <iostream>
#include <span>
#include <unistd.h>

constexpr size_t BUF_SIZE = 65536;

void fast_tr_loop_cpp(const std::array<unsigned char, 256>& map) {
    std::vector<unsigned char> in_buf(BUF_SIZE);
    std::vector<unsigned char> out_buf(BUF_SIZE);
    ssize_t n_read = 0;

    while ((n_read = ::read(0, in_buf.data(), in_buf.size())) > 0) {
        std::span<const unsigned char> in_span(in_buf.data(), static_cast<size_t>(n_read));
        std::span<unsigned char> out_span(out_buf.data(), static_cast<size_t>(n_read));

        for (size_t i = 0; i < in_span.size(); ++i) {
            out_span[i] = map[in_span[i]];
        }
        ::write(1, out_span.data(), out_span.size());
    }
}
