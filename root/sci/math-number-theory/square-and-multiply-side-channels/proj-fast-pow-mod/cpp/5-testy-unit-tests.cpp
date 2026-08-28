#include <iostream>
#include <cassert>

using namespace MathLib;

void test_pow_mod() {
    // 3^13 mod 17 = 12
    assert(pow_mod<uint64_t>(3, 13, 17) == 12);
    
    // 2^10 mod 1000 = 24
    assert(pow_mod<uint64_t>(2, 10, 1000) == 24);
    
    // 5^0 mod 7 = 1
    assert(pow_mod<uint64_t>(5, 0, 7) == 1);
    
    // Великі числа (менше 64 біт, але легко переповнюються без __uint128_t)
    uint64_t large_base = 1000000007;
    uint64_t large_exp = 999999999;
    uint64_t mod = 1000000009;
    assert(pow_mod<uint64_t>(large_base, large_exp, mod) > 0);
    
    std::cout << "All pow_mod tests passed!" << std::endl;
}

int main() {
    test_pow_mod();
    return 0;
}
