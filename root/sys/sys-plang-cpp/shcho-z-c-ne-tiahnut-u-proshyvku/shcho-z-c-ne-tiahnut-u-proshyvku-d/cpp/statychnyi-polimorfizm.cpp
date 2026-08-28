/* Базовий інтерфейс без віртуальних методів */
template <typename Derived>
class GpioDriver {
public:
    void set_high() noexcept {
        /* Приведення типів виконується на етапі компіляції */
        static_cast<Derived*>(this)->set_high_impl();
    }
};

/* Конкретна апаратна реалізація */
class Stm32GpioPin : public GpioDriver<Stm32GpioPin> {
public:
    explicit constexpr Stm32GpioPin(volatile uint32_t* bsrr, uint32_t pin_mask) noexcept
        : m_bsrr(bsrr), m_mask(pin_mask) {}

    /* Метод повністю інлайниться в пряму інструкцію STR */
    void set_high_impl() noexcept {
        *m_bsrr = m_mask;
    }

private:
    volatile uint32_t* m_bsrr;
    uint32_t m_mask;
};
