// Дані задачі
const double capacity   = 8.0e9;    // 8 ГБ ємності
const double endurance  = 3000.0;   // TLC: ~3000 циклів на блок
const double waf        = 3.0;      // підсилення запису файлової системи
const double rec_bytes  = 200.0;    // байтів на запис
const double rec_per_s  = 1.0;      // записів за секунду

// Логічний запис за добу
double per_day = rec_bytes * rec_per_s * 86400.0;   // = 17 280 000 байт/добу ≈ 17.3 МБ

// Строк служби
double years = (endurance * capacity) / (waf * per_day * 365.0);
//   = (3000 × 8e9) / (3 × 1.728e7 × 365)
//   = 2.4e13 / 1.893e10
//   ≈ 1268 років
