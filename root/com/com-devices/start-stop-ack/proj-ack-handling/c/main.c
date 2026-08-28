#include <stdint.h>
#include <stdbool.h>

typedef enum {
    I2C_OK = 0,        // усе підтверджено
    I2C_NACK_ADDR,     // на адресу ніхто не озвався → пристрою нема
    I2C_NACK_DATA,     // ведений не прийняв байт даних (зайнятий/збій)
    I2C_BUS_TIMEOUT,   // лінія завмерла → шина зависла
} i2c_status_t;

// --- умовний апаратний шар ---------------------------------------------------
extern void i2c_hw_start(void);                 // видати СТАРТ (або повторний)
extern void i2c_hw_stop(void);                  // видати СТОП
extern bool i2c_hw_write(uint8_t b);            // вислати байт; true == прийшов ACK
extern uint8_t i2c_hw_read(bool ack);           // прийняти байт; ack → ACK, інакше NACK
extern bool i2c_hw_wait_ready(uint32_t to_us);  // чекати готовності лінії; false == таймаут
// -----------------------------------------------------------------------------

// одна спроба: прочитати один байт із регістра reg давача addr7 у *out
static i2c_status_t i2c_read_reg_once(uint8_t addr7, uint8_t reg, uint8_t *out) {
    if (!i2c_hw_wait_ready(1000))      // шина вільна впродовж 1 мс?
        return I2C_BUS_TIMEOUT;        //   ні — хтось тримає лінію

    // -- фаза запису: куди дивитися --
    i2c_hw_start();
    if (!i2c_hw_write((addr7 << 1) | 0)) {   // адреса + W; чекаємо ACK на адресу
        i2c_hw_stop();
        return I2C_NACK_ADDR;                 // ніхто не озвався → пристрою нема
    }
    if (!i2c_hw_write(reg)) {                 // номер регістра; ACK?
        i2c_hw_stop();
        return I2C_NACK_DATA;                 // ведений зайнятий/збій → варто повторити
    }

    // -- повторний СТАРТ, фаза читання: не відпускаючи шину --
    i2c_hw_start();                           // Sr замість STOP+START
    if (!i2c_hw_write((addr7 << 1) | 1)) {   // адреса + R; ACK?
        i2c_hw_stop();
        return I2C_NACK_ADDR;
    }
    *out = i2c_hw_read(false);                // єдиний байт → ведучий дає NACK (false)
    i2c_hw_stop();                            // NACK + СТОП = «досить»
    return I2C_OK;
}

// обгортка з повтором: тимчасові збої — повторюємо, сталі — ні
i2c_status_t i2c_read_reg(uint8_t addr7, uint8_t reg, uint8_t *out) {
    i2c_status_t st = I2C_OK;
    for (int attempt = 0; attempt < 3; attempt++) {
        st = i2c_read_reg_once(addr7, reg, out);
        if (st == I2C_OK || st == I2C_NACK_ADDR)
            return st;                 // успіх або «пристрою нема» — повтор не поможе
        delay_us(200);                 // NACK на даних / таймаут — даємо отямитися
    }
    return st;                         // вичерпали спроби — повертаємо останню причину
}
