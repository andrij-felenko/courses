/* Ідіоматичний оптимізаційний бар'єр на C++ */
namespace bench {

template <typename T>
inline void do_not_optimize(T&& val) {
    #if defined(__clang__)
    asm volatile("" : "+r,m"(val) : : "memory");
    #else
    asm volatile("" : : "g"(val) : "memory");
    #endif
}

} // namespace bench
