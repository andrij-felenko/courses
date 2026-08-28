namespace std::meta {
    // Отримання імен та ідентифікаторів
    consteval string_view name_of(info r);
    consteval string_view display_name_of(info r);
    consteval string_view identifier_of(info r);

    // Дослідження родоводу та типу сутності
    consteval info type_of(info r);
    consteval info parent_of(info r);

    // Отримання колекцій дочірніх сутностей
    consteval vector<info> members_of(info r);
    consteval vector<info> nonstatic_data_members_of(info r);
    consteval vector<info> static_data_members_of(info r);
    consteval vector<info> enumerators_of(info r);
    consteval vector<info> bases_of(info r);
    consteval vector<info> template_arguments_of(info r);

    // Предикати перевірки природи сутності
    consteval bool is_type(info r) noexcept;
    consteval bool is_variable(info r) noexcept;
    consteval bool is_function(info r) noexcept;
    consteval bool is_class(info r) noexcept;
    consteval bool is_enum(info r) noexcept;
    consteval bool is_public(info r) noexcept;
    consteval bool is_protected(info r) noexcept;
    consteval bool is_private(info r) noexcept;
    consteval bool is_virtual(info r) noexcept;
    consteval bool is_constexpr(info r) noexcept;
    consteval bool is_noexcept(info r) noexcept;

    // Синтез нових типів та маніпуляція шаблонами
    consteval info substitute(info tmpl, span<const info> args);
    consteval info reflect_value(auto value);
    template <typename T>
    consteval T extract(info r);
}
