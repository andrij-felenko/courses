// Зчитування вибірок IIO через libiio (C++)
#include <iostream>
#include <memory>
#include <stdexcept>
#include <iio.h>

class IIOReader {
public:
    IIOReader(const std::string& dev_name) {
        ctx_ = iio_create_local_context();
        if (!ctx_) {
            throw std::runtime_error("Не вдалося створити контекст IIO");
        }

        dev_ = iio_context_find_device(ctx_, dev_name.c_str());
        if (!dev_) {
            iio_context_destroy(ctx_);
            throw std::runtime_error("Пристрій IIO не знайдено");
        }
    }

    ~IIOReader() {
        if (buf_) iio_buffer_destroy(buf_);
        if (ctx_) iio_context_destroy(ctx_);
    }

    void start_streaming(size_t samples) {
        struct iio_channel* ch = iio_device_find_channel(dev_, "accel_x", false);
        if (ch) iio_channel_enable(ch);

        buf_ = iio_device_create_buffer(dev_, samples, false);
        if (!buf_) {
            throw std::runtime_error("Помилка створення буфера IIO");
        }

        ssize_t bytes = iio_buffer_refill(buf_);
        std::cout << "Отримано " << bytes << " байт вимірів з давача." << std::endl;
    }

private:
    struct iio_context* ctx_{nullptr};
    struct iio_device* dev_{nullptr};
    struct iio_buffer* buf_{nullptr};
};

int main() {
    try {
        IIOReader reader("mpu6050");
        reader.start_streaming(1024);
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
