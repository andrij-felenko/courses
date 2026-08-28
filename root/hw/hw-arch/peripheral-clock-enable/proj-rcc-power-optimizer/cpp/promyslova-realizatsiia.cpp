#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <concepts>
#include <type_traits>
#include <utility>

// ── Строга типізація периферійних модулів ───────────────────────────────────
enum class periph_tag : std::uint8_t {
    gpioa = 0,
    gpiob,
    gpioc,
    dma1,
    dma2,
    usart1,
    usart2,
    i2c1,
    spi1,
    tim2,
    adc1,
    count
};

enum class bus_domain_tag : std::uint8_t {
    ahb1 = 0,
    ahb2,
    apb1,
    apb2,
    count
};

// ── Апаратні регістри для C++ середовища ──────────────────────────────────────
struct rcc_block_sim {
    volatile std::uint32_t ahb1enr{0};
    volatile std::uint32_t ahb2enr{0};
    volatile std::uint32_t apb1enr{0};
    volatile std::uint32_t apb2enr{0};
    volatile std::uint32_t ahb1lpenr{0};
    volatile std::uint32_t apb1lpenr{0};
    volatile std::uint32_t apb2lpenr{0};
    volatile std::uint32_t ahb1rstr{0};
    volatile std::uint32_t apb1rstr{0};
    volatile std::uint32_t apb2rstr{0};
};

// ── Метадані дескриптора модуля ──────────────────────────────────────────────
struct periph_descriptor {
    bus_domain_tag                   domain;
    volatile std::uint32_t* const    enr_reg;
    volatile std::uint32_t* const    lpenr_reg;
    volatile std::uint32_t* const    rstr_reg;
    const std::uint32_t              mask;
    const std::span<const periph_tag> dependencies;
    const std::uint32_t              current_ua;
};

// ── Клас диспетчера тактування C++20 ─────────────────────────────────────────
class modern_clock_manager {
public:
    static inline rcc_block_sim hw_rcc{};

private:
    static constexpr periph_tag usart1_deps[]{periph_tag::gpioa};
    static constexpr periph_tag usart2_deps[]{periph_tag::gpioa};
    static constexpr periph_tag i2c1_deps[]{periph_tag::gpiob};
    static constexpr periph_tag spi1_deps[]{periph_tag::gpioa, periph_tag::dma2};
    static constexpr periph_tag adc1_deps[]{periph_tag::gpioa};

    static inline const std::array<periph_descriptor, static_cast<std::size_t>(periph_tag::count)> descriptors_{{
        { bus_domain_tag::ahb1, &hw_rcc.ahb1enr, &hw_rcc.ahb1lpenr, &hw_rcc.ahb1rstr, (1U << 0), {}, 250 },
        { bus_domain_tag::ahb1, &hw_rcc.ahb1enr, &hw_rcc.ahb1lpenr, &hw_rcc.ahb1rstr, (1U << 1), {}, 250 },
        { bus_domain_tag::ahb1, &hw_rcc.ahb1enr, &hw_rcc.ahb1lpenr, &hw_rcc.ahb1rstr, (1U << 2), {}, 250 },
        { bus_domain_tag::ahb1, &hw_rcc.ahb1enr, &hw_rcc.ahb1lpenr, &hw_rcc.ahb1rstr, (1U << 21), {}, 1200 },
        { bus_domain_tag::ahb1, &hw_rcc.ahb1enr, &hw_rcc.ahb1lpenr, &hw_rcc.ahb1rstr, (1U << 22), {}, 1200 },
        { bus_domain_tag::apb2, &hw_rcc.apb2enr, &hw_rcc.apb2lpenr, &hw_rcc.apb2rstr, (1U << 4), usart1_deps, 850 },
        { bus_domain_tag::apb1, &hw_rcc.apb1enr, &hw_rcc.apb1lpenr, &hw_rcc.apb1rstr, (1U << 17), usart2_deps, 600 },
        { bus_domain_tag::apb1, &hw_rcc.apb1enr, &hw_rcc.apb1lpenr, &hw_rcc.apb1rstr, (1U << 21), i2c1_deps, 450 },
        { bus_domain_tag::apb2, &hw_rcc.apb2enr, &hw_rcc.apb2lpenr, &hw_rcc.apb2rstr, (1U << 12), spi1_deps, 1100 },
        { bus_domain_tag::apb1, &hw_rcc.apb1enr, &hw_rcc.apb1lpenr, &hw_rcc.apb1rstr, (1U << 0), {}, 700 },
        { bus_domain_tag::apb2, &hw_rcc.apb2enr, &hw_rcc.apb2lpenr, &hw_rcc.apb2rstr, (1U << 8), adc1_deps, 1800 },
    }};

