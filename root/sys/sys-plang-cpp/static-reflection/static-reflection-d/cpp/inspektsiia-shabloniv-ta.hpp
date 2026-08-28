// Функція замінює тип елемента в довільному контейнері STL
consteval auto rebind_container_type(std::meta::info container_type, std::meta::info new_element_type) -> std::meta::info {
    auto primary_tmpl = std::meta::template_of(container_type);
    auto args = std::meta::template_arguments_of(container_type);
    args[0] = new_element_type; // підставляємо новий тип першого параметра
    return std::meta::substitute(primary_tmpl, args);
}

// Приклад використання
using OriginalList = std::vector<int>;
using ReboundList  = [: rebind_container_type(^^OriginalList, ^^double) :];
static_assert(std::same_as<ReboundList, std::vector<double>>);
