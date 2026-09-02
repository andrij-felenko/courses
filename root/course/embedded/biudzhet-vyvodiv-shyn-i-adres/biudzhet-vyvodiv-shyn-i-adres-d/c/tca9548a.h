#ifndef TCA9548A_H
#define TCA9548A_H

#include "platform.h"

#define TCA9548A_ADDR_BASE 0x70u  /* A2..A0 = 000; діапазон адрес 0x70..0x77 */
#define TCA9548A_CHANNELS  8u
#define TCA9548A_ALL_OFF   0x00u
#define TCA9548A_MAX_MUX   8u     /* 8 комутаторів × 8 каналів = 64 субшини */

/* Один комутатор на головній шині. shadow — тіньова копія байта керування:
   вона рятує від зайвої транзакції на 45 мкс там, де канал уже відкритий. */
typedef struct {
    uint8_t addr;
    uint8_t reset_pin;    /* PIN_NONE, якщо ~RESET прив'язаний до живлення */
    uint8_t shadow;
    bool    shadow_valid;
} tca9548a_t;

io_status_t tca9548a_init(tca9548a_t *mux, uint8_t addr, uint8_t reset_pin);

/* Відкриває рівно один канал 0..7 (усі інші ключі розмикаються). */
io_status_t tca9548a_select(tca9548a_t *mux, uint8_t channel);

/* Розмикає всі ключі: субшини з їхньою ємністю й адресами зникають із шини. */
io_status_t tca9548a_disable(tca9548a_t *mux);

/* Читання самого комутатора повертає його байт керування — так перевіряють,
   що ключі справді там, де ми думаємо. */
io_status_t tca9548a_readback(const tca9548a_t *mux, uint8_t *mask);

void tca9548a_hard_reset(tca9548a_t *mux);

/* Регістрове читання давача, який сидить на вказаному каналі. */
io_status_t tca9548a_read_reg(tca9548a_t *mux, uint8_t channel, uint8_t dev,
                              uint8_t reg, uint8_t *buf, uint8_t len);

/* Банк комутаторів на спільній головній шині: наскрізна нумерація субшин. */
typedef struct {
    tca9548a_t *mux;
    uint8_t     count;    /* 1..TCA9548A_MAX_MUX */
} mux_bank_t;

io_status_t mux_bank_select(mux_bank_t *bank, uint8_t subbus);
io_status_t mux_bank_isolate(mux_bank_t *bank);

/* Обходить усі субшини й читає той самий регістр однакових давачів.
   out — масив на count*8 записів по len байтів. Повертає кількість успішно
   опитаних давачів, а біти невдалих субшин кладе у fail_mask. */
uint8_t mux_bank_poll(mux_bank_t *bank, uint8_t dev, uint8_t reg,
                      uint8_t *out, uint8_t len, uint64_t *fail_mask);

#endif /* TCA9548A_H */
