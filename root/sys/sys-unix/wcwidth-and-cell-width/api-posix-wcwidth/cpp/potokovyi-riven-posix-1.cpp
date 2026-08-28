#include <iostream>
#include <clocale>
#include <cwchar>
#include <locale.h>

// RAII-обгортка для безпечного перемикання потокової локалі в C++
class ThreadLocaleGuard {
public:
    explicit ThreadLocaleGuard(const char* locale_name) {
        loc_ = newlocale(LC_CTYPE_MASK, locale_name, nullptr);
        if (loc_) {
            old_loc_ = uselocale(loc_);
        }
    }

    ~ThreadLocaleGuard() {
        if (loc_) {
            uselocale(old_loc_);
            freelocale(loc_);
        }
    }

    ThreadLocaleGuard(const ThreadLocaleGuard&) = delete;
    ThreadLocaleGuard& operator=(const ThreadLocaleGuard&) = delete;

private:
    locale_t loc_{nullptr};
    locale_t old_loc_{nullptr};
};

int calculate_width_safe(wchar_t wc) {
    ThreadLocaleGuard guard("C.UTF-8");
    return wcwidth(wc);
}
