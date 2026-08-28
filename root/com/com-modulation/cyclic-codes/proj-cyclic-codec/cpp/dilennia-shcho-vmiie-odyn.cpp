#include <cstdint>

// остача word mod g(x): ділення XOR-зсувами.
// word — до N бітів; g має степінь R (старший біт g стоїть у розряді R).
constexpr std::uint16_t poly_rem(std::uint16_t word) {
    for (int i = N - 1; i >= R; --i)      // від старшого біта вниз до розряду R
        if (word & (1u << i))             // провідний член ще стирчить?
            word ^= (G << (i - R));       // відняти g, вирівняний під xⁱ
    return word & ((1u << R) - 1);        // лишилась остача степеня < R
}
