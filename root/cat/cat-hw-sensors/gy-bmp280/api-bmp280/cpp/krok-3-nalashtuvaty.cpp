// Поля ctrl_meas (0xF4):
#define OSRS_T_X2   (0x02 << 5)   // температура ×2
#define OSRS_P_X16  (0x05 << 2)   // тиск ×16
#define MODE_NORMAL  0x03         // неперервний
#define MODE_FORCED  0x01         // разовий на вимогу
#define MODE_SLEEP   0x00         // сон

// Поля config (0xF5):
#define T_SB_500MS  (0x04 << 5)   // пауза 500 мс між вимірами
#define FILTER_16   (0x04 << 2)   // IIR-коефіцієнт 16

// Налаштувати давач на неперервний вимір: T×2, P×16, фільтр 16, пауза 500 мс.
bool bmp280_configure(void) {
  // config пишемо ПЕРШИМ: у режимі normal запис у config може бути проігнорований,
  // тож безпечно міняти його, поки давач ще спить (mode=00 після живлення).
  if (!wr8(0xF5, T_SB_500MS | FILTER_16)) return false;
  // ctrl_meas із режимом normal — з цієї миті давач починає міряти сам.
  if (!wr8(0xF4, OSRS_T_X2 | OSRS_P_X16 | MODE_NORMAL)) return false;
  return true;
}
