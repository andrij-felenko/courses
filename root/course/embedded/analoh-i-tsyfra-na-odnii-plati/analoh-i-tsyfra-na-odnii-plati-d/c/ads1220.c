#include "ads1220.h"

#include <stddef.h>

#include "platform.h"

/* Команди інтерфейсу (даташит TI SBAS501, розділ «Command Definitions»). */
#define CMD_RESET     0x06u
#define CMD_START     0x08u
#define CMD_POWERDOWN 0x02u
#define CMD_RDATA     0x10u

/* RREG/WREG: у молодших бітах адреса регістра (rr) і кількість байтів
 * мінус один (nn). Читаємо й пишемо всі чотири регістри одним пакетом. */
#define CMD_RREG(reg, count) ((uint8_t)(0x20u | ((uint8_t)(reg) << 2) | ((uint8_t)(count) - 1u)))
#define CMD_WREG(reg, count) ((uint8_t)(0x40u | ((uint8_t)(reg) << 2) | ((uint8_t)(count) - 1u)))

#define ADS1220_REG_COUNT 4u

/* Регістр 0: MUX[7:4] = 0000 — диференційна пара AIN0/AIN1;
 *            GAIN[3:1] = 101 — підсилення 32;
 *            PGA_BYPASS[0] = 0 — PGA увімкнено, вхід високоомний.
 * Регістр 1: DR[7:5] = 000 — 20 SPS у нормальному режимі;
 *            MODE[4:3] = 00 — нормальний режим;
 *            CM[2] = 1 — неперервні перетворення;
 *            TS[1] = 0, BCS[0] = 0 — датчик температури й струм обриву вимкнені.
 * Регістр 2: VREF[7:6] = 01 — зовнішня опора з виводів REFP0/REFN0;
 *            50/60[5:4] = 01 — одночасне придушення 50 і 60 Гц (доступне при 20 SPS);
 *            PSW[3] = 0, IDAC[2:0] = 000 — силовий ключ і джерела струму вимкнені.
 * Регістр 3: усі поля нульові — виводи IDAC нікуди не заведені,
 *            DRDY віддається окремою лінією, а не поверх DOUT. */
static const uint8_t k_config[ADS1220_REG_COUNT] = { 0x0Au, 0x04u, 0x50u, 0x00u };

static bool xfer(const uint8_t *tx, uint8_t *rx, size_t len)
{
    board_spi_select();
    bool ok = board_spi_transfer(tx, rx, len);
    board_spi_release();
    return ok;
}

static ads1220_status_t send_command(uint8_t op)
{
    uint8_t tx = op;
    uint8_t rx = 0u;

    return xfer(&tx, &rx, 1u) ? ADS1220_OK : ADS1220_ERR_SPI;
}

ads1220_status_t ads1220_init(void)
{
    ads1220_status_t st = send_command(CMD_RESET);
    if (st != ADS1220_OK) {
        return st;
    }

    /* Даташит вимагає витримати після скидання 50 мкс плюс 32 такти
     * модулятора. Двох мілісекунд вистачає з великим запасом. */
    board_delay_ms(2u);

    uint8_t tx[1u + ADS1220_REG_COUNT];
    uint8_t rx[1u + ADS1220_REG_COUNT] = { 0u };

    tx[0] = CMD_WREG(0u, ADS1220_REG_COUNT);
    for (size_t i = 0u; i < ADS1220_REG_COUNT; ++i) {
        tx[i + 1u] = k_config[i];
    }
    if (!xfer(tx, rx, sizeof tx)) {
        return ADS1220_ERR_SPI;
    }

    /* Читаємо конфігурацію назад і звіряємо. Це не параноя: якщо лінію CS
     * розвели через розріз полігону і на її зворотний струм наклався дзвін,
     * чип половину команд просто не побачить. Він лишиться в стандартному
     * ввімкненні — підсилення 1, внутрішня опора 2.048 В, — і всі виміри
     * поїдуть у смітник, жодного разу не поскаржившись. */
    uint8_t qtx[1u + ADS1220_REG_COUNT];
    uint8_t qrx[1u + ADS1220_REG_COUNT] = { 0u };

    qtx[0] = CMD_RREG(0u, ADS1220_REG_COUNT);
    for (size_t i = 1u; i < sizeof qtx; ++i) {
        qtx[i] = 0xFFu; /* під час читання вміст DIN чип ігнорує */
    }
    if (!xfer(qtx, qrx, sizeof qtx)) {
        return ADS1220_ERR_SPI;
    }

    for (size_t i = 0u; i < ADS1220_REG_COUNT; ++i) {
        if (qrx[i + 1u] != k_config[i]) {
            return ADS1220_ERR_CONFIG;
        }
    }

    return ADS1220_OK;
}

ads1220_status_t ads1220_start(void)
{
    return send_command(CMD_START);
}

ads1220_status_t ads1220_read(int32_t *code_out)
{
    if (code_out == NULL) {
        return ADS1220_ERR_CONFIG;
    }

    uint32_t started = board_millis();
    while (!board_adc_data_ready()) {
        /* Різниця беззнакових коректна й на переповненні лічильника. */
        if ((uint32_t)(board_millis() - started) > ADS1220_DRDY_TIMEOUT_MS) {
            return ADS1220_ERR_TIMEOUT;
        }
    }

    uint8_t tx[4] = { CMD_RDATA, 0u, 0u, 0u };
    uint8_t rx[4] = { 0u };

    if (!xfer(tx, rx, sizeof tx)) {
        return ADS1220_ERR_SPI;
    }

    /* Три байти результату йдуть старшим уперед, у доповняльному коді. */
    int32_t code = ((int32_t)rx[1] << 16) | ((int32_t)rx[2] << 8) | (int32_t)rx[3];
    if ((code & 0x00800000L) != 0L) {
        code -= 0x01000000L;
    }

    *code_out = code;

    if (code >= ADS1220_FULL_SCALE || code <= -ADS1220_FULL_SCALE) {
        return ADS1220_ERR_SATURATED;
    }
    return ADS1220_OK;
}

int32_t ads1220_code_to_nanovolts(int32_t code)
{
    /* Повна шкала при підсиленні G дорівнює ±Vref/G. Ділимо опору на
     * підсилення першою дією: добуток коду на 103 125 000 лишається
     * далеко в межах int64, а точності не втрачаємо — 3.3·10⁹ ділиться
     * на 32 без остачі. */
    const int64_t fsr_nv = ADS1220_VREF_NV / ADS1220_GAIN;

    return (int32_t)(((int64_t)code * fsr_nv) / ADS1220_FULL_SCALE);
}

const char *ads1220_strerror(ads1220_status_t status)
{
    switch (status) {
    case ADS1220_OK:            return "усе гаразд";
    case ADS1220_ERR_SPI:       return "обмін SPI не завершився";
    case ADS1220_ERR_TIMEOUT:   return "DRDY мовчить";
    case ADS1220_ERR_CONFIG:    return "конфігурація не записалася";
    case ADS1220_ERR_SATURATED: return "вхід за межами шкали";
    default:                    return "невідомий стан";
    }
}
