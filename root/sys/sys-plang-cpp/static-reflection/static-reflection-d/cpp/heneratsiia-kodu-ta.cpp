// Динамічне створення структури, яка містить лише числові поля вихідного класу
consteval auto make_numeric_subset(std::meta::info source_type) -> std::meta::info {
    std::vector<std::meta::data_member_spec> specs;

    for (auto f : std::meta::nonstatic_data_members_of(source_type)) {
        auto field_type = std::meta::type_of(f);
        if (field_type == ^^int || field_type == ^^double || field_type == ^^float) {
            specs.push_back({
                .type = field_type,
                .name = std::meta::name_of(f)
            });
        }
    }

    return std::meta::define_class(specs);
}
