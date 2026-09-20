#include "RadioRssi.hpp"
#include <stdexcept>
#include <cstdlib>
#include <ctime>

RadioRssi::RadioRssi(RadioFrequency freq, int hardwareId)
    : frequency_(freq), hardwareId_(hardwareId), isConnected_(false) {
    
    // Імітація перевірки наявності пристрою на шині
    if (hardwareId < 0) {
        throw std::invalid_argument("Некоректний ідентифікатор обладнання");
    }
    
    // Імітація успішної ініціалізації
    isConnected_ = true;
    
    // Сід для імітації значень
    std::srand(static_cast<unsigned int>(std::time(nullptr)) ^ hardwareId_);
}

RadioRssi::~RadioRssi() {
    if (isConnected_) {
        // Вимкнення живлення антени/модуля, переведення в сон тощо
        isConnected_ = false;
    }
}

RadioRssi::RadioRssi(RadioRssi&& other) noexcept
    : frequency_(other.frequency_), 
      hardwareId_(other.hardwareId_), 
      isConnected_(other.isConnected_) {
    other.isConnected_ = false;
}

RadioRssi& RadioRssi::operator=(RadioRssi&& other) noexcept {
    if (this != &other) {
        frequency_ = other.frequency_;
        hardwareId_ = other.hardwareId_;
        isConnected_ = other.isConnected_;
        other.isConnected_ = false;
    }
    return *this;
}

int8_t RadioRssi::readRssi() const {
    if (!isConnected_) {
        throw std::runtime_error("Втрачено зв'язок із радіомодулем");
    }
    
    // Імітація отримання даних із регістра
    int baseRssi = (frequency_ == RadioFrequency::Freq433MHz) ? -65 : -75;
    int noise = (std::rand() % 15) - 7;
    
    return static_cast<int8_t>(baseRssi + noise);
}
