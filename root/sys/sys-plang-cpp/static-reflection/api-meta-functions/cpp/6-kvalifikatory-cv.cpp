namespace std::meta {
    // Предикати перевірки кваліфікаторів
    consteval auto is_const(info type) -> bool;
    consteval auto is_volatile(info type) -> bool;
    consteval auto is_lvalue_reference(info type) -> bool;
    consteval auto is_rvalue_reference(info type) -> bool;
    consteval auto is_pointer(info type) -> bool;
    consteval auto is_array(info type) -> bool;

    // Трансформації кваліфікаторів типу
    consteval auto remove_cv(info type) -> info;
    consteval auto remove_reference(info type) -> info;
    consteval auto remove_cvref(info type) -> info;
    consteval auto add_lvalue_reference(info type) -> info;
    consteval auto add_rvalue_reference(info type) -> info;
    consteval auto add_pointer(info type) -> info;
    consteval auto remove_pointer(info type) -> info;
}
