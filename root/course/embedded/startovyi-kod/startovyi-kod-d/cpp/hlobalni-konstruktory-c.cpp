/* Глобальний об'єкт C++ з нетривіальним конструктором */
class UartDriver {
public:
    UartDriver(uint32_t baudrate) {
        /* Код конструктора, який має виконатися ДО виклику main() */
        this->init_hardware(baudrate);
    }
private:
    void init_hardware(uint32_t baudrate);
};

UartDriver g_console_uart(115200); /* Хто викличе цей конструктор? */
