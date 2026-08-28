#include <linux/gpio/consumer.h>
#include <cstdint>

// C++ RAII-обгортка над масивом дескрипторів GPIO у ядрі
class KernelGpioBus {
public:
    KernelGpioBus(struct device* dev, const char* name) {
        descs_ = devm_gpiod_get_array(dev, name, GPIOD_OUT_LOW);
    }

    [[nodiscard]] bool valid() const noexcept {
        return descs_ && !IS_ERR(descs_);
    }

    void write_mask(std::uint64_t value) noexcept {
        if (valid()) {
            unsigned long val = value;
            gpiod_set_array_value(descs_->ndescs, descs_->desc, descs_->info, &val);
        }
    }

private:
    struct gpio_descs* descs_{nullptr};
};
