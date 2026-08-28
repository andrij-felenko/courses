#include <bit>
#include <cstdint>
#include <optional>

// виправлення однієї помилки методом error-trapping.
// Повертає std::optional з виправленим словом або std::nullopt при понад 1 помилці.
constexpr std::optional<std::uint16_t> decode(std::uint16_t recv) {
    std::uint16_t s = syndrome(recv);
    if (s == 0) return recv;                      // синдром нульовий — слово ціле

    std::uint16_t w = recv;
    for (int j = 0; j < N; ++j) {
        if (std::popcount(s) <= 1) {              // помилка у перевірних розрядах
            w ^= s;                               // синдром і є помилковий біт
            for (int back = 0; back < j; ++back)
                w = rotr(w);
            return w;
        }
        w = rotl(w);                              // крутимо слово по колу
        s <<= 1;                                  // синдром * x mod g:
        if (s & (1u << R)) s ^= G;                // відняти g при виході за R
    }
    return std::nullopt;                          // понад 1 помилка
}
