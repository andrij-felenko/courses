// Функція створює тип структури, що містить дзеркальні поля двох інших типів
consteval auto create_combined_struct(std::meta::info type_a, std::meta::info type_b) -> std::meta::info {
    std::vector<std::meta::data_member_spec> specs;

    for (auto f : std::meta::nonstatic_data_members_of(type_a)) {
        specs.push_back({
            .type = std::meta::type_of(f),
            .name = std::meta::name_of(f)
        });
    }
    for (auto f : std::meta::nonstatic_data_members_of(type_b)) {
        specs.push_back({
            .type = std::meta::type_of(f),
            .name = std::meta::name_of(f)
        });
    }

    return std::meta::define_class(specs);
}
