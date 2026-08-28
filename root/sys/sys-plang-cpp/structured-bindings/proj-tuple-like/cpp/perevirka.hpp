hw::Sample s{40000, "ch0"};
static_assert(std::tuple_size_v<hw::Sample> == 2);

auto& [u, tag] = s;                    // e — Sample&, працює get() &
static_assert(std::is_same_v<decltype(u),   double>);
static_assert(std::is_same_v<decltype(tag), std::string>);

const auto& [cu, ctag] = s;            // e — const Sample&, працює get() const&
static_assert(std::is_same_v<decltype(cu),   const double>);
static_assert(std::is_same_v<decltype(ctag), const std::string>);

tag = "ch0-rev2";                      // пише в поле s: tag — ім'я підоб'єкта
u   = 0.0;                             // пише в тимчасовий double: s не змінився
