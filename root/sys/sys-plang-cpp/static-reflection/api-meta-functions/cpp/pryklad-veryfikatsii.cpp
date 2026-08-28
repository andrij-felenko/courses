template <typename T>
consteval void verify_serializable() {
    constexpr auto type_info = ^^T;
    if (!std::meta::is_class(type_info)) {
        std::meta::report_error("Серіалізація підтримується лише для класів та структур");
    }

    for (auto field : std::meta::nonstatic_data_members_of(type_info)) {
        if (std::meta::is_private(field)) {
            std::meta::report_error("Клас містить приватні поля, що унеможливлює пряму серіалізацію");
        }
    }
}
