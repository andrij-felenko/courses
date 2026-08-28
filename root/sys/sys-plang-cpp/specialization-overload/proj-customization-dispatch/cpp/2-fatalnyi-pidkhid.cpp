namespace broken_design {

// 1. Первинний шаблон серіалізатора для загальних типів
template<typename T>
void serialize(BinaryBuffer& buf, const T& value) {
    // За замовчуванням копіюємо як плоскі сирі байти
    buf.write_raw(&value, sizeof(T));
}

// 2. Спеціалізація для рядків std::string
template<>
inline void serialize<std::string>(BinaryBuffer& buf, const std::string& str) {
    uint32_t len = static_cast<uint32_t>(str.size());
    buf.write_raw(&len, sizeof(len));
    buf.write_raw(str.data(), len);
}

// 3. Спеціалізація для вказівників const char*
template<>
inline void serialize<const char*>(BinaryBuffer& buf, const char* const& str) {
    uint32_t len = static_cast<uint32_t>(std::strlen(str));
    buf.write_raw(&len, sizeof(len));
    buf.write_raw(str, len);
}

} // namespace broken_design
