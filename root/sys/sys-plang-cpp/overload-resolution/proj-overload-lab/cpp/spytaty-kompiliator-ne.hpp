#include <type_traits>

short       probe_s{};
float       probe_x{};
const char* probe_p{};

static_assert(std::is_same_v<decltype(f(42)),        AsInt>);
static_assert(std::is_same_v<decltype(f(probe_s)),   AsInt>);
static_assert(std::is_same_v<decltype(f(probe_x)),   AsDouble>);
static_assert(std::is_same_v<decltype(f(probe_p)),   AsBool>);
static_assert(std::is_same_v<decltype(f(Feet{1.0})), AsMeters>);
static_assert(std::is_same_v<decltype(f(Blob{})),    AsAny>);
