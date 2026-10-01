#ifndef ESP_FLASHER_HPP
#define ESP_FLASHER_HPP

#include <string>
#include <vector>
#include <cstdint>
#include <memory>
#include <chrono>

#if defined(_WIN32)
#include <windows.h>
#else
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <sys/ioctl.h>
#endif

// Клас для автоматизованого флешування ESP8266 через послідовний порт
class EspFlasher {
public:
    EspFlasher(const std::string& port_name, uint32_t baud_rate = 115200);
    ~EspFlasher();

    // Заборона копіювання через RAII-управління системним дескриптором
    EspFlasher(const EspFlasher&) = delete;
    EspFlasher& operator=(const EspFlasher&) = delete;

    bool open_port();
    void close_port();

    // Апаратне автоскидання в режим UART Download Mode за допомогою ліній DTR та RTS
    bool reset_to_bootloader();

    // Синхронізація (рукостискання) з ROM Bootloader ESP8266
    bool sync_bootloader(int max_attempts = 10);

    // Поблочний запис двійкового образу прошивки у Flash-пам'ять
    bool write_flash(uint32_t address, const std::vector<uint8_t>& data, uint32_t block_size = 1024);

private:
    std::string port_name_;
    uint32_t baud_rate_;
    
#if defined(_WIN32)
    HANDLE handle_ = INVALID_HANDLE_VALUE;
#else
    int fd_ = -1;
#endif

    void set_dtr(bool state);
    void set_rts(bool state);
    bool write_raw(const uint8_t* data, size_t size);
    bool read_raw(uint8_t* buffer, size_t size, uint32_t timeout_ms = 1000);
    
    // Формування SLIP-пакета для протоколу esptool
    std::vector<uint8_t> make_command_packet(uint8_t op, const std::vector<uint8_t>& payload, uint32_t checksum = 0);
};

#endif // ESP_FLASHER_HPP
