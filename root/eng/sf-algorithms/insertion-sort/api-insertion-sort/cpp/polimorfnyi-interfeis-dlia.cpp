#include <cstddef>
#include <concepts>

// C++ сумісне оголошення функції з C-лінкуванням
extern "C" {
    void insertion_sort_generic(
        void *base,
        std::size_t nel,
        std::size_t width,
        int (*compar)(const void *, const void *)
    );
}
