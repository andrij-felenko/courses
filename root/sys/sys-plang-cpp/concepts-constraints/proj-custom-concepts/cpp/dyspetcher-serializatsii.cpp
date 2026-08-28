class BinarySerializer {
public:
    // Стратегія 1: Прямий запис тривіальних типів у пам'ять (POD, числа, структури)
    template<ByteStream S, TriviallySerializable T>
    static void serialize(S& stream, const T& value) {
        const auto* byte_ptr = reinterpret_cast<const std::byte*>(std::addressof(value));
        stream.write(std::span<const std::byte>(byte_ptr, sizeof(T)));
    }

    // Стратегія 2: Об'єкти з власною бізнес-логікою серіалізації
    template<ByteStream S, typename T>
    requires CustomSerializable<T, S>
    static void serialize(S& stream, const T& value) {
        value.serialize(stream);
    }

    // Стратегія 3: Рядки та рядкові перегляди (довжина + байти)
    template<ByteStream S, StringLike T>
    static void serialize(S& stream, const T& value) {
        const auto length = static_cast<std::uint32_t>(std::ranges::size(value));
        serialize(stream, length);

        if (length > 0) {
            const auto* byte_ptr = reinterpret_cast<const std::byte*>(std::ranges::data(value));
            stream.write(std::span<const std::byte>(byte_ptr, length));
        }
    }

    // Стратегія 4: Неперервні діапазони тривіальних типів (вектори POD) — надшвидке блокове копіювання
    template<ByteStream S, TriviallyContiguousRange T>
    static void serialize(S& stream, const T& value) {
        using ElementType = std::ranges::range_value_t<T>;
        const auto count = static_cast<std::uint32_t>(std::ranges::size(value));
        serialize(stream, count);

        if (count > 0) {
            const auto total_bytes = count * sizeof(ElementType);
            const auto* byte_ptr = reinterpret_cast<const std::byte*>(std::ranges::data(value));
            stream.write(std::span<const std::byte>(byte_ptr, total_bytes));
        }
    }

    // Стратегія 5: Узагальнені нетривіальні контейнери (рекурсивний обхід)
    template<ByteStream S, SerializableRange T>
    static void serialize(S& stream, const T& value) {
        const auto count = static_cast<std::uint32_t>(std::ranges::size(value));
        serialize(stream, count);

        for (const auto& item : value) {
            serialize(stream, item);
        }
    }
};
