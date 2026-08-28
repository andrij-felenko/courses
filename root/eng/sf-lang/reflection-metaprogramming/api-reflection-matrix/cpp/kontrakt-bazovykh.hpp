namespace std::meta {
    // Перевірка категорій сутностей
    consteval bool is_type(info r);
    consteval bool is_variable(info r);
    consteval bool is_function(info r);
    consteval bool is_nonstatic_data_member(info r);

    // Отримання властивостей та метрик
    consteval string_view name_of(info r);
    consteval string_view display_name_of(info r);
    consteval info        type_of(info r);
    consteval size_t      offset_of(info r);
    consteval size_t      size_of(info r);
    consteval size_t      alignment_of(info r);

    // Дослідження структури та ієрархій
    consteval vector<info> members_of(info r);
    consteval vector<info> nonstatic_data_members_of(info r);
    consteval vector<info> bases_of(info r);
    consteval vector<info> enumerators_of(info r);

    // Генерація нових сутностей
    consteval info identifier(string_view name);
    consteval info substitute(info template_entity, span<const info> args);
}
