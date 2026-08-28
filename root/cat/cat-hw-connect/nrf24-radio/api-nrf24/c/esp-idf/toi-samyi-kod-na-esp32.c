// Ті самі три речі — шина, CSN, CE — але названі в конфігурації драйвера.
spi_bus_config_t bus = {                 // SPI2_HOST (він же VSPI)
  .sclk_io_num = 18, .mosi_io_num = 23, .miso_io_num = 19,
  .quadwp_io_num = -1, .quadhd_io_num = -1,
};
spi_device_interface_config_t dev = {
  .mode = 0, .clock_speed_hz = 8 * 1000 * 1000,
  .spics_io_num = 5,                     // CSN — драйвер смикає його сам
  .queue_size = 1,
};
gpio_set_direction(GPIO_NUM_4, GPIO_MODE_OUTPUT);   // CE — звичайний вихід, він ваш
