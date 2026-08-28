#include <iterator>
#include <vector>
#include <list>
#include <forward_list>
#include <type_traits>

template<typename Iterator, typename Distance>
constexpr void generic_advance(Iterator& it, Distance n) {
    using Category = typename std::iterator_traits<Iterator>::iterator_category;

    if constexpr (std::is_base_of_v<std::random_access_iterator_tag, Category>) {
        // 1. Швидкий шлях прямого доступу O(1)
        it += n;
    } else if constexpr (std::is_base_of_v<std::bidirectional_iterator_tag, Category>) {
        // 2. Двосторонній прохід O(n)
        if (n > 0) {
            while (n--) ++it;
        } else {
            while (n++) --it;
        }
    } else {
        // 3. Односпрямований рух тільки вперед O(n)
        while (n--) {
            ++it;
        }
    }
}
