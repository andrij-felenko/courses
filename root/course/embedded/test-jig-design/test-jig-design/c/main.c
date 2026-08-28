// поріг у мілівольтах: 3.3 В ±0.1 В
#define RAIL_3V3_MIN_MV  3200
#define RAIL_3V3_MAX_MV  3400

// перевірка однієї точки: чи напруга в допуску
bool check_rail(uint16_t measured_mv, uint16_t lo_mv, uint16_t hi_mv) {
    return (measured_mv >= lo_mv) && (measured_mv <= hi_mv);
}

// у циклі тесту:
uint16_t v3v3 = jig_read_probe_mv(PROBE_3V3);   // прочитати голку через АЦП
bool ok = check_rail(v3v3, RAIL_3V3_MIN_MV, RAIL_3V3_MAX_MV);
if (!ok) {
    jig_fail("3V3 out of range", v3v3);          // у журнал: що саме й скільки
    return;                                       // далі не йдемо
}
