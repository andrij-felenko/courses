namespace trait_design {

// 1. Первинний шаблон структури серіалізатора
template<typename T, typename Enable = void>
struct SerializerTraits {
    static void write(BinaryBuffer& buf, const T& value) {
        static_assert(std::is_trivially_copyable_v<T>,
                      "Тип повинен бути trivially copyable або мати спеціалізацію SerializerTraits");
        
        // Для скалярних типів враховуємо порядок байтів
        if constexpr (std::is_integral_v<T> && sizeof(T) > 1) {
            // Перетворення до стандарту Big-Endian (мережевий порядок)
            T be_val = value;
            if constexpr (std::endian::native == std::endian::little) {
                be_val = std::byteswap(value);
            }
            buf.write_raw(&be_val, sizeof(T));
        } else {
            buf.write_raw(&value, sizeof(T));
        }
    }
};

// 2. Часткова спеціалізація для всіх вказівників T*
template<typename T>
struct SerializerTraits<T*> {
    static void write(BinaryBuffer& buf, const T* ptr) {
        uint8_t has_value = (ptr != nullptr) ? 1 : 0;
        buf.write_raw(&has_value, sizeof(has_value));
        if (ptr != nullptr) {
            SerializerTraits<T>::write(buf, *ptr);
        }
    }
};

// 3. Спеціалізація для рядків C-стилю const char*
template<>
struct SerializerTraits<const char*> {
    static void write(BinaryBuffer& buf, const char* str) {
        if (str == nullptr) {
            uint32_t zero_len = 0;
            buf.write_raw(&zero_len, sizeof(zero_len));
            return;
        }
        uint32_t len = static_cast<uint32_t>(std::strlen(str));
        buf.write_raw(&len, sizeof(len));
        buf.write_raw(str, len);
    }
};

// 4. Часткова спеціалізація для динамічних векторів std::vector<T>
template<typename T>
struct SerializerTraits<std::vector<T>> {
    static void write(BinaryBuffer& buf, const std::vector<T>& vec) {
        uint32_t count = static_cast<uint32_t>(vec.size());
        buf.write_raw(&count, sizeof(count));
        for (const auto& item : vec) {
            SerializerTraits<T>::write(buf, item);
        }
    }
};

// 5. Часткова спеціалізація для пар std::pair<T1, T2>
template<typename T1, typename T2>
struct SerializerTraits<std::pair<T1, T2>> {
    static void write(BinaryBuffer& buf, const std::pair<T1, T2>& pair) {
        SerializerTraits<T1>::write(buf, pair.first);
        SerializerTraits<T2>::write(buf, pair.second);
    }
};

// 6. Повна спеціалізація для рядків std::string
template<>
struct SerializerTraits<std::string> {
    static void write(BinaryBuffer& buf, const std::string& str) {
        uint32_t len = static_cast<uint32_t>(str.size());
        buf.write_raw(&len, sizeof(len));
        buf.write_raw(str.data(), len);
    }
};

// 7. ЄДИНА ПУБЛІЧНА ФУНКЦІЯ API (Ніколи не перевантажується і не спеціалізується!)
template<typename T>
void serialize(BinaryBuffer& buf, const T& value) {
    SerializerTraits<std::remove_cvref_t<T>>::write(buf, value);
}

} // namespace trait_design
