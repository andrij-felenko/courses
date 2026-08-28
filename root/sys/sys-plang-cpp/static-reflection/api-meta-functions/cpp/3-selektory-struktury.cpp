namespace std::meta {
    // Повний список усіх членів класу або простору назв
    consteval auto members_of(info type_or_ns) -> std::vector<info>;

    // Нестатичні поля даних екземпляра класу
    consteval auto nonstatic_data_members_of(info class_type) -> std::vector<info>;

    // Статичні змінні-члени класу
    consteval auto static_data_members_of(info class_type) -> std::vector<info>;

    // Усі функції-члени класу (методи, конструктори, деструктори, оператори)
    consteval auto member_functions_of(info class_type) -> std::vector<info>;

    // Вкладені типи (структури, класи, об'єднання, переліки, псевдоніми using)
    consteval auto member_types_of(info class_type) -> std::vector<info>;

    // Специфікатори безпосередніх базових класів
    consteval auto bases_of(info class_type) -> std::vector<info>;

    // Усі константи переліку (для enum та enum class)
    consteval auto enumerators_of(info enum_type) -> std::vector<info>;
}
