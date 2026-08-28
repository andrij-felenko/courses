// ── Адреси регістрів: парна = запис, непарна = читання ──
// (біт7=1; біт6=0 годинник; біти5..1 адреса; біт0 = напрям)
const uint8_t REG_SECONDS = 0x80;   // читання 0x81
const uint8_t REG_MINUTES = 0x82;   // 0x83
const uint8_t REG_HOURS   = 0x84;   // 0x85
const uint8_t REG_DATE    = 0x86;   // число місяця,     0x87
const uint8_t REG_MONTH   = 0x88;   // 0x89
const uint8_t REG_DOW     = 0x8A;   // день тижня 1..7,  0x8B
const uint8_t REG_YEAR    = 0x8C;   // 00..99,           0x8D
const uint8_t REG_WP      = 0x8E;   // захист запису,    0x8F
const uint8_t REG_TRICKLE = 0x90;   // підзаряд,         0x91

const uint8_t CLK_BURST   = 0xBE;   // запис усіх регістрів пачкою; читання 0xBF
