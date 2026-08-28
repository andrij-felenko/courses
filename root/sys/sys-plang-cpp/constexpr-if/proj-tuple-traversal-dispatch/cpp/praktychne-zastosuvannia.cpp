template<typename... Types>
void print_as_json_array(const std::tuple<Types...>& t) {
    std::cout << "[";
    tuple_for_each(t, [](const auto& item, std::size_t index) {
        if (index > 0) {
            std::cout << ", ";
        }

        using ValueType = std::decay_t<decltype(item)>;

        // Статична інтроспекція типу кожного окремого поля
        if constexpr (std::is_same_v<ValueType, std::string> || 
                      std::is_same_v<ValueType, const char*>) {
            std::cout << '"' << item << '"';
        } else if constexpr (std::is_same_v<ValueType, bool>) {
            std::cout << (item ? "true" : "false");
        } else if constexpr (std::is_null_pointer_v<ValueType>) {
            std::cout << "null";
        } else {
            std::cout << item;
        }
    });
    std::cout << "]\n";
}

int main() {
    auto telemetry_record = std::make_tuple(
        42,
        std::string("Engine/Temperature"),
        98.6,
        true,
        nullptr
    );

    // Виведе: [42, "Engine/Temperature", 98.6, true, null]
    print_as_json_array(telemetry_record);
    return 0;
}
