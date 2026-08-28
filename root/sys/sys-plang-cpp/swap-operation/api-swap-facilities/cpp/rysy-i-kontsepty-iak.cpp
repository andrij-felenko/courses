#include <concepts>
#include <type_traits>

namespace geo {
struct Path;
void swap(Path&, Path&) noexcept;
}

static_assert(std::is_swappable_v<geo::Path>);          // обмін узагалі можливий
static_assert(std::is_nothrow_swappable_v<geo::Path>);  // і він не кидає
static_assert(std::swappable<geo::Path>);               // те саме через ranges::swap
