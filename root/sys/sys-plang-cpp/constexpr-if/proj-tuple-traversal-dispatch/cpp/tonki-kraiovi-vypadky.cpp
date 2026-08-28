template<typename T>
void transmit_safe(T& obj) {
    if constexpr (std::is_class_v<T>) {
        // Тут гарантовано, що T є класом, тому звернення
        // до внутрішніх типів не зламає збірку для примітивних типів
        if constexpr (requires_custom_header_v<T>) {
            obj.send();
        } else {
            obj.write_raw();
        }
    } else {
        // Гілка для скалярних типів
    }
}
