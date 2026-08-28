#include <linux/gpio/consumer.h>
#include <utility>

// Ідіоматична C++ RAII-обгортка навколо ядерного дескриптора gpio_desc
// Для використання у вбудованих системах та підсистемах ядра з C++ фреймворками
class KernelGpioDescriptor {
public:
    explicit KernelGpioDescriptor(struct gpio_desc* desc = nullptr) noexcept
        : desc_(desc) {}

    ~KernelGpioDescriptor() {
        if (desc_) {
            gpiod_put(desc_);
        }
    }

    KernelGpioDescriptor(const KernelGpioDescriptor&) = delete;
    KernelGpioDescriptor& operator=(const KernelGpioDescriptor&) = delete;

    KernelGpioDescriptor(KernelGpioDescriptor&& other) noexcept
        : desc_(std::exchange(other.desc_, nullptr)) {}

    KernelGpioDescriptor& operator=(KernelGpioDescriptor&& other) noexcept {
        if (this != &other) {
            if (desc_) gpiod_put(desc_);
            desc_ = std::exchange(other.desc_, nullptr);
        }
        return *this;
    }

    void set_value(int value) noexcept {
        if (desc_) {
            gpiod_set_value(desc_, value);
        }
    }

    [[nodiscard]] int get_value() const noexcept {
        return desc_ ? gpiod_get_value(desc_) : -1;
    }

    [[nodiscard]] bool valid() const noexcept {
        return desc_ && !IS_ERR(desc_);
    }

private:
    struct gpio_desc* desc_{nullptr};
};
