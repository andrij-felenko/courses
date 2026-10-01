#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <cstdint>
#include <array>

// Платформа: Arduino Framework (C++)
// Призначення: Формування тестових сигналів SPI та I2C для аналізу 8-канальним логічним аналізатором WeAct DLA Mini

constexpr uint8_t PIN_SPI_CS = 10;
constexpr uint8_t I2C_SLAVE_ADDR = 0x68; // Стандартна адреса веденого пристрою (наприклад, MPU6050 / DS3231)
constexpr uint32_t SPI_CLOCK_HZ = 4000000; // 4 МГц для зручного захоплення при частоті дискретизації DLA Mini 24 МГц

class BusTestGenerator {
private:
    uint8_t m_csPin;
    uint8_t m_i2cAddress;
    uint32_t m_spiSpeed;

public:
    BusTestGenerator(uint8_t csPin, uint8_t i2cAddress, uint32_t spiSpeed)
        : m_csPin(csPin), m_i2cAddress(i2cAddress), m_spiSpeed(spiSpeed) {}

    void begin() {
        // Налаштування виводу Chip Select для SPI
        pinMode(m_csPin, OUTPUT);
        digitalWrite(m_csPin, HIGH); // Пасивний стан (неактивний високий рівень)

        // Апаратна ініціалізація шини SPI (Mode 0: CPOL=0, CPHA=0, MSB first)
        SPI.begin();

        // Апаратна ініціалізація шини I2C в режимі Master (стандартна частота Fast Mode 400 кГц)
        Wire.begin();
        Wire.setClock(400000);
    }

    void sendSpiFrame(const uint8_t* data, size_t length) {
        if (data == nullptr || length == 0) {
            return;
        }

        // Активація веденого пристрою (падаючий фронт на CS слугує тригером для DLA Mini)
        digitalWrite(m_csPin, LOW);
        delayMicroseconds(2); // Мінімальна затримка для встановлення фронту

        SPI.beginTransaction(SPISettings(m_spiSpeed, MSBFIRST, SPI_MODE0));
        for (size_t i = 0; i < length; ++i) {
            SPI.transfer(data[i]);
        }
        SPI.endTransaction();

        delayMicroseconds(2);
        digitalWrite(m_csPin, HIGH); // Деактивація Chip Select
    }

    void sendI2cRegisterWrite(uint8_t regAddr, const uint8_t* data, size_t length) {
        // Стартова умова (Start Condition), передача адреси пристрою та біта W
        Wire.beginTransmission(m_i2cAddress);
        Wire.write(regAddr); // Запис адреси цільового регістру

        if (data != nullptr && length > 0) {
            Wire.write(data, length); // Передача байтового масиву даних
        }

        // Стопова умова (Stop Condition), вивільнення шини SCL/SDA
        uint8_t result = Wire.endTransmission();
        (void)result; // Результат ACK/NACK відстежується на логічному аналізаторі
    }
};

// Створення об'єкта генератора тестових сигналів
static BusTestGenerator busTester(PIN_SPI_CS, I2C_SLAVE_ADDR, SPI_CLOCK_HZ);

void setup() {
    Serial.begin(115200);
    busTester.begin();
}

void loop() {
    // 1. Тестова пачка даних для шини SPI (Команда читання регістру 0x80 та 3 байти даних)
    const std::array<uint8_t, 4> spiTestData = {0x80, 0xA5, 0x5A, 0xFF};
    busTester.sendSpiFrame(spiTestData.data(), spiTestData.size());

    delayMicroseconds(500); // Пауза між транзакціями для розрізнення пачок у PulseView

    // 2. Тестова пачка даних для шини I2C (Запис у регістр 0x10 значення 0xDE 0xAD 0xBE 0xEF)
    const std::array<uint8_t, 4> i2cTestData = {0xDE, 0xAD, 0xBE, 0xEF};
    busTester.sendI2cRegisterWrite(0x10, i2cTestData.data(), i2cTestData.size());

    // Інтервал між циклами генерації (100 мс для зручного повторного тригерування)
    delay(100);
}
