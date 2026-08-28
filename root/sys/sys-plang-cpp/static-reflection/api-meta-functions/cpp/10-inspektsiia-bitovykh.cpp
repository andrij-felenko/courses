struct NetworkHeader {
    uint8_t  version : 4;
    uint8_t  ihl     : 4;
    uint8_t  tos;
    uint16_t total_length;
};

consteval auto inspect_layout(std::meta::info type_info) {
    for (auto field : std::meta::nonstatic_data_members_of(type_info)) {
        if (std::meta::is_bit_field(field)) {
            // Отримання розрядності бітового поля
            size_t bits = std::meta::bit_size_of(field);
        } else {
            // Отримання байтового зміщення та розміру
            size_t byte_offset = std::meta::offset_of(field);
            size_t byte_size   = std::meta::size_of(std::meta::type_of(field));
        }
    }
}
