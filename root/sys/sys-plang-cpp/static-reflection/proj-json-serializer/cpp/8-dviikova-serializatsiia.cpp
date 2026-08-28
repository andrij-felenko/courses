template <typename T>
void serialize_binary(const T& obj, std::vector<uint8_t>& buffer) {
    constexpr auto type_info = ^^T;

    // Якщо структура тривіальна і не має вказівників — копіюємо весь блок пам'яті
    if constexpr (std::is_trivially_copyable_v<T>) {
        const auto* byte_ptr = reinterpret_cast<const uint8_t*>(&obj);
        buffer.insert(buffer.end(), byte_ptr, byte_ptr + sizeof(T));
    } else {
        // Поелементна серіалізація полів через рефлексію
        template for (constexpr auto member : std::meta::nonstatic_data_members_of(type_info)) {
            serialize_binary(obj.[: member :], buffer);
        }
    }
}
