#include <cstdint>
#include <utility>
#include <concepts>

enum class periph_id : std::uint8_t {
    gpioa = 0,
    gpiob,
    usart1,
    usart2,
    i2c1,
    spi1,
    count
};

struct periph_descriptor {
    volatile std::uint32_t* const enr_register;
    const std::uint32_t           enable_mask;
    std::uint8_t                  reference_count{0};
};

class clock_manager {
private:
    static inline std::uint32_t sim_ahb1enr{0};
    static inline std::uint32_t sim_apb1enr{0};
    static inline std::uint32_t sim_apb2enr{0};

    static inline periph_descriptor registry_[static_cast<std::size_t>(periph_id::count)] = {
        { &sim_ahb1enr, (1U << 0),  0 },
        { &sim_ahb1enr, (1U << 1),  0 },
        { &sim_apb2enr, (1U << 4),  0 },
        { &sim_apb1enr, (1U << 17), 0 },
        { &sim_apb1enr, (1U << 21), 0 },
        { &sim_apb2enr, (1U << 12), 0 },
    };

public:
    static bool acquire(periph_id id) noexcept {
        const auto idx = static_cast<std::size_t>(id);
        if (idx >= static_cast<std::size_t>(periph_id::count)) return false;

        auto& desc = registry_[idx];
        if (desc.reference_count == 0) {
            *desc.enr_register |= desc.enable_mask;
            // Фіктивне читання для безпеки шини
            [[maybe_unused]] volatile auto barrier = *desc.enr_register;
        }
        ++desc.reference_count;
        return true;
    }

    static bool release(periph_id id) noexcept {
        const auto idx = static_cast<std::size_t>(id);
        if (idx >= static_cast<std::size_t>(periph_id::count)) return false;

        auto& desc = registry_[idx];
        if (desc.reference_count == 0) return false;

        --desc.reference_count;
        if (desc.reference_count == 0) {
            *desc.enr_register &= ~desc.enable_mask;
            [[maybe_unused]] volatile auto barrier = *desc.enr_register;
        }
        return true;
    }

    static bool is_active(periph_id id) noexcept {
        const auto idx = static_cast<std::size_t>(id);
        return registry_[idx].reference_count > 0;
    }
};

// RAII-вартовий тактування периферійного блоку
class scoped_peripheral_clock {
private:
    periph_id id_;
    bool      engaged_{false};

public:
    explicit scoped_peripheral_clock(periph_id id) noexcept
        : id_(id), engaged_(clock_manager::acquire(id)) {}

    ~scoped_peripheral_clock() noexcept {
        if (engaged_) {
            clock_manager::release(id_);
        }
    }

    // Заборона копіювання для запобігання подвійному звільненню
    scoped_peripheral_clock(const scoped_peripheral_clock&) = delete;
    scoped_peripheral_clock& operator=(const scoped_peripheral_clock&) = delete;

    // Дозвіл переміщення
    scoped_peripheral_clock(scoped_peripheral_clock&& other) noexcept
        : id_(other.id_), engaged_(other.engaged_) {
        other.engaged_ = false;
    }

    scoped_peripheral_clock& operator=(scoped_peripheral_clock&& other) noexcept {
        if (this != &other) {
            if (engaged_) clock_manager::release(id_);
            id_ = other.id_;
            engaged_ = other.engaged_;
            other.engaged_ = false;
        }
        return *this;
    }

    [[nodiscard]] bool is_engaged() const noexcept { return engaged_; }
};
