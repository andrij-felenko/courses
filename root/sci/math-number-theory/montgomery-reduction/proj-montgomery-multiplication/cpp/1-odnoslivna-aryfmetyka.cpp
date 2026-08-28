#include <cstdint>
#include <optional>
#include <iostream>
#include <concepts>

// Клас контексту та арифметики Монтгомері в сучасному стилі C++20
class Montgomery64 {
public:
    // Фабричний метод для безпечної ініціалізації непарним модулем
    static std::optional<Montgomery64> create(uint64_t modulus) noexcept {
        if ((modulus & 1) == 0 || modulus <= 1) {
            return std::nullopt; // Модуль зобов'язаний бути непарним
        }
        return Montgomery64(modulus);
    }

    [[nodiscard]] constexpr uint64_t modulus() const noexcept { return n_; }
    [[nodiscard]] constexpr uint64_t n_prime() const noexcept { return n_prime_; }
    [[nodiscard]] constexpr uint64_t r_mod_n() const noexcept { return r_mod_n_; }

    // Переведення в простір Монтгомері: a -> a * R mod N
    [[nodiscard]] uint64_t to_domain(uint64_t a) const noexcept {
        return redc(static_cast<unsigned __int128>(a) * r2_mod_n_);
    }

    // Повернення з простору Монтгомері: a_bar -> a
    [[nodiscard]] uint64_t from_domain(uint64_t a_bar) const noexcept {
        return redc(static_cast<unsigned __int128>(a_bar));
    }

    // Множення двох чисел у просторі Монтгомері
    [[nodiscard]] uint64_t multiply(uint64_t a_bar, uint64_t b_bar) const noexcept {
        return redc(static_cast<unsigned __int128>(a_bar) * b_bar);
    }

    // Редукція Монтгомері (REDC)
    [[nodiscard]] uint64_t redc(unsigned __int128 T) const noexcept {
        const auto t_low = static_cast<uint64_t>(T);
        const uint64_t m = t_low * n_prime_;
        
        const unsigned __int128 mn = static_cast<unsigned __int128>(m) * n_;
        const unsigned __int128 sum = T + mn;
        
        auto t = static_cast<uint64_t>(sum >> 64);
        if (t >= n_) {
            t -= n_;
        }
        return t;
    }

private:
    explicit Montgomery64(uint64_t n) noexcept : n_(n) {
        n_prime_ = compute_nprime(n);
        
        const unsigned __int128 r = static_cast<unsigned __int128>(1) << 64;
        r_mod_n_ = static_cast<uint64_t>(r % n);
        
        const unsigned __int128 r2 = (r % n) * (r % n);
        r2_mod_n_ = static_cast<uint64_t>(r2 % n);
    }

    // Обчислення n' методом піднесення Гензеля
    static constexpr uint64_t compute_nprime(uint64_t n) noexcept {
        uint64_t x = 1;
        for (int i = 0; i < 6; ++i) {
            x = x * (2 - n * x);
        }
        return -x;
    }

    uint64_t n_{0};
    uint64_t n_prime_{0};
    uint64_t r_mod_n_{0};
    uint64_t r2_mod_n_{0};
};
