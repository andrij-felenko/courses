#include "adxl345_driver.hpp"
#include "stm32_exti_guard.hpp"
#include <iostream>
#include <vector>
#include <atomic>

// Навчальна реалізація апаратної шини SPI STM32 для демонстрації підключення Драйвера
class Stm32SpiBus : public adxl345::IBus {
public:
    Stm32SpiBus() = default;
    ~Stm32SpiBus() override = default;

    void acquire() override {
        // Симуляція вибору Chip Select (CS -> LOW) та встановлення SPI mutex
    }

    void release() override {
        // Симуляція деактивації Chip Select (CS -> HIGH) та звільнення SPI mutex
    }

    bool read_registers(uint8_t reg, uint8_t* buffer, size_t len) override {
        if (!buffer || len == 0) return false;

        // Симуляція зчитування регістрів ADXL345
        if (reg == adxl345::Register::DEVID) {
            buffer[0] = adxl345::ADXL345_EXPECTED_DEVID; // Повертаємо 0xE5
            return true;
        }

        if (reg == adxl345::Register::FIFO_STATUS) {
            buffer[0] = 16; // Симулюємо наявність 16 вибірок у FIFO
            return true;
        }

        if (reg == adxl345::Register::DATAX0) {
            // Симуляція закодованих 16-бітних даних вибірок LSB
            for (size_t i = 0; i < len; ++i) {
                buffer[i] = static_cast<uint8_t>(i * 10);
            }
            return true;
        }

        return true;
    }

    bool write_register(uint8_t reg, uint8_t value) override {
        (void)reg;
        (void)value;
        return true;
    }
};

// Глобальний прапорець сигналу переривання для подійної обробки в main
static std::atomic<bool> g_fifo_watermark_flag{false};

int main() {
    std::cout << "--- Запуск C++ Драйвера ADXL345 (STM32 Event-Driven Architecture) ---" << std::endl;

    // 1. Створення апаратної шини SPI та ініціалізація драйвера
    Stm32SpiBus spi_bus;
    adxl345::Adxl345Driver accel(spi_bus);

    if (!accel.init(adxl345::Range::G2, true)) {
        std::cerr << "Помилка ініціалізації акселерометра ADXL345!" << std::endl;
        return -1;
    }
    std::cout << "ADXL345 успішно ініціалізовано. Режим: FULL_RES, Діапазон: ±2g." << std::endl;

    // 2. Налаштування апаратного переривання EXTI для виводу INT1 (Watermark threshold = 16 вибірок)
    stm32::ExtiConfig exti_cfg{};
    exti_cfg.gpio_pin = 0x0001;
    exti_cfg.irq_number = 6;
    stm32::ExtiInterruptGuard exti_guard(exti_cfg);

    // 3. Реєстрація подійно-орієнтованих callback-функцій
    accel.set_watermark_callback([]() {
        g_fifo_watermark_flag.store(true);
    });

    exti_guard.register_callback([&accel]() {
        accel.handle_watermark_event();
    });

    // 4. Налаштування FIFO буфера ADXL345 у режим Stream з порогом 16 вибірок
    constexpr uint8_t WATERMARK_THRESHOLD = 16;
    if (!accel.configure_fifo_watermark(WATERMARK_THRESHOLD, 1)) {
        std::cerr << "Помилка конфігурації FIFO Watermark!" << std::endl;
        return -1;
    }
    std::cout << "FIFO Watermark налаштовано на " << static_cast<int>(WATERMARK_THRESHOLD) << " вибірок." << std::endl;

    // 5. Симуляція апаратного переривання EXTI (ISR сповіщення)
    std::cout << "\n[Подія EXTI] Спрацювало апаратне переривання Watermark!" << std::endl;
    exti_guard.handle_isr();

    // 6. Неблокуюча обробка подійної черги у головному циклі
    if (g_fifo_watermark_flag.load()) {
        g_fifo_watermark_flag.store(false);

        adxl345::RawVector3 raw_samples[32];
        size_t samples_read = accel.read_fifo_burst(raw_samples, WATERMARK_THRESHOLD);

        std::cout << "Успішно зчитано " << samples_read << " вибірок з FIFO буфера ADXL345." << std::endl;

        // Перетворення першої вибірки у фізичні величини за допомогою шаблонізованого UnitConverter
        if (samples_read > 0) {
            auto accel_g = adxl345::UnitConverter<adxl345::Unit::G>::convert_vector(
                raw_samples[0], accel.get_current_range(), accel.is_full_resolution()
            );

            auto accel_mps2 = adxl345::UnitConverter<adxl345::Unit::MetersPerSecSq>::convert_vector(
                raw_samples[0], accel.get_current_range(), accel.is_full_resolution()
            );

            std::cout << "\nПриклад конвертації першої вибірки LSB у фізичні одиниці:" << std::endl;
            std::cout << "  Raw LSB: X=" << raw_samples[0].x << ", Y=" << raw_samples[0].y << ", Z=" << raw_samples[0].z << std::endl;
            std::cout << "  Прискорення [g]:     X=" << accel_g.x << " g, Y=" << accel_g.y << " g, Z=" << accel_g.z << " g" << std::endl;
            std::cout << "  Прискорення [м/с²]:  X=" << accel_mps2.x << " м/с², Y=" << accel_mps2.y << " м/с², Z=" << accel_mps2.z << " м/с²" << std::endl;
        }
    }

    std::cout << "\n--- Програму успішно завершено ---" << std::endl;
    return 0;
}
