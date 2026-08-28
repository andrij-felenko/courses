class BinaryDeserializer {
public:
    // Стратегія 1: Читання тривіальних типів
    template<ByteSource S, TriviallySerializable T>
    static void deserialize(S& source, T& value) {
        auto* byte_ptr = reinterpret_cast<std::byte*>(std::addressof(value));
        const auto read_bytes = source.read(std::span<std::byte>(byte_ptr, sizeof(T)));
        if (read_bytes != sizeof(T)) {
            throw std::runtime_error("Недостатньо байтів у потоці для відновлення об'єкта");
        }
    }

    // Стратегія 2: Об'єкти з власним методом десеріалізації
    template<ByteSource S, typename T>
    requires CustomDeserializable<T, S>
    static void deserialize(S& source, T& value) {
        value.deserialize(source);
    }

    // Стратегія 3: Відновлення рядків std::string
    template<ByteSource S>
    static void deserialize(S& source, std::string& str) {
        std::uint32_t length = 0;
        deserialize(source, length);

        str.resize(length);
        if (length > 0) {
            auto* byte_ptr = reinterpret_cast<std::byte*>(str.data());
            const auto read_bytes = source.read(std::span<std::byte>(byte_ptr, length));
            if (read_bytes != length) {
                throw std::runtime_error("Помилка читання рядка: неочікуваний кінець потоку");
            }
        }
    }

    // Стратегія 4: Відновлення неперервних тривіальних векторів через прямий memcpy
    template<ByteSource S, typename T>
    requires TriviallySerializable<T>
    static void deserialize(S& source, std::vector<T>& vec) {
        std::uint32_t count = 0;
        deserialize(source, count);

        vec.resize(count);
        if (count > 0) {
            const auto total_bytes = count * sizeof(T);
            auto* byte_ptr = reinterpret_cast<std::byte*>(vec.data());
            const auto read_bytes = source.read(std::span<std::byte>(byte_ptr, total_bytes));
            if (read_bytes != total_bytes) {
                throw std::runtime_error("Помилка блокового читання вектора");
            }
        }
    }

    // Стратегія 5: Відновлення динамічних контейнерів загального типу
    template<ByteSource S, DeserializableContainer T>
    static void deserialize(S& source, T& container) {
        std::uint32_t count = 0;
        deserialize(source, count);

        container.clear();
        for (std::uint32_t i = 0; i < count; ++i) {
            using ElementType = std::ranges::range_value_t<T>;
            ElementType element{};
            deserialize(source, element);
            container.emplace_back(std::move(element));
        }
    }
};
