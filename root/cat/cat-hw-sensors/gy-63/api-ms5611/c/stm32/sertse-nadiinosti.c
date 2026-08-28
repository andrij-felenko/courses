int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_I2C1_Init();                    // CubeMX: I2C1, Fast Mode 400 кГц, ніжки з альт. функцією

  if (!ms5611_reset())     { printf("MS5611: немає ACK на скид\r\n"); Error_Handler(); }
  if (!ms5611_read_prom()) { printf("MS5611: не прочитав PROM\r\n");  Error_Handler(); }

  if (!ms5611_prom_crc_ok(g_prom)) {
    printf("MS5611: CRC-4 калібрування НЕ зійшлася — коефіцієнти пошкоджені!\r\n");
    Error_Handler();                 // працювати з такими даними не можна
  }
  printf("MS5611: PROM цілий, коефіцієнти дійсні.\r\n");

  while (1) { /* цикл вимірювання */ }
}
