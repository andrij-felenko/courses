#include <concepts>

namespace math::optimization {

template <typename Func>
requires std::invocable<Func, double> && 
         std::same_as<std::invoke_result_t<Func, double>, double>
SearchResult golden_section_search_concept(
    Func&& func, double a, double b, double eps = 1e-7);

} // namespace math::optimization
