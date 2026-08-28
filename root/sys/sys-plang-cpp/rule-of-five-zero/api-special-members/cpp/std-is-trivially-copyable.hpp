#include <type_traits>

struct Probe {
    int a;
    Probe(const Probe&)            = delete;
    Probe& operator=(const Probe&) = delete;
    Probe(Probe&&)                 = default;
    Probe& operator=(Probe&&)      = default;
    // деструктор не оголошено — його згенерують тривіальним
};

static_assert(!std::is_copy_constructible_v<Probe>);
static_assert( std::is_trivially_move_constructible_v<Probe>);
static_assert( std::is_trivially_copyable_v<Probe>);   // ← видалені копії не заважають
static_assert( std::is_nothrow_move_constructible_v<Probe>);
