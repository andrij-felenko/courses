#ifndef CH340_AUTORESET_HPP
#define CH340_AUTORESET_HPP

#include <string>
#include <string_view>
#include <chrono>

#ifdef _WIN32
#include <windows.h>
#else
#include <termios.h>
#endif

// Клас Ch340AutoReset обгортає системний дескриптор послідовного порту CH340
// та надає методи керування лініями DTR і RTS для автоматичного скидання мікроконтролерів.
class Ch340AutoReset {
public:
    explicit Ch340AutoReset(std::string_view portName);
    ~Ch340AutoReset();

    // Заборона копіювання для запобігання дублюванню системного дескриптора (RAII)
    Ch340AutoReset(const Ch340AutoReset&) = delete;
    Ch340AutoReset& operator=(const Ch340AutoReset&) = delete;

    // Дозвіл переміщення
    Ch340AutoReset(Ch340AutoReset&& other) noexcept;
    Ch340AutoReset& operator=(Ch340AutoReset&& other) noexcept;

    // Відкриття та налаштування послідовного порту
    bool open(unsigned int baudRate = 115200);

    // Закриття порту
    void close();

    // Перевірка стану підключення
    bool isOpen() const;

    // Встановлення стану лінії DTR (true - активний/низький рівень)
    bool setDTR(bool active);

    // Встановлення стану лінії RTS (true - активний/низький рівень)
    bool setRTS(bool active);

    // Формування імпульсів для переведення мікроконтролера у режим завантажувача (bootloader)
    bool enterBootloader(std::chrono::milliseconds holdTime = std::chrono::milliseconds(100));

    // Просте перезавантаження мікроконтролера (RESET імпульс)
    bool reset(std::chrono::milliseconds pulseTime = std::chrono::milliseconds(50));

private:
    std::string m_portName;

#ifdef _WIN32
    HANDLE m_handle{INVALID_HANDLE_VALUE};
#else
    int m_fd{-1};
#endif
};

#endif // CH340_AUTORESET_HPP
