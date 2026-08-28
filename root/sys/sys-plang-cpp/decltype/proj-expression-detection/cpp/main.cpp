#include <cstddef>
#include <deque>
#include <list>
#include <type_traits>
#include <utility>
#include <vector>
#include <cstdio>

template <class T, class = void>
struct has_reserve : std::false_type {};
template <class T>
struct has_reserve<T, std::void_t<decltype(std::declval<T&>().reserve(std::size_t{}))>>
    : std::true_type {};

template <class T, class = void>
struct has_size : std::false_type {};
template <class T>
struct has_size<T, std::void_t<decltype(std::declval<const T&>().size())>>
    : std::true_type {};

template <class T> inline constexpr bool has_reserve_v = has_reserve<T>::value;
template <class T> inline constexpr bool has_size_v    = has_size<T>::value;

template <class Dst, class Src>
void append_all(Dst& dst, const Src& src) {
    if constexpr (has_reserve_v<Dst> && has_size_v<Dst> && has_size_v<Src>)
        dst.reserve(dst.size() + src.size());          // цієї гілки для list просто немає
    dst.insert(dst.end(), src.begin(), src.end());
}

static_assert( has_reserve_v<std::vector<int>>);
static_assert(!has_reserve_v<std::list<int>>);
static_assert(!has_reserve_v<std::deque<int>>);        // deque має size(), але не reserve()
static_assert( has_size_v<std::list<int>>);

int main() {
    std::vector<int> v{1, 2, 3};
    std::list<int>   l{4, 5};
    append_all(v, l);                                   // reserve(5) — одна алокація
    append_all(l, v);                                   // гілка з reserve не інстанціюється
    std::printf("%zu %zu\n", v.size(), l.size());       // 5 7
}
