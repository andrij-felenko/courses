#include <Arduino.h>

class UartFifoDriver {
public:
    static const size_t BUF_SIZE = 1024;

    void begin(uint32_t baud) {
        Serial.begin(baud);
        // Налаштування апаратних регістрів UART0 під Arduino Core ESP8266
        USC0(0) = (116 << UTRXI) | (10 << UTTXI); // Пороги watermark та timeout
        USC0(1) |= UCRXI | UCFLOW;              // Увімкнення таймауту та RTS/CTS
        
        // Скидання FIFO та увімкнення переривань
        USC0(1) |= UCRST;
        USC0(1) &= ~UCRST;
        USIE(0) |= UIFF | UITO | UIOV;           // Дозвіл FULL, TOUT, OVF переривань
    }

    static void IRAM_ATTR onInterrupt() {
        uint32_t st = USIS(0);
        if (st & (UIFF | UITO)) {
            while (USF(0) & 0xFF) { // Читання поки є байти у FIFO
                uint8_t c = USB(0);
                bufferPut(c);
            }
            USIC(0) = UIFF | UITO; // Очищення прапорів
        }
        if (st & UIOV) { // Обробка overrun
            USC0(1) |= UCRST;
            USC0(1) &= ~UCRST;
            USIC(0) = UIOV;
        }
    }

private:
    static uint8_t ringBuf[BUF_SIZE];
    static volatile size_t head;
    static volatile size_t tail;

    static void bufferPut(uint8_t b) {
        size_t next = (head + 1) % BUF_SIZE;
        if (next != tail) {
            ringBuf[head] = b;
            head = next;
        }
    }
};

uint8_t UartFifoDriver::ringBuf[UartFifoDriver::BUF_SIZE];
volatile size_t UartFifoDriver::head = 0;
volatile size_t UartFifoDriver::tail = 0;
