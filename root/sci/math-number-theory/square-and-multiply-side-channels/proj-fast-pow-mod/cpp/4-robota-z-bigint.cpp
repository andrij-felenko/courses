class BigInt {
public:
    // ... імплементація конструкторів та зберігання даних ...
    
    BigInt operator*(const BigInt& other) const;
    BigInt operator%(const BigInt& mod) const;
    BigInt& operator>>=(size_t shift);
    bool is_odd() const;
    bool is_zero() const;
};

// Алгоритм виглядатиме ідентично завдяки перевантаженню
BigInt pow_mod_big(BigInt base, BigInt exponent, BigInt mod) {
    BigInt result = BigInt(1);
    base = base % mod;
    
    while (!exponent.is_zero()) {
        if (exponent.is_odd()) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exponent >>= 1;
    }
    return result;
}
