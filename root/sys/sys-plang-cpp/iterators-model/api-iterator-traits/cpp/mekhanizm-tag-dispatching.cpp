// Класичний Tag Dispatching у C++98/C++11
namespace detail {
    template<typename InputIt, typename Distance>
    void advance_impl(InputIt& it, Distance n, std::input_iterator_tag) {
        while (n > 0) { ++it; --n; }
    }

    template<typename RandomIt, typename Distance>
    void advance_impl(RandomIt& it, Distance n, std::random_access_iterator_tag) {
        it += n;
    }
}

template<typename It, typename Distance>
void advance(It& it, Distance n) {
    using category = typename std::iterator_traits<It>::iterator_category();
    detail::advance_impl(it, n, category{});
}
