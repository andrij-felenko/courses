#include <bitset>
#include <iostream>
#include <string_view>

// друк n молодших бітів v через std::bitset
template <std::size_t Bits>
static void pbits(std::string_view tag, std::uint16_t v) {
    std::cout << tag << std::bitset<Bits>(v) << '\n';
}

int main() {
    std::uint16_t msg  = 0x0Au;                 // дані 1010
    std::uint16_t code = encode(msg);           // → 1010011
    pbits<K>("дані      m = ", msg);
    pbits<N>("код       c = ", code);
    pbits<N>("код(LFSR) c = ", encode_lfsr(msg)); // та сама остача

    std::uint16_t recv = code ^ (1u << 4);      // внесемо одну помилку: розряд x⁴
    pbits<N>("прийнято  r = ", recv);
    pbits<R>("синдром   s = ", syndrome(recv));   // 110 ≠ 0

    if (auto fixed = decode(recv)) {
        pbits<N>("виправл.  c = ", *fixed);
        pbits<K>("відновл.  m = ", *fixed >> R);
        std::cout << "ok = 1\n";
    } else {
        std::cout << "ok = 0\n";
    }
}
