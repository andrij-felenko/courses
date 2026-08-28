namespace modern_cpp20 {

// Концепт 1: Типи, які надають власний метод збереження serialize_to
template<typename T>
concept CustomSerializable = requires(const T& obj, BinaryBuffer& buf) {
    obj.serialize_to(buf);
};

// Концепт 2: Стандартні ітеровані контейнери
template<typename T>
concept SerializableContainer = requires(const T& container) {
    { container.begin() } -> std::input_or_output_iterator;
    { container.end() } -> std::input_or_output_iterator;
    { container.size() } -> std::convertible_to<std::size_t>;
} && !std::same_as<std::remove_cvref_t<T>, std::string>;

// Уніфікована функція серіалізації нового покоління
template<typename T>
void serialize(BinaryBuffer& buf, const T& value) {
    using PureType = std::remove_cvref_t<T>;

    if constexpr (CustomSerializable<PureType>) {
        // Пріоритет 1: Власний метод класу
        value.serialize_to(buf);
    } 
    else if constexpr (std::same_as<PureType, std::string>) {
        // Пріоритет 2: Рядки std::string
        uint32_t len = static_cast<uint32_t>(value.size());
        buf.write_raw(&len, sizeof(len));
        buf.write_raw(value.data(), len);
    } 
    else if constexpr (std::same_as<PureType, const char*> || std::same_as<PureType, char*>) {
        // Пріоритет 3: Рядки C-стилю
        if (value == nullptr) {
            uint32_t zero = 0;
            buf.write_raw(&zero, sizeof(zero));
        } else {
            uint32_t len = static_cast<uint32_t>(std::strlen(value));
            buf.write_raw(&len, sizeof(len));
            buf.write_raw(value, len);
        }
    } 
    else if constexpr (SerializableContainer<PureType>) {
        // Пріоритет 4: Контейнери (вектори, списки, множини)
        uint32_t count = static_cast<uint32_t>(value.size());
        buf.write_raw(&count, sizeof(count));
        for (const auto& item : value) {
            serialize(buf, item); // Рекурсивне збереження
        }
    } 
    else if constexpr (std::is_pointer_v<PureType>) {
        // Пріоритет 5: Довільні вказівники
        uint8_t has_val = (value != nullptr) ? 1 : 0;
        buf.write_raw(&has_val, sizeof(has_val));
        if (value != nullptr) {
            serialize(buf, *value);
        }
    } 
    else if constexpr (std::is_trivially_copyable_v<PureType>) {
        // Пріоритет 6: Скаляри та плоскі структури
        if constexpr (std::is_integral_v<PureType> && sizeof(PureType) > 1) {
            PureType be_val = value;
            if constexpr (std::endian::native == std::endian::little) {
                be_val = std::byteswap(value);
            }
            buf.write_raw(&be_val, sizeof(PureType));
        } else {
            buf.write_raw(&value, sizeof(PureType));
        }
    } 
    else {
        // Якщо жодна гілка не підійшла — зупиняємо збірку з детальним повідомленням
        static_assert(!sizeof(T), "Помилка компіляції: тип не підтримує бінарну серіалізацію!");
    }
}

} // namespace modern_cpp20
