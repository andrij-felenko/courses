// Зробити ОДИН вимір у режимі forced і прочитати тиск (гПа). Між вимірами давач спить.
float bmp280_read_forced_pressure(void) {
  // Запустити разовий вимір (ті самі передискретизації + MODE_FORCED):
  wr8(0xF4, OSRS_T_X2 | OSRS_P_X16 | MODE_FORCED);

  // Дочекатися завершення: біт 3 (measuring) у статусі 0xF3 = 0, коли готово.
  uint8_t st;
  do {
    delay(2);
    if (!rd8(0xF3, &st)) return NAN;
  } while (st & 0x08);          // біт measuring ще виставлений — чекаємо

  return bmp280_pressure_hpa(); // читає T (оновлює t_fine) і P
}
