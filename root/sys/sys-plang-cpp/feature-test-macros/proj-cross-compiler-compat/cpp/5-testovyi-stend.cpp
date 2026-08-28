#include "compat/config.hpp"
#include "compat/span.hpp"
#include "compat/expected.hpp"
#include "compat/algorithm.hpp"
#include <iostream>
#include <string_view>
#include <vector>

enum class ParseError {
    EmptyBuffer,
    InvalidChecksum,
    Overflow
};

compat::expected<int, ParseError> parse_telemetry_frame(compat::span<const int> frame) {
    if (frame.empty()) COMPAT_UNLIKELY {
        return compat::unexpected(ParseError::EmptyBuffer);
    }

    const int total = compat::fast_accumulate(frame);
    if (total > 10000) COMPAT_UNLIKELY {
        return compat::unexpected(ParseError::Overflow);
    }

    return total;
}

int main() {
    std::cout << "Статус середовища компіляції:\n";
    std::cout << "  __cplusplus: " << __cplusplus << "\n";
    
#if defined(__cpp_concepts)
    std::cout << "  __cpp_concepts: " << __cpp_concepts << " (Рідні концепції)\n";
#else
    std::cout << "  __cpp_concepts: не підтримується (SFINAE fallback)\n";
#endif

#if defined(__cpp_lib_span)
    std::cout << "  __cpp_lib_span: " << __cpp_lib_span << " (Рідний std::span)\n";
#else
    std::cout << "  __cpp_lib_span: не підтримується (compat::span polyfill)\n";
#endif

#if defined(__cpp_lib_expected)
    std::cout << "  __cpp_lib_expected: " << __cpp_lib_expected << " (Рідний std::expected)\n";
#else
    std::cout << "  __cpp_lib_expected: не підтримується (compat::expected polyfill)\n";
#endif

    std::vector<int> sensor_data = {10, 20, 30, 40, 50};
    compat::span<const int> view(sensor_data.data(), sensor_data.size());

    auto result = parse_telemetry_frame(view);
    if (result.has_value()) {
        std::cout << "Успішно обчислено телеметрію: " << result.value() << "\n";
    } else {
        std::cout << "Помилка парсингу кадру телеметрії!\n";
    }

    return 0;
}
