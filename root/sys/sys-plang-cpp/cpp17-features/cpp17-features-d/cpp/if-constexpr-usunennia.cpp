template <typename T>
void serialize(Serializer& s, const T& value) {
    if constexpr (std::is_arithmetic_v<T>) {
        s.write_raw_bytes(&value, sizeof(T));
    } else if constexpr (std::is_same_v<T, std::string>) {
        s.write_uint32(value.size());
        s.write_raw_bytes(value.data(), value.size());
    } else {
        value.custom_serialize(s); // Інстанціюється лише для користувацьких класів!
    }
}
