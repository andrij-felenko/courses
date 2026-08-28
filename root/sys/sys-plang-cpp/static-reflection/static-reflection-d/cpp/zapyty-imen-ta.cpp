namespace std::meta {
    // Символьне ім'я сутності без простору назв
    consteval auto name_of(info entity) -> std::string_view;

    // Дескриптор типу змінної, поля або функції
    consteval auto type_of(info entity) -> info;

    // Предикати класифікації
    consteval auto is_public(info member) -> bool;
    consteval auto is_private(info member) -> bool;
    consteval auto is_static(info entity) -> bool;
    consteval auto is_enum(info type) -> bool;
    consteval auto is_class(info type) -> bool;
    consteval auto is_complete_type(info type) -> bool;

    // Зняття шарів псевдонімів using та typedef до канонічного типу
    consteval auto dealias(info entity) -> info;
}
