// Ініціалізація конфігурації для конкретних виводів
BitBangConfig bus_cfg{
    .data_port  = reinterpret_cast<void*>(GPIOB), // Порт лінії даних
    .data_pin   = 7,                              // Вивід SDA (лінія даних)
    .clock_port = reinterpret_cast<void*>(GPIOB), // Порт лінії тактування
    .clock_pin  = 6,                              // Вивід SCL (лінія тактування)
    .delay_us   = 4,                              // Затримка напівперіоду з компенсацією
    .open_drain = true                            // Режим відкритого колектора
};

// Створення екземпляра драйвера та ініціалізація шини
BitBangDriver bus(bus_cfg);
if (!bus.Init()) {
    // Обробка помилки ініціалізації ліній
}
