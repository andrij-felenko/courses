#include <iostream>
#include <memory>
#include <stdexcept>
#include <iio.h>

class IioContextWrapper {
    struct iio_context* ctx;
public:
    IioContextWrapper() {
        ctx = iio_create_default_context();
        if (!ctx) throw std::runtime_error("Не вдалося створити IIO контекст");
    }
    ~IioContextWrapper() {
        if (ctx) iio_context_destroy(ctx);
    }
    struct iio_context* get() const { return ctx; }
};

int main() {
    try {
        IioContextWrapper ctx;
        struct iio_device* dev = iio_context_find_device(ctx.get(), "iio:device0");
        if (!dev) {
            throw std::runtime_error("Пристрій iio:device0 не знайдено");
        }

        struct iio_channel* accel_x = iio_device_find_channel(dev, "accel_x", false);
        if (accel_x) iio_channel_enable(accel_x);

        struct iio_buffer* buf = iio_device_create_buffer(dev, 512, false);
        if (!buf) {
            throw std::runtime_error("Помилка створення об'єкта iio_buffer");
        }

        std::cout << "Успішна ініціалізація C++ обгортки libiio.\n";
        ssize_t bytes = iio_buffer_refill(buf);
        std::cout << "Прочитано байтів з кільцевого буфера: " << bytes << '\n';

        iio_buffer_destroy(buf);
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
