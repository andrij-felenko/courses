namespace std::meta {
    // Отримання всіх членів (поля, методи, типи, псевдоніми)
    consteval auto members_of(info type_or_ns) -> std::vector<info>;

    // Отримання лише нестатичних полів даних екземпляра
    consteval auto nonstatic_data_members_of(info class_type) -> std::vector<info>;

    // Отримання констант переліку
    consteval auto enumerators_of(info enum_type) -> std::vector<info>;

    // Отримання базових класів
    consteval auto bases_of(info class_type) -> std::vector<info>;
}
