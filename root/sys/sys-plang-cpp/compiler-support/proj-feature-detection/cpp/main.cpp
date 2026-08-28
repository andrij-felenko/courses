// main.cpp
#include <iostream>
#include <vector>
#include <string>
#include <chrono>

#include "compat/version_check.hpp"
#include "compat/serialize_feature.hpp"
#include "compat/matrix.hpp"
#include "compat/span.hpp"
#include "compat/expected.hpp"
#include "compat/format.hpp"
#include "compat/jthread.hpp"
#include "compat/utilities.hpp"
#include "compat/ranges.hpp"
#include "compat/attributes.hpp"

enum class Status : uint16_t {
    Ready = 1,
    Processing = 2,
    Failed = 3
};

struct UserData {
    uint32_t id;
    uint32_t flags;
};

compat::expected<UserData, std::string> parse_user(uint32_t raw_id) {
    if (raw_id == 0) {
        return compat::unexpected<std::string>("ID cannot be zero");
    }
    return UserData{raw_id, 0x01};
}

void print_buffer_span(compat::span<const uint8_t> buffer_view) {
    std::cout << "Span view of buffer (size=" << buffer_view.size() << "): ";
    for (auto byte : buffer_view) {
        std::cout << static_cast<int>(byte) << " ";
    }
    std::cout << "\n";
}

int main() {
    std::cout << "Compiler standard check: __cplusplus = " << __cplusplus << "\n";

#if defined(__cpp_concepts)
    std::cout << "Feature: __cpp_concepts = " << __cpp_concepts << " (Active)\n";
#else
    std::cout << "Feature: __cpp_concepts is not active (Using SFINAE fallback)\n";
#endif

#if defined(__cpp_lib_span)
    std::cout << "Library: __cpp_lib_span = " << __cpp_lib_span << " (Standard std::span)\n";
#else
    std::cout << "Library: Using compat::span polyfill\n";
#endif

#if defined(__cpp_lib_expected)
    std::cout << "Library: __cpp_lib_expected = " << __cpp_lib_expected << " (Standard std::expected)\n";
#else
    std::cout << "Library: Using compat::expected polyfill\n";
#endif

#if defined(__cpp_lib_jthread)
    std::cout << "Library: __cpp_lib_jthread = " << __cpp_lib_jthread << " (Standard std::jthread)\n";
#else
    std::cout << "Library: Using compat::jthread polyfill\n";
#endif

    // Тест форматування через міст compat::format
    std::string formatted_msg = compat::format("Formatted user info: id={}, active={}", 101, true);
    std::cout << formatted_msg << "\n";

    // Тест утиліти to_underlying
    auto status_val = compat::to_underlying(Status::Ready);
    std::cout << "Underlying status value: " << status_val << "\n";

    // Тест утиліти bit_cast
    float f_val = 1.0f;
    auto u_val = compat::bit_cast<uint32_t>(f_val);
    std::cout << "Bit cast of 1.0f to uint32: 0x" << std::hex << u_val << std::dec << "\n";

    // Тест серіалізації
    UserData user{101, 0xFF};
    std::vector<uint8_t> buffer;
    compat::serialize(user, buffer);
    std::cout << "Serialized buffer size: " << buffer.size() << " bytes\n";

    // Тест перегляду через span
    print_buffer_span(buffer);

    // Тест матриці та індексації
    compat::Matrix2D<int> mat(3, 3);
    mat(0, 0) = 42;
#if defined(__cpp_multidimensional_subscript)
    mat[1, 1] = 84;
    std::cout << "Matrix[1, 1] via C++23 subscript: " << mat[1, 1] << "\n";
#else
    std::cout << "Matrix(0, 0) via fallback call: " << mat(0, 0) << "\n";
#endif

    // Тест обробки помилок через expected
    auto result = parse_user(0);
    if (!result) {
        std::cout << "Handled expected error: " << result.error() << "\n";
    }

    // Тест кооперативного потоку jthread
    compat::jthread worker([](compat::stop_token st) {
        while (!st.stop_requested()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            break;
        }
    });
    worker.request_stop();

    return 0;
}
