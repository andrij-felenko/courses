consteval auto compute_struct_signature(std::meta::info type_info) -> uint64_t {
    uint64_t hash = 14695981039346656037ULL; // початкове значення FNV-1a
    constexpr uint64_t prime = 1099511628211ULL;

    auto update_hash = [&](std::string_view text) {
        for (char c : text) {
            hash ^= static_cast<uint8_t>(c);
            hash *= prime;
        }
    };

    // Враховуємо ім'я самої структури
    update_hash(std::meta::name_of(type_info));

    // Враховуємо імена та типи всіх нестатичних полів
    for (auto member : std::meta::nonstatic_data_members_of(type_info)) {
        update_hash(std::meta::name_of(member));
        update_hash(std::meta::display_name_of(std::meta::type_of(member)));
    }

    return hash;
}
