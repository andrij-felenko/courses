consteval auto get_all_fields_recursive(std::meta::info class_info) -> std::vector<std::meta::info> {
    std::vector<std::meta::info> all_fields;

    // Рекурсивний збір полів батьківських класів
    for (auto base_spec : std::meta::bases_of(class_info)) {
        auto base_type = std::meta::type_of(base_spec);
        auto base_fields = get_all_fields_recursive(base_type);
        all_fields.insert(all_fields.end(), base_fields.begin(), base_fields.end());
    }

    // Додавання власних нестатичних полів
    auto local_fields = std::meta::nonstatic_data_members_of(class_info);
    all_fields.insert(all_fields.end(), local_fields.begin(), local_fields.end());

    return all_fields;
}
