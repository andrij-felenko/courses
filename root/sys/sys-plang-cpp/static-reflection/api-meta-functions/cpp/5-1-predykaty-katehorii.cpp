namespace std::meta {
    consteval auto is_type(info entity) -> bool;
    consteval auto is_variable(info entity) -> bool;
    consteval auto is_function(info entity) -> bool;
    consteval auto is_namespace(info entity) -> bool;
    consteval auto is_template(info entity) -> bool;
    consteval auto is_concept(info entity) -> bool;
    consteval auto is_enumerator(info entity) -> bool;
    consteval auto is_nonstatic_data_member(info entity) -> bool;
    consteval auto is_static_data_member(info entity) -> bool;
    consteval auto is_base(info entity) -> bool;
    consteval auto is_bit_field(info entity) -> bool;
}
