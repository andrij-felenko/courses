template<typename T>
concept IntegralNumber = std::integral<T> && (sizeof(T) > 1);

template<ByteStream S, IntegralNumber T>
void write_network_order(S& stream, T value) {
    if constexpr (std::endian::native == std::endian::little) {
        // На little-endian платформах реверсуємо порядок байтів під час компіляції/виконання
        // У C++23 доступна функція std::byteswap:
        #if defined(__cpp_lib_byteswap)
            const T swapped = std::byteswap(value);
        #else
            // Сумісна реалізація для C++20
            T swapped = value;
            auto* p = reinterpret_cast<std::byte*>(&swapped);
            std::reverse(p, p + sizeof(T));
        #endif
        BinarySerializer::serialize(stream, swapped);
    } else {
        // На big-endian платформах записуємо без змін
        BinarySerializer::serialize(stream, value);
    }
}
