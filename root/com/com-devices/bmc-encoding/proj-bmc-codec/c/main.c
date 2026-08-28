#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define USBPD_FREQ_HZ         300000UL
#define USBPD_TBIT_US         3.333333f
#define USBPD_THALF_US        1.666667f

#define USBPD_TNOISE_MIN_US   0.833f
#define USBPD_TSPLIT_US       2.500f
#define USBPD_TTIMEOUT_MAX_US 4.167f

// 5-бітні коди K-символів
#define K_SYNC1               0x18  // 11000b
#define K_SYNC2               0x12  // 10010b
#define K_SYNC3               0x06  // 00110b
#define K_RST1                0x07  // 00111b
#define K_RST2                0x19  // 11001b
#define K_EOP                 0x0D  // 01101b

// Типи пакетних маркерів
typedef enum {
    SOP_TYPE_UNKNOWN = 0,
    SOP_TYPE_SOP,       // Sync1 + Sync1 + Sync1 + Sync2
    SOP_TYPE_SOP_PRIME, // Sync1 + Sync1 + Sync3 + Sync3
    SOP_TYPE_SOP_DPRIME,// Sync1 + Sync3 + Sync1 + Sync3
    SOP_TYPE_HARD_RESET,// RST1 + RST1 + RST1 + RST2
    SOP_TYPE_CABLE_RESET// RST1 + Sync1 + RST1 + Sync1
} usbpd_sop_t;

// Таблиця перетворення 4b у 5b
static const uint8_t table_4b5b[16] = {
    0x1E, 0x09, 0x14, 0x15, 0x0A, 0x0B, 0x0E, 0x0F,
    0x12, 0x13, 0x16, 0x17, 0x1A, 0x1B, 0x1C, 0x1D
};

// Зворотна таблиця 5b у 4b (0xFF означає невалідний код або K-код)
static const uint8_t table_5b4b[32] = {
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0x01, 0x04, 0x05, 0xFF, 0xFF, 0x06, 0x07,
    0xFF, 0xFF, 0x08, 0x09, 0x02, 0x03, 0x0A, 0x0B,
    0xFF, 0xFF, 0x0C, 0x0D, 0x0E, 0x0F, 0x00, 0xFF
};

// Розрахунок CRC-32 для USB Power Delivery
uint32_t usbpd_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320UL; // Дзеркальний поліном 0x04C11DB7
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

// Структура вихідного буфера BMC інтервалів
typedef struct {
    float intervals_us[2048];
    size_t count;
    uint8_t current_level;
} bmc_encoder_t;

void bmc_encoder_init(bmc_encoder_t *enc) {
    enc->count = 0;
    enc->current_level = 0;
}

static void bmc_encode_bit(bmc_encoder_t *enc, uint8_t bit) {
    if (bit) {
        // Логічна '1': два інтервали по 1.667 мкс
        enc->intervals_us[enc->count++] = USBPD_THALF_US;
        enc->intervals_us[enc->count++] = USBPD_THALF_US;
    } else {
        // Логічний '0': один інтервал 3.333 мкс
        enc->intervals_us[enc->count++] = USBPD_TBIT_US;
    }
}

static void bmc_encode_5b_symbol(bmc_encoder_t *enc, uint8_t sym5b) {
    // Передача LSB вперед (біти 0..4)
    for (int i = 0; i < 5; ++i) {
        bmc_encode_bit(enc, (sym5b >> i) & 1);
    }
}

// Формування повного пакета BMC в інтервали часу
size_t usbpd_encode_packet(const uint8_t *payload, size_t len,
                           usbpd_sop_t sop, bmc_encoder_t *enc) {
    bmc_encoder_init(enc);

    // 1. Преамбула: 64 біти '0' у BMC (64 переходи частотою 300 кГц)
    for (int i = 0; i < 64; ++i) {
        bmc_encode_bit(enc, 0);
    }

    // 2. Впорядкований набір SOP (4 символи 5b)
    switch (sop) {
        case SOP_TYPE_SOP:
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC2);
            break;
        case SOP_TYPE_SOP_PRIME:
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC3);
            bmc_encode_5b_symbol(enc, K_SYNC3);
            break;
        case SOP_TYPE_SOP_DPRIME:
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC3);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC3);
            break;
        case SOP_TYPE_HARD_RESET:
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_RST2);
            return enc->count;
        case SOP_TYPE_CABLE_RESET:
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            return enc->count;
        default:
            return 0;
    }

    // 3. Корисні дані (розбиття кожного байта на молодший і старший нібли)
    for (size_t i = 0; i < len; ++i) {
        uint8_t low_nibble = payload[i] & 0x0F;
        uint8_t high_nibble = (payload[i] >> 4) & 0x0F;
        bmc_encode_5b_symbol(enc, table_4b5b[low_nibble]);
        bmc_encode_5b_symbol(enc, table_4b5b[high_nibble]);
    }

    // 4. Обчислення та додавання CRC-32 (4 байти)
    uint32_t crc = usbpd_crc32(payload, len);
    for (int i = 0; i < 4; ++i) {
        uint8_t byte = (crc >> (i * 8)) & 0xFF;
        bmc_encode_5b_symbol(enc, table_4b5b[byte & 0x0F]);
        bmc_encode_5b_symbol(enc, table_4b5b[(byte >> 4) & 0x0F]);
    }

    // 5. Маркер кінця пакета EOP
    bmc_encode_5b_symbol(enc, K_EOP);

    return enc->count;
}

