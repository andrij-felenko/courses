#include <type_traits>
#include <string>
#include <memory>

template<typename T>
auto serialize_value(const T& val) {
    if constexpr (std::is_pointer_v<T>) {
        if (val == nullptr) {
            return std::string("null");
        }
        return std::to_string(*val);
    } else if constexpr (std::is_same_v<T, std::string>) {
        return '"' + val + '"';
    } else if constexpr (std::is_arithmetic_v<T>) {
        return std::to_string(val);
    } else {
        return val.to_string();
    }
}
