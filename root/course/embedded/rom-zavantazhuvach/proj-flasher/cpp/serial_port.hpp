#pragma once

#include <chrono>
#include <cstdint>
#include <span>
#include <string>

// Послідовний порт у сирому режимі 115200 8E1 — саме такий кадр очікує
// ROM-завантажувач під час автопідлаштування бітрейту.
//
// RAII без напівживих станів: конструктор або віддає готовий до роботи порт,
// або кидає std::system_error. Дескриптор закриває деструктор.
class SerialPort {
public:
    explicit SerialPort(const std::string& path);
    ~SerialPort();

    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;
    SerialPort(SerialPort&& other) noexcept;
    SerialPort& operator=(SerialPort&& other) noexcept;

    // Пише весь зріз; часткові записи дописує сама.
    [[nodiscard]] bool write(std::span<const std::uint8_t> data) const;

    // Заповнює весь буфер або віддає false після спільного таймауту.
    [[nodiscard]] bool read(std::span<std::uint8_t> buffer, std::chrono::milliseconds timeout) const;

    void flush() const noexcept;

    // BOOT0 = 1, імпульс NRST, пауза на розкрутку HSI.
    void enterBootloader() const;

private:
    void setLines(bool dtr, bool rts) const;

    int fd_{-1};
};
