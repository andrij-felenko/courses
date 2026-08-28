struct Plain  { Buffer buf; };                       // нічого зайвого
struct Frame  { const Buffer buf; int id = 0; };     // константне поле
struct Holder { Buffer buf; ~Holder() {} };          // власний деструктор

static_assert( std::is_nothrow_move_constructible_v<Plain>);
static_assert( std::is_move_constructible_v<Holder>);          // «так» — але це копіювання
static_assert(!std::is_nothrow_move_constructible_v<Holder>);  // ось де правда
static_assert(!std::is_nothrow_move_constructible_v<Frame>);

void demo_traps() {
    { Plain  a{Buffer(1u << 20)}; Stats m = g; Plain  b = std::move(a); report("Plain                ", m); }
    { Frame  a{Buffer(1u << 20)}; Stats m = g; Frame  b = std::move(a); report("Frame  (const-поле)  ", m); }
    { Holder a{Buffer(1u << 20)}; Stats m = g; Holder b = std::move(a); report("Holder (свій ~Holder)", m); }
}
