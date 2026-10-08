#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <cstdint>

struct alignas(8) IioAccelSample {
    std::int16_t x;
    std::int16_t y;
    std::int16_t z;
    std::int16_t reserved;
    std::int64_t timestamp;
};

int main() {
    const char* dev_path = "/dev/iio:device0";
    int fd = ::open(dev_path, O_RDONLY);
    if (fd < 0) {
        std::cerr << "Помилка відкриття IIO пристрою: " << dev_path << '\n';
        return 1;
    }

    IioAccelSample sample{};
    std::cout << "Потокове зчитування пакетів даних IIO...\n";

    for (int i = 0; i < 10; ++i) {
        ssize_t res = ::read(fd, &sample, sizeof(sample));
        if (res != sizeof(sample)) {
            std::cerr << "Неповна вибірка або помилка читання\n";
            break;
        }
        std::cout << "Вибірка #" << i << " -> X: " << sample.x 
                  << " Y: " << sample.y << " Z: " << sample.z 
                  << " | Час: " << sample.timestamp << " нс\n";
    }

    ::close(fd);
    return 0;
}
