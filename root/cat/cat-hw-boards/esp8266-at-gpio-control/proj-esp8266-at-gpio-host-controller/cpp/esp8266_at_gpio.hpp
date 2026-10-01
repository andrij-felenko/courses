#ifndef ESP8266_AT_GPIO_HPP
#define ESP8266_AT_GPIO_HPP

#include <string>
#include <string_view>
#include <functional>
#include <cstdint>

// Режими роботи виводів GPIO ESP8266
enum class GpioMode {
    Input = 0,
    Output = 1
};

// Логічні рівні на виводах GPIO
enum class GpioLevel {
    Low = 0,
    High = 1
};

// Статуси виконання AT-команд
enum class AtResponseStatus {
    None,
    Ok,
    Error,
    Timeout
};

// Стани асинхронного автомата (FSM)
enum class DriverState {
    Idle,
    SendingSetDir,
    WaitingSetDirResponse,
    SendingWritePin,
    WaitingWritePinResponse,
    SendingReadPin,
    WaitingReadPinResponse
};

/**
 * @brief Клас для розбору текстового потоку UART та URC-повідомлень від ESP8266
 */
class UrcParser {
public:
    using UrcCallback = std::function<void(int pin, GpioLevel level)>;

    UrcParser() = default;

    // Додавання символу з UART у буфер та перевірка рядка
    void feedChar(char c);

    // Отримання статусу виконання останньої команди
    AtResponseStatus popResponseStatus();

    // Встановлення зворотного виклику для асинхронних подій +GPIOINDB
    void setUrcCallback(UrcCallback cb) { urcCallback_ = cb; }

private:
    std::string rxBuffer_;
    AtResponseStatus lastStatus_{AtResponseStatus::None};
    UrcCallback urcCallback_;

    void processLine(std::string_view line);
    void parseUrc(std::string_view line);
};

/**
 * @brief Клас неблокуючого драйвера керування GPIO ESP8266 через AT-команди
 */
class Esp8266GpioDriver {
public:
    using TxFunc = std::function<void(std::string_view)>;

    explicit Esp8266GpioDriver(TxFunc txFunc);

    // Передача символів з UART в обробник
    void feedRx(std::string_view data);

    // Асинхронне налаштування напрямку виводу (AT+SYSGPIODIR)
    bool setPinDirection(int pin, GpioMode mode);

    // Асинхронний запис логічного рівня (AT+SYSGPIOWR)
    bool writePin(int pin, GpioLevel level);

    // Асинхронне зчитування логічного рівня (AT+SYSGPIORD)
    bool readPin(int pin);

    // Періодичне оновлення автомата станів (викликається в головному циклі)
    void tick(uint32_t currentMillis);

    // Перевірка зайнятості драйвера виконанням команди
    bool isBusy() const { return state_ != DriverState::Idle; }

    // Реєстрація обробника асинхронних подій виводів (+GPIOINDB)
    void setOnPinChanged(UrcParser::UrcCallback cb) { parser_.setUrcCallback(cb); }

private:
    TxFunc txFunc_;
    UrcParser parser_;
    DriverState state_{DriverState::Idle};

    int activePin_{-1};
    GpioMode targetMode_{GpioMode::Output};
    GpioLevel targetLevel_{GpioLevel::Low};
    uint32_t commandStartMs_{0};
    static constexpr uint32_t TIMEOUT_MS = 2000;
};

#endif // ESP8266_AT_GPIO_HPP
