namespace broken_design {

// Додано нове перевантаження первинного шаблону для довільних вказівників T*
template<typename T>
void serialize(BinaryBuffer& buf, T* ptr) {
    uint8_t has_value = (ptr != nullptr) ? 1 : 0;
    buf.write_raw(&has_value, sizeof(has_value));
    if (ptr != nullptr) {
        serialize(buf, *ptr); // Рекурсивний виклик для розіменованого об'єкта
    }
}

} // namespace broken_design
