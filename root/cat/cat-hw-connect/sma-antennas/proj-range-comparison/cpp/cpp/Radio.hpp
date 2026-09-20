#ifndef RADIO_HPP
#define RADIO_HPP

#include <string>
#include <cstdint>

class Radio {
public:
    explicit Radio(const std::string& spi_device);
    ~Radio();

    // Забороняємо копіювання та переміщення для спрощення
    Radio(const Radio&) = delete;
    Radio& operator=(const Radio&) = delete;

    // Зчитування рівня сигналу (RSSI)
    int8_t getRssi() const;

private:
    int spi_fd;
};

#endif // RADIO_HPP
