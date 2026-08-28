// Історична репродукція ідеї Ервіна Унруха (1994)
template <int i> struct is_prime;
template <int p, int d> struct is_prime_helper {
    static constexpr bool value = (p % d != 0) && is_prime_helper<p, d - 1>::value;
};
template <int p> struct is_prime_helper<p, 2> {
    static constexpr bool value = (p % 2 != 0);
};
template <int i> struct Prime_print {
    Prime_print<i - 1> a;
    enum { is_p = is_prime_helper<i, i - 1>::value };
    // Якщо число просте, створюється помилка типу, яка виводить 'i' в терміналі!
    void f() { struct Dummy { Dummy(int); } d = is_p ? i : 0; }
};