    static inline std::array<std::uint16_t, static_cast<std::size_t>(periph_tag::count)> ref_counts_{};
    static inline std::array<std::uint16_t, static_cast<std::size_t>(bus_domain_tag::count)> domain_counts_{};

    static void sync_barrier(volatile std::uint32_t* reg) noexcept {
        [[maybe_unused]] volatile auto dummy = *reg;
        asm volatile("" ::: "memory");
    }

public:
    static bool acquire(periph_tag tag) noexcept {
        const auto idx = static_cast<std::size_t>(tag);
        if (idx >= descriptors_.size()) return false;

        const auto& desc = descriptors_[idx];

        // 1. Захоплення залежностей
        for (const auto dep : desc.dependencies) {
            if (!acquire(dep)) {
                // Відкат при невдачі
                for (const auto rollback : desc.dependencies) {
                    if (rollback == dep) break;
                    release(rollback);
                }
                return false;
            }
        }

        // 2. Увімкнення апаратури
        if (ref_counts_[idx] == 0) {
            *desc.enr_reg |= desc.mask;
            if (desc.lpenr_reg != nullptr) {
                *desc.lpenr_reg |= desc.mask;
            }
            sync_barrier(desc.enr_reg);
            ++domain_counts_[static_cast<std::size_t>(desc.domain)];
        }

        ++ref_counts_[idx];
        return true;
    }

    static bool release(periph_tag tag) noexcept {
        const auto idx = static_cast<std::size_t>(tag);
        if (idx >= descriptors_.size() || ref_counts_[idx] == 0) return false;

        --ref_counts_[idx];
        const auto& desc = descriptors_[idx];

        // Фізичне вимкнення
        if (ref_counts_[idx] == 0) {
            *desc.enr_reg &= ~desc.mask;
            if (desc.lpenr_reg != nullptr) {
                *desc.lpenr_reg &= ~desc.mask;
            }
            sync_barrier(desc.enr_reg);

            auto& d_count = domain_counts_[static_cast<std::size_t>(desc.domain)];
            if (d_count > 0) --d_count;
        }

        // Звільнення залежностей
        for (const auto dep : desc.dependencies) {
            release(dep);
        }

        return true;
    }

    static bool reset(periph_tag tag) noexcept {
        const auto idx = static_cast<std::size_t>(tag);
        if (idx >= descriptors_.size()) return false;

        const auto& desc = descriptors_[idx];
        if (desc.rstr_reg == nullptr) return false;

        *desc.rstr_reg |= desc.mask;
        sync_barrier(desc.rstr_reg);

        for (volatile int i = 0; i < 32; ++i) {
            asm volatile("nop");
        }

        *desc.rstr_reg &= ~desc.mask;
        sync_barrier(desc.rstr_reg);
        return true;
    }

    [[nodiscard]] static bool is_active(periph_tag tag) noexcept {
        const auto idx = static_cast<std::size_t>(tag);
        return (idx < ref_counts_.size()) && (ref_counts_[idx] > 0);
    }

    [[nodiscard]] static std::uint16_t bus_active_count(bus_domain_tag domain) noexcept {
        const auto idx = static_cast<std::size_t>(domain);
        return (idx < domain_counts_.size()) ? domain_counts_[idx] : 0;
    }
};

// ── RAII-вартовий тактування модуля ─────────────────────────────────────────
template <periph_tag Tag>
class peripheral_clock_guard {
private:
    bool active_{false};

public:
    peripheral_clock_guard() noexcept : active_(modern_clock_manager::acquire(Tag)) {}

    ~peripheral_clock_guard() noexcept {
        if (active_) {
            modern_clock_manager::release(Tag);
        }
    }

    peripheral_clock_guard(const peripheral_clock_guard&) = delete;
    peripheral_clock_guard& operator=(const peripheral_clock_guard&) = delete;

    peripheral_clock_guard(peripheral_clock_guard&& other) noexcept : active_(other.active_) {
        other.active_ = false;
    }

    peripheral_clock_guard& operator=(peripheral_clock_guard&& other) noexcept {
        if (this != &other) {
            if (active_) modern_clock_manager::release(Tag);
            active_ = other.active_;
            other.active_ = false;
        }
        return *this;
    }

    [[nodiscard]] explicit operator bool() const noexcept { return active_; }
    [[nodiscard]] bool is_valid() const noexcept { return active_; }
};
