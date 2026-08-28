namespace std::meta {
    // Параметри опису нового поля структури
    struct data_member_spec {
        info type;                          // дескриптор типу поля
        std::string_view name;              // ім'я поля
        size_t alignment = 0;               // вирівнювання (0 — стандартне)
        bool is_bitfield = false;           // чи є поле бітовим
        size_t bit_width = 0;               // ширина бітового поля
    };

    // Синтез нового типу класу на основі списку специфікаторів полів
    consteval auto define_class(std::span<const data_member_spec> members) -> info;
}
