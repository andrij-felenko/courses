#include <cstdint>
#include <cstddef>
#include <span>

#if defined(USE_VALGRIND_CTGRIND)
#include <valgrind/memcheck.h>
#endif

namespace crypto::analysis {

/* Обгортка для позначення конфіденційної пам'яті в середовищі Valgrind */
inline void poison_secret(const void *addr, size_t len) noexcept {
    #if defined(USE_VALGRIND_CTGRIND)
    VALGRIND_MAKE_MEM_UNDEFINED(addr, len);
    #else
    (void)addr; (void)len;
    #endif
}

inline void unpoison_public(const void *addr, size_t len) noexcept {
    #if defined(USE_VALGRIND_CTGRIND)
    VALGRIND_MAKE_MEM_DEFINED(addr, len);
    #else
    (void)addr; (void)len;
    #endif
}

template <typename T>
void poison_object(T &obj) noexcept {
    poison_secret(&obj, sizeof(T));
}

template <typename T>
void unpoison_object(T &obj) noexcept {
    unpoison_public(&obj, sizeof(T));
}

} // namespace crypto::analysis
