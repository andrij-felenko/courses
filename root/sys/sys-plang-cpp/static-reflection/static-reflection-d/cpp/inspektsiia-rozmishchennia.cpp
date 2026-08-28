struct BadLayout {
    char a;     // 1 байт + 7 байтів padding
    double b;   // 8 байтів
    char c;     // 1 байт + 7 байтів padding
}; // Загальний розмір: 24 байти

consteval auto calculate_wasted_padding(std::meta::info class_info) -> size_t {
    size_t fields_total_size = 0;
    for (auto field : std::meta::nonstatic_data_members_of(class_info)) {
        fields_total_size += std::meta::size_of(std::meta::type_of(field));
    }
    return std::meta::size_of(class_info) - fields_total_size;
}

static_assert(calculate_wasted_padding(^^BadLayout) == 14);