// Стан декодера BMC
typedef enum {
    DEC_WAIT_PREAMBLE,
    DEC_WAIT_SOP,
    DEC_RECEIVE_PAYLOAD,
    DEC_PACKET_DONE,
    DEC_ERROR
} dec_state_t;

typedef struct {
    dec_state_t state;
    bool half_bit_pending;
    uint32_t shift_reg;      // 20-бітний регістр для детекції SOP
    uint8_t sym_shift_reg;   // 5-бітний накопичувач для символів
    uint8_t sym_bit_count;
    uint8_t nibble_buffer;
    bool high_nibble_expected;
    usbpd_sop_t detected_sop;
    uint8_t rx_buffer[64];
    size_t rx_len;
    uint32_t rx_crc;
} bmc_decoder_t;

void bmc_decoder_init(bmc_decoder_t *dec) {
    memset(dec, 0, sizeof(bmc_decoder_t));
    dec->state = DEC_WAIT_PREAMBLE;
}

// Обробка одного виміряного інтервалу часу між фронтами
bool bmc_decoder_feed_interval(bmc_decoder_t *dec, float dt_us) {
    // 1. Фільтрація шумів
    if (dt_us < USBPD_TNOISE_MIN_US) {
        return false; // Ігноруємо брязкіт
    }

    // 2. Перевірка на таймаут
    if (dt_us > USBPD_TTIMEOUT_MAX_US) {
        dec->half_bit_pending = false;
        if (dec->state == DEC_RECEIVE_PAYLOAD && dec->rx_len > 4) {
            dec->state = DEC_PACKET_DONE;
            return true;
        }
        dec->state = DEC_WAIT_PREAMBLE;
        return false;
    }

    // 3. Розпізнавання півбіта / повного біта
    int bit_val = -1;
    if (dt_us < USBPD_TSPLIT_US) {
        // Інтервал півбіта (1.67 мкс)
        if (dec->half_bit_pending) {
            bit_val = 1; // Отримано другий півбіт -> це '1'
            dec->half_bit_pending = false;
        } else {
            dec->half_bit_pending = true; // Чекаємо напарника
            return false;
        }
    } else {
        // Інтервал повного біта (3.33 мкс)
        if (dec->half_bit_pending) {
            // Порушення протоколу: після першого півбіта прийшов повний біт
            dec->half_bit_pending = false;
            dec->state = DEC_ERROR;
            return false;
        }
        bit_val = 0; // Одиночний перехід -> це '0'
    }

    // 4. Обробка прийнятого біта скінченним автоматом
    dec->shift_reg = ((dec->shift_reg >> 1) | ((uint32_t)bit_val << 19)) & 0xFFFFF;

    if (dec->state == DEC_WAIT_PREAMBLE || dec->state == DEC_WAIT_SOP) {
        // Перевірка 20-бітного вікна на послідовність SOP (LSB-перший)
        uint32_t sop_pattern = (uint32_t)K_SYNC1 | ((uint32_t)K_SYNC1 << 5) |
                               ((uint32_t)K_SYNC1 << 10) | ((uint32_t)K_SYNC2 << 15);
        uint32_t sop_p_pattern = (uint32_t)K_SYNC1 | ((uint32_t)K_SYNC1 << 5) |
                                 ((uint32_t)K_SYNC3 << 10) | ((uint32_t)K_SYNC3 << 15);
        uint32_t hard_rst_pattern = (uint32_t)K_RST1 | ((uint32_t)K_RST1 << 5) |
                                    ((uint32_t)K_RST1 << 10) | ((uint32_t)K_RST2 << 15);

        if (dec->shift_reg == sop_pattern) {
            dec->detected_sop = SOP_TYPE_SOP;
            dec->state = DEC_RECEIVE_PAYLOAD;
            dec->sym_bit_count = 0;
            dec->sym_shift_reg = 0;
            dec->rx_len = 0;
            dec->high_nibble_expected = false;
            return false;
        } else if (dec->shift_reg == sop_p_pattern) {
            dec->detected_sop = SOP_TYPE_SOP_PRIME;
            dec->state = DEC_RECEIVE_PAYLOAD;
            dec->sym_bit_count = 0;
            dec->sym_shift_reg = 0;
            dec->rx_len = 0;
            dec->high_nibble_expected = false;
            return false;
        } else if (dec->shift_reg == hard_rst_pattern) {
            dec->detected_sop = SOP_TYPE_HARD_RESET;
            dec->state = DEC_PACKET_DONE;
            return true;
        }
        return false;
    }

    if (dec->state == DEC_RECEIVE_PAYLOAD) {
        dec->sym_shift_reg |= ((uint8_t)bit_val << dec->sym_bit_count);
        dec->sym_bit_count++;

        if (dec->sym_bit_count == 5) {
            uint8_t symbol = dec->sym_shift_reg;
            dec->sym_bit_count = 0;
            dec->sym_shift_reg = 0;

            // Перевірка на EOP
            if (symbol == K_EOP) {
                dec->state = DEC_PACKET_DONE;
                return true;
            }

            // Декодування 5b у 4b
            uint8_t nibble = table_5b4b[symbol & 0x1F];
            if (nibble == 0xFF) {
                dec->state = DEC_ERROR;
                return false;
            }

            if (!dec->high_nibble_expected) {
                dec->nibble_buffer = nibble;
                dec->high_nibble_expected = true;
            } else {
                uint8_t full_byte = dec->nibble_buffer | (nibble << 4);
                dec->high_nibble_expected = false;
                if (dec->rx_len < sizeof(dec->rx_buffer)) {
                    dec->rx_buffer[dec->rx_len++] = full_byte;
                }
            }
        }
    }

    return false;
}
