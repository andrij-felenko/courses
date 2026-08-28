// Концептуальна реалізація умовного деструктора у бібліотеці STL
template <typename T, bool = std::is_trivially_destructible_v<T>>
struct _Optional_destruct_base {
    // Нетривіальний деструктор для типів із власними ресурсами
    ~_Optional_destruct_base() {
        if (this->_M_has_value) {
            this->_M_payload.~T();
        }
    }
};

// Спеціалізація для тривіальних типів (int, double, просто структури)
template <typename T>
struct _Optional_destruct_base<T, true> {
    // Тривіальний деструктор за замовчуванням = default!
    ~_Optional_destruct_base() = default;
};
