// Ключові поля з UBX-NAV-PVT (зсуви в байтах від початку payload).
// Числа приходять little-endian — на ARM/ESP32 читаються як є.
typedef struct {
    uint32_t iTOW;      // 0  час тижня, мс
    // ...пропущені поля дати/часу...
    uint8_t  fixType;   // 20 тип фікса: 0=немає, 2=2D, 3=3D
    uint8_t  flags;     // 21
    uint8_t  reserved;  // 22
    uint8_t  numSV;     // 23 кількість супутників у розв'язку
    int32_t  lon;       // 24 довгота, одиниці 1e-7 градуса
    int32_t  lat;       // 28 широта,  одиниці 1e-7 градуса
    int32_t  height;    // 32 висота над еліпсоїдом, мм
    int32_t  hMSL;      // 36 висота над рівнем моря, мм
    // ...швидкості, курс, точності далі...
} ubx_nav_pvt_t;

void use_pvt(const ubx_nav_pvt_t *p) {
    if (p->fixType < 3) return;                 // немає 3D-фікса — не довіряти
    double lat_deg = p->lat * 1e-7;             // 1e-7°/од. → градуси
    double lon_deg = p->lon * 1e-7;
    double alt_m   = p->hMSL / 1000.0;          // мм → метри
    ekf_update_position(lat_deg, lon_deg, alt_m, p->numSV);
}
