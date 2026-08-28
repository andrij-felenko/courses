namespace my_lib {
    namespace detail {
        // Низькопріоритетний фолбек для будь-яких типів, що підтримують std::ostream
        template<typename T>
        auto serialize_impl(const T& obj, std::ostream& os, long)
            -> decltype(os << obj, void())
        {
            os << obj;
        }

        // Високопріоритетне перевантаження, що активується за наявності користувацької serialize
        template<typename T>
        auto serialize_impl(const T& obj, std::ostream& os, int)
            -> decltype(serialize(os, obj), void()) 
        {
            serialize(os, obj); // Виклик користувацької функції через ADL
        }
    }

    // Публічний фасад бібліотеки
    template<typename T>
    void serialize(const T& obj, std::ostream& os) {
        using my_lib::detail::serialize_impl;
        serialize_impl(obj, os, 0); // int(0) віддає перевагу високопріоритетній гілці
    }
}
