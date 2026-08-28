namespace std::meta {
    consteval auto is_class(info type) -> bool;
    consteval auto is_struct(info type) -> bool;
    consteval auto is_union(info type) -> bool;
    consteval auto is_enum(info type) -> bool;
    consteval auto is_scoped_enum(info type) -> bool;
    consteval auto is_complete_type(info type) -> bool;
    consteval auto is_abstract(info type) -> bool;
    consteval auto is_polymorphic(info type) -> bool;
    consteval auto is_aggregate(info type) -> bool;
    consteval auto is_trivial(info type) -> bool;
    consteval auto is_standard_layout(info type) -> bool;
    consteval auto is_empty_class(info type) -> bool;
}
