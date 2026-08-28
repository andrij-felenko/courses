namespace std::meta {
    consteval auto is_static(info entity) -> bool;
    consteval auto is_virtual(info entity) -> bool;
    consteval auto is_pure_virtual(info entity) -> bool;
    consteval auto is_override(info entity) -> bool;
    consteval auto is_final(info entity) -> bool;
    consteval auto is_constexpr(info entity) -> bool;
    consteval auto is_consteval(info entity) -> bool;
    consteval auto is_noexcept(info entity) -> bool;
    consteval auto is_deleted(info entity) -> bool;
    consteval auto is_defaulted(info entity) -> bool;
    consteval auto is_explicit(info entity) -> bool;
    consteval auto is_inline(info entity) -> bool;
}
