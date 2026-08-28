#include <cwchar>
#include <clocale>

int std::wcscoll(const wchar_t *ws1, const wchar_t *ws2);
std::size_t std::wcsxfrm(wchar_t *dest, const wchar_t *src, std::size_t n);

extern "C" {
int wcscoll_l(const wchar_t *ws1, const wchar_t *ws2, locale_t loc);
size_t wcsxfrm_l(wchar_t *dest, const wchar_t *src, size_t n, locale_t loc);
}
