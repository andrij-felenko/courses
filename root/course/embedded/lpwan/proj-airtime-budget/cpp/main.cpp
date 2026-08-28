#include <cstdint>

// Параметри пакета й радіо для розрахунку airtime.
struct LoraCfg {
    uint8_t  sf;          // коефіцієнт розширення, 7..12
    uint32_t bw_hz;       // ширина смуги в Гц (напр. 125000)
    uint8_t  payload;     // довжина корисних даних, байтів
    uint8_t  cr;          // кодова швидкість: 1..4  (1 = 4/5 ... 4 = 4/8)
    uint8_t  preamble;    // символів преамбули (типово 8)
    bool     explicit_hdr;// true = явний заголовок, false = неявний
    bool     crc;         // true = додано CRC
};

// Цілочисельна стеля цілого ділення: ⌈a / b⌉ для a >= 0, b > 0.
static constexpr int32_t ceil_div(int32_t a, int32_t b) {
    return (a + b - 1) / b;
}

// Час одного символа в наносекундах: Tsym = 2^SF / BW.
// Наносекунди дають запас точності навіть на найшвидших SF без float.
static uint64_t symbol_time_ns(uint8_t sf, uint32_t bw_hz) {
    uint64_t two_pow_sf = uint64_t{1} << sf;                // 2^SF
    return (two_pow_sf * 1000000000ULL) / bw_hz;            // 2^SF / BW, нс
}

// Повний час пакета в ефірі (time on air) у мікросекундах.
uint32_t lora_airtime_us(const LoraCfg &c) {
    uint64_t tsym_ns = symbol_time_ns(c.sf, c.bw_hz);

    // DE (low data rate optimize) вмикається, коли символ довший за 16 мс.
    int de = (tsym_ns > 16000000ULL) ? 1 : 0;              // 16 мс = 16e6 нс
    int ih = c.explicit_hdr ? 0 : 1;                       // implicit header
    int crc = c.crc ? 1 : 0;

    // Число символів пакета за формулою Semtech.
    int32_t num = 8 * static_cast<int32_t>(c.payload) - 4 * static_cast<int32_t>(c.sf)
                  + 28 + 16 * crc - 20 * ih;
    int32_t den = 4 * (static_cast<int32_t>(c.sf) - 2 * de);
    int32_t groups = ceil_div(num, den) * (static_cast<int32_t>(c.cr) + 4);
    if (groups < 0) groups = 0;                            // max(..., 0)
    int32_t payload_symb = 8 + groups;

    // Преамбула: (n + 4.25) символів. 4.25 = 17/4 → рахуємо в чвертях символа.
    // символів·4 + 17 чвертей, тоді ділимо на 4 у наносекундах.
    uint64_t preamble_q = uint64_t{c.preamble} * 4 + 17;   // (n + 4.25) у чвертях
    uint64_t t_preamble_ns = preamble_q * tsym_ns / 4;
    uint64_t t_payload_ns  = uint64_t{payload_symb} * tsym_ns;

    return static_cast<uint32_t>((t_preamble_ns + t_payload_ns) / 1000ULL); // нс → мкс
}
