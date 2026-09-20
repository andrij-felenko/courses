#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"

// Клас-обгортка для управління радіомодулем
class NRF24L01 {
    spi_inst_t* spi;
    uint csn_pin;
    uint ce_pin;
public:
    NRF24L01(spi_inst_t* spi_inst, uint csn, uint ce) 
        : spi(spi_inst), csn_pin(csn), ce_pin(ce) {}
    
    void init() {
        // Ініціалізація SPI на 1 МГц (nRF24L01 підтримує до 10 МГц, але 1 МГц достатньо для перевірки)
        spi_init(spi, 1000 * 1000);
        gpio_set_function(PICO_DEFAULT_SPI_RX_PIN, GPIO_FUNC_SPI);
        gpio_set_function(PICO_DEFAULT_SPI_SCK_PIN, GPIO_FUNC_SPI);
        gpio_set_function(PICO_DEFAULT_SPI_TX_PIN, GPIO_FUNC_SPI);
        
        // Піни для вибору чіпа та ввімкнення приймача/передавача
        gpio_init(csn_pin);
        gpio_set_dir(csn_pin, GPIO_OUT);
        gpio_put(csn_pin, 1); // CSN високий - пристрій не вибрано
        
        gpio_init(ce_pin);
        gpio_set_dir(ce_pin, GPIO_OUT);
        gpio_put(ce_pin, 0);  // CE низький - режим очікування
    }

    // Читання регістру STATUS для перевірки SPI зв'язку.
    // Якщо адаптер живлення працює правильно, статус поверне значення (за замовчуванням 0x0E).
    // Якщо зв'язку немає або живлення відсутнє, повернеться 0x00 або 0xFF.
    uint8_t read_status() {
        uint8_t cmd = 0xFF; // Команда NOP (немає операції). nRF24L01 завжди повертає статус на першому байті транзакції
        uint8_t status = 0;
        
        gpio_put(csn_pin, 0); // Починаємо транзакцію (CSN = 0)
        spi_write_read_blocking(spi, &cmd, &status, 1);
        gpio_put(csn_pin, 1); // Завершуємо транзакцію (CSN = 1)
        
        return status;
    }
};

int main() {
    stdio_init_all();
    
    // Використовуємо spi0, CSN = пін 17, CE = пін 16
    NRF24L01 radio(spi0, 17, 16);
    radio.init();
    
    while (true) {
        uint8_t status = radio.read_status();
        printf("nRF24L01 STATUS: 0x%02X\n", status);
        
        if (status == 0x0E) {
            printf("Зв'язок успішний! Модуль підключено через адаптер і він отримує живлення.\n");
        } else if (status == 0x00 || status == 0xFF) {
            printf("Помилка: Немає зв'язку (перевірте підключення SPI та адаптера живлення).\n");
        }
        
        sleep_ms(2000);
    }
}
