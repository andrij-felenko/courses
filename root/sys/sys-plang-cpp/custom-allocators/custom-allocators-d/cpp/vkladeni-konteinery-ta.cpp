#include <scoped_allocator>

template <typename T>
using ScopedArenaAlloc = std::scoped_allocator_adaptor<ArenaAllocator<T>>;

using ScopedString = std::basic_string<char, std::char_traits<char>, ArenaAllocator<char>>;
using ScopedVector = std::vector<ScopedString, ScopedArenaAlloc<ScopedString>>;

void test_scoped() {
    Arena arena(64 * 1024);
    ArenaAllocator<std::byte> byte_alloc(arena);
    ScopedArenaAlloc<ScopedString> alloc(byte_alloc);

    ScopedVector vec(alloc);
    // Тепер і буфер вектора, і буфери всіх рядків виділяються виключно в arena!
    vec.emplace_back("A very long text string that definitely exceeds Small String Optimization limit");
}
