namespace std::meta {
    // Спеціальні функції-члени
    consteval auto is_constructor(info entity) -> bool;
    consteval auto is_destructor(info entity) -> bool;
    consteval auto is_copy_constructor(info entity) -> bool;
    consteval auto is_move_constructor(info entity) -> bool;
    consteval auto is_assignment_operator(info entity) -> bool;

    // Інспекція параметрів функцій
    consteval auto parameters_of(info function_entity) -> std::vector<info>;
    consteval auto return_type_of(info function_entity) -> info;
}
