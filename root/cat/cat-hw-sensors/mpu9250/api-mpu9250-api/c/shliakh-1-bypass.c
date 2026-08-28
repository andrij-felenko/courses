#define REG_USER_CTRL     0x6A
#define REG_INT_PIN_CFG   0x37

// Регістри самого AK8963 (адресуються за AK_ADDR = 0x0C):
#define AK_WIA    0x00       // паспорт, має віддати 0x48
#define AK_ST1    0x02       // біт 0 (DRDY) = дані готові
#define AK_HXL    0x03       // перший байт даних (X, МОЛОДШИЙ — little-endian!)
#define AK_ST2    0x09       // читання ЗАВЕРШУЄ цикл; біт 3 (HOFL) = перевантаження
#define AK_CNTL1  0x0A       // режим роботи
#define AK_ASAX   0x10       // заводські поправки чутливості X/Y/Z (0x10..0x12)

// Режими AK8963 (біти 3:0 регістра CNTL1; біт 4 = роздільність):
#define AK_MODE_POWERDOWN  0x00
#define AK_MODE_FUSEROM    0x0F           // доступ до заводських поправок
#define AK_MODE_CONT2_16B  0x16           // безперервно 100 Гц, 16 біт
//  0x16 = 0001 0110: біт4=1 → 16 біт; біти3:0=0110 → безперервний режим 2 (100 Гц)

void ak_enable_bypass(void) {
    // 1. Вимкнути внутрішній майстер MPU — інакше bypass не пустить.
    i2c_write_reg(MPU_ADDR, REG_USER_CTRL, 0x00);
    delay_ms(3);
    // 2. Увімкнути наскрізний прохід: BYPASS_EN (біт 1).
    i2c_write_reg(MPU_ADDR, REG_INT_PIN_CFG, 0x02);
    delay_ms(3);
    // Тепер AK8963 доступний напряму на адресі 0x0C.
}
