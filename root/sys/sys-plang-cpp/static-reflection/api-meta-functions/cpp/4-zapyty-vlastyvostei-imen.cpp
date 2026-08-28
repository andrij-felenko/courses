namespace std::meta {
    // Базове некваліфіковане ім'я сутності (наприклад, "login" або "vector")
    consteval auto name_of(info entity) -> std::string_view;

    // Символьний ідентифікатор мови (повертає порожній рядок для безіменних сутностей)
    consteval auto identifier_of(info entity) -> std::string_view;

    // Повне форматоване найменування з просторами назв та шаблонними параметрами
    consteval auto display_name_of(info entity) -> std::string_view;

    // Тип сутності (для змінних, полів даних, параметрів, функцій)
    consteval auto type_of(info entity) -> info;

    // Батьківська область видимості (клас або простір назв, у якому оголошено сутність)
    consteval auto parent_of(info entity) -> info;

    // Базовий цілочисельний тип переліку (підлеглий тип для enum)
    consteval auto underlying_type_of(info enum_type) -> info;

    // Точні координати оголошення сутності у файлі коду
    consteval auto source_location_of(info entity) -> std::source_location;
}
