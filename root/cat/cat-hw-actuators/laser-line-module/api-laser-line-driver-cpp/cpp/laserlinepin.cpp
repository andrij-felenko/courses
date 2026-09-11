#include <cstdint>

/* Клас апаратного керування виводом лазера за принципом RAII */
class LaserLinePin {
public:
    enum class ActiveLevel : uint8_t {
        Low = 0,    // Активний логічний нуль (P-MOSFET / PNP)
        High = 1    // Активна логічна одиниця (N-MOSFET / NPN)
    };

    struct Registers {
        volatile uint32_t MODER;
        volatile uint32_t OTYPER;
        volatile uint32_t OSPEEDR;
        volatile uint32_t PUPDR;
        volatile uint32_t IDR;
        volatile uint32_t ODR;
        volatile uint32_t BSRR;
        volatile uint32_t LCKR;
        volatile uint32_t AFR[2];
    };

    LaserLinePin(Registers* port, uint8_t pin, ActiveLevel level)
        : port_(port), pin_(pin), level_(level) {}

    /**
     * @brief Безглітчева конфігурація виводу.
     * Гарантує вимкнений стан випромінювача при переході з Hi-Z у вихід.
     */
    void init_safe() {
        if (!port_ || pin_ > 15) {
            return;
        }

        // 1. Конфігурація апаратного стягування/підтяжки під час переходу
        port_->PUPDR &= ~(0x3U << (pin_ * 2));
        if (level_ == ActiveLevel::High) {
            port_->PUPDR |= (0x2U << (pin_ * 2)); // Pull-down
        } else {
            port_->PUPDR |= (0x1U << (pin_ * 2)); // Pull-up
        }

        // 2. Безпечний попередній запис неактивного стану ДО зміни напрямку
        force_safe_level();

        // 3. Двотактний каскад (push-pull)
        port_->OTYPER &= ~(1U << pin_);

        // 4. Висока швидкодія фронтів
        port_->OSPEEDR &= ~(0x3U << (pin_ * 2));
        port_->OSPEEDR |= (0x2U << (pin_ * 2));

        // 5. Перемикання в режим виводу (01b)
        port_->MODER &= ~(0x3U << (pin_ * 2));
        port_->MODER |= (0x1U << (pin_ * 2));
    }

    /**
     * @brief Увімкнення або вимкнення генерації світла.
     */
    void set_emission(bool enabled) {
        if (!port_) {
            return;
        }

        bool drive_high = (level_ == ActiveLevel::High) ? enabled : !enabled;
        if (drive_high) {
            port_->BSRR = (1U << pin_);
        } else {
            port_->BSRR = (1U << (pin_ + 16));
        }
    }

    /**
     * @brief Аварійне вимкнення у деструкторі.
     */
    ~LaserLinePin() {
        force_safe_level();
    }

private:
    Registers* port_;
    uint8_t pin_;
    ActiveLevel level_;

    void force_safe_level() {
        if (level_ == ActiveLevel::High) {
            port_->BSRR = (1U << (pin_ + 16)); // Примусовий 0 В
        } else {
            port_->BSRR = (1U << pin_);        // Примусовий VDD
        }
    }
};
