#pragma once

#include <cstdint>
#include <system_error>

enum class RadioFrequency {
    Freq433MHz,
    Freq2400MHz
};

class RadioRssi {
public:
    // Конструктор ініціалізує з'єднання з радіомодулем
    // Може кидати std::runtime_error при апаратних помилках
    RadioRssi(RadioFrequency freq, int hardwareId);
    
    // Звільнення ресурсів
    ~RadioRssi();

    // Заборона копіювання (радіомодуль - унікальний ресурс)
    RadioRssi(const RadioRssi&) = delete;
    RadioRssi& operator=(const RadioRssi&) = delete;
    
    // Дозвіл на переміщення
    RadioRssi(RadioRssi&&) noexcept;
    RadioRssi& operator=(RadioRssi&&) noexcept;

    // Читає рівень сигналу
    // Повертає значення в дБм або кидає виняток, якщо зв'язок втрачено
    int8_t readRssi() const;

    RadioFrequency getFrequency() const noexcept { return frequency_; }

private:
    RadioFrequency frequency_;
    int hardwareId_;
    bool isConnected_;
};
