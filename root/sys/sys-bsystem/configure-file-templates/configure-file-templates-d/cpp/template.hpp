// template.hpp.in (ПОМИЛКОВИЙ ПІДХІД БЕЗ @ONLY)
#pragma once
#include <string_view>

namespace app {
    inline constexpr std::string_view version = "@PROJECT_VERSION@";

    // Уявімо макрос чи коментар, де зустрічається синтаксис ${...}
    // або регулярний вираз для перевірки параметрів:
    // static constexpr auto pattern = R"(${USER_ID:[0-9]+})";
}
