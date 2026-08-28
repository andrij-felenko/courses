#include <stdint.h>
#include <stdbool.h>

#define TCPC_REG_ROLE_CTRL   0x1A
#define TCPC_REG_CC_STATUS   0x1D
#define SW_REG_CONTROL       0x02

#define CC_STATUS_VRA        0x01
#define CC_STATUS_MASK       0x03

/* Приклад апаратного читання регістрів через I2C */
extern uint8_t tcpc_i2c_read(uint8_t reg);
extern void audio_switch_i2c_write(uint8_t reg, uint8_t val);
extern void audio_codec_enable_dac(bool enable);

/* Обробник переривання підключення від TCPC */
void handle_typec_attach_interrupt(void) {
    uint8_t cc_stat = tcpc_i2c_read(TCPC_REG_CC_STATUS);
    uint8_t cc1 = (cc_stat >> 0) & CC_STATUS_MASK;
    uint8_t cc2 = (cc_stat >> 2) & CC_STATUS_MASK;

    /* Перевіряємо умову AudioAccessory: CC1 == vRa І CC2 == vRa */
    if (cc1 == CC_STATUS_VRA && cc2 == CC_STATUS_VRA) {
        /* 1. Заборонити подачу живлення VBUS і VCONN */
        /* 2. Налаштувати комутатор: увімкнути заряд-помпу та перемкнути DP/DN на ЦАП */
        uint8_t sw_cfg = (1 << 7) |  /* SW_EN: увімкнути ключі */
                         (2 << 5) |  /* USB_AUDIO_SEL: режим аналогового звуку */
                         (1 << 0);   /* NEG_PUMP_EN: увімкнути генератор -3 В */
        audio_switch_i2c_write(SW_REG_CONTROL, sw_cfg);

        /* 3. Запустити вихідний стереокаскад аудіокодека */
        audio_codec_enable_dac(true);
    }
}
