// Реалізація серіалізатора для C++17 (SFINAE + Priority Tag Dispatching)

// 1. Найвищий пріоритет (Tag 3): Власний метод serialize
template<typename T, std::enable_if_t<has_member_serialize_v<T>, int> = 0>
void write_impl(Buffer& buf, const T& obj, priority_tag<3>) {
    std::cout << "[SFINAE: Priority 3] Виклик obj.serialize(buf)\n";
    obj.serialize(buf);
}

// 2. Другий пріоритет (Tag 2): Вільна функція через ADL
template<typename T, std::enable_if_t<has_adl_serialize_v<T>, int> = 0>
void write_impl(Buffer& buf, const T& obj, priority_tag<2>) {
    std::cout << "[SFINAE: Priority 2] Виклик serialize(buf, obj) через ADL\n";
    serialize(buf, obj);
}

// 3. Третій пріоритет (Tag 1): Контейнери та послідовності
template<typename T, std::enable_if_t<is_iterable_container_v<T>, int> = 0>
void write_impl(Buffer& buf, const T& container, priority_tag<1>) {
    std::cout << "[SFINAE: Priority 1] Послідовна серіалізація контейнера\n";
    uint32_t sz = static_cast<uint32_t>(container.size());
    // Рекурсивно записуємо розмір
    const uint8_t* sz_ptr = reinterpret_cast<const uint8_t*>(&sz);
    buf.insert(buf.end(), sz_ptr, sz_ptr + sizeof(sz));
    for (const auto& item : container) {
        write_impl(buf, item, priority_tag<3>{});
    }
}

// 4. Четвертий пріоритет (Tag 0): Сирі тривіально копійовані байти
template<typename T, std::enable_if_t<std::is_trivially_copyable_v<T>, int> = 0>
void write_impl(Buffer& buf, const T& val, priority_tag<0>) {
    std::cout << "[SFINAE: Priority 0] Прямий запис сирих байтів пам'яті\n";
    const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&val);
    buf.insert(buf.end(), ptr, ptr + sizeof(T));
}

// Публічний фасад
template<typename T>
void write_data(Buffer& buf, const T& val) {
    write_impl(buf, val, priority_tag<3>{});
}
