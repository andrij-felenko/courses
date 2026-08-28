namespace std::meta {
    // Інстанціювання первинного шаблону переданим списком дескрипторів аргументів
    consteval auto substitute(info template_entity, std::span<const info> args) -> info;

    // Отримання дескриптора первинного шаблону для інстанційованого типу
    consteval auto template_of(info instantiated_type) -> info;

    // Отримання списку аргументів шаблону для інстанційованого типу
    consteval auto template_arguments_of(info instantiated_type) -> std::vector<info>;

    // Зняття шарів псевдонімів using та typedef до вихідного типу
    consteval auto dealias(info entity) -> info;

    // Перетворення значення часу компіляції у дескриптор info
    template <typename T>
    consteval auto reflect_value(const T& value) -> info;

    // Вилучення типізованого значення з дескриптора константи
    template <typename T>
    consteval auto extract(info value_entity) -> T;

    // Перевірка, чи несе дескриптор дійсне константне значення
    consteval auto has_value(info entity) -> bool;

    // Геометричні параметри пам'яті (розмір, вирівнювання, зміщення в байтах)
    consteval auto size_of(info type_entity) -> size_t;
    consteval auto alignment_of(info type_entity) -> size_t;
    consteval auto offset_of(info member_entity) -> size_t;
    consteval auto bit_size_of(info bitfield_entity) -> size_t;
}
