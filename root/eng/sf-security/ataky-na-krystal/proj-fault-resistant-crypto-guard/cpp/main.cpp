#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>
#include <type_traits>

namespace sec {

/* ── 1. Типізовані багатозначні токени безпеки ────────────────────── */
enum class Token : std::uint32_t {
    True  = 0x55AA55AAU,
    False = 0xAA55AA55U,
    Init  = 0x3C3C3C3CU,
    Panic = 0xFFFFFFFFU
};

enum class Canary : std::uint32_t {
    Init   = 0x6A09E667U,
    Stage1 = 0xBB67AE85U,
    Stage2 = 0x3C6EF372U
};

/* Допоміжні побітові оператори для канарейок */
[[nodiscard]] constexpr std::uint32_t to_underlying(Canary c) noexcept {
    return static_cast<std::uint32_t>(c);
}

[[nodiscard]] constexpr std::uint32_t to_underlying(Token t) noexcept {
    return static_cast<std::uint32_t>(t);
}

/* Бар'єр компілятора */
template <typename T>
inline void barrier(T& var) noexcept {
    asm volatile("" : "+r"(var) : : "memory");
}

/* ── 2. RAII-обгортка для гарантованого стирання секретів ───────── */
template <std::size_t N>
class SecureBuffer {
public:
    constexpr SecureBuffer() noexcept { data_.fill(0U); }
    explicit SecureBuffer(std::span<const std::uint8_t, N> src) noexcept {
        for (std::size_t i = 0; i < N; ++i) data_[i] = src[i];
    }

    ~SecureBuffer() noexcept {
        wipe();
    }

    SecureBuffer(const SecureBuffer&) = delete;
    SecureBuffer& operator=(const SecureBuffer&) = delete;
    SecureBuffer(SecureBuffer&&) noexcept = default;
    SecureBuffer& operator=(SecureBuffer&&) noexcept = default;

    [[nodiscard]] std::span<const std::uint8_t, N> span() const noexcept { return data_; }
    [[nodiscard]] std::span<std::uint8_t, N> span() noexcept { return data_; }

    void wipe() noexcept {
        volatile std::uint8_t* ptr = data_.data();
        for (std::size_t i = 0; i < N; ++i) {
            ptr[i] = 0U;
        }
        asm volatile("" : : "r"(data_.data()) : "memory");
    }

private:
    std::array<std::uint8_t, N> data_;
};

/* ── 3. Апаратна панічна пастка ─────────────────────────────────── */
[[noreturn]] inline void panic_trap() noexcept {
    asm volatile("cpsid i" : : : "memory");

    register std::uint32_t r0 asm("r0") = 0;
    register std::uint32_t r1 asm("r1") = 0;
    register std::uint32_t r2 asm("r2") = 0;
    register std::uint32_t r3 asm("r3") = 0;
    asm volatile("" : : "r"(r0), "r"(r1), "r"(r2), "r"(r3));

    while (true) {
        asm volatile("wfi");
    }
}

/* ── 4. Constant-Time верифікатор ────────────────────────────────── */
[[nodiscard]] inline Token constant_time_compare(std::span<const std::uint8_t> a,
                                                 std::span<const std::uint8_t> b) noexcept {
    if (a.size() != b.size() || a.empty()) {
        return Token::False;
    }

    volatile std::uint32_t diff_acc = 0U;
    const std::size_t len = a.size();

    for (std::size_t i = 0; i < len; ++i) {
        diff_acc |= (static_cast<std::uint32_t>(a[i]) ^ static_cast<std::uint32_t>(b[i]));
    }
    barrier(diff_acc);

    auto is_zero_mask = static_cast<std::uint32_t>(
        (static_cast<std::int32_t>(diff_acc | (0U - diff_acc))) >> 31
    );

    auto true_val  = to_underlying(Token::True);
    auto false_val = to_underlying(Token::False);
    auto raw_res   = (true_val & ~is_zero_mask) | (false_val & is_zero_mask);

    barrier(raw_res);
    return static_cast<Token>(raw_res);
}

/* ── 5. Програмний рандомізатор затримок ─────────────────────────── */
inline void delay_jitter(std::uint32_t entropy) noexcept {
    volatile std::uint32_t loops = (entropy & 0x3FU) + 16U;
    while (loops > 0U) {
        --loops;
        barrier(loops);
    }
}

/* ── 6. Захищений клас верифікатора підпису/MAC ─────────────────── */
class HardenedVerifier {
public:
    [[nodiscard]] static Token verify(std::span<const std::uint8_t> computed,
                                      std::span<const std::uint8_t> expected,
                                      std::uint32_t entropy) noexcept {
        volatile std::uint32_t canary = to_underlying(Canary::Init);
        volatile Token check1 = Token::Init;
        volatile Token check2 = Token::Init;

        /* Етап 1 */
        check1 = constant_time_compare(computed, expected);
        canary ^= to_underlying(Canary::Stage1);
        barrier(check1);
        barrier(canary);

        delay_jitter(entropy);

        /* Етап 2 */
        check2 = constant_time_compare(expected, computed);
        canary ^= to_underlying(Canary::Stage2);
        barrier(check2);
        barrier(canary);

        /* Контроль цілісності потоку виконання */
        const std::uint32_t target_canary = to_underlying(Canary::Init)
                                          ^ to_underlying(Canary::Stage1)
                                          ^ to_underlying(Canary::Stage2);
        if (canary != target_canary) {
            panic_trap();
        }

        /* Захищений подвійний перехід */
        if (check1 == Token::True && check2 == Token::True) {
            if (check1 != Token::True || check2 != Token::True) {
                panic_trap();
            }
            return Token::True;
        }

        if (check1 == Token::False || check2 == Token::False) {
            return Token::False;
        }

        panic_trap();
    }
};

} // namespace sec
