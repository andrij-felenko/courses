#include "i2c.h"

#include <avr/io.h>
#include <util/delay.h>
#include <util/twi.h>

/* SDA і SCL на ATmega328P сидять на порту C. */
#define I2C_SDA_BIT PC4
#define I2C_SCL_BIT PC5

#define I2C_SCL_HZ 400000UL

void i2c_init(void)
{
    /* Внутрішні підтяжки як страховка: на платі мусять стояти зовнішні
     * резистори 2.2…4.7 кОм, слабкої підтяжки МК на довгі дроти не досить. */
    PORTC |= (1 << I2C_SDA_BIT) | (1 << I2C_SCL_BIT);

    TWSR = 0;                                        /* Дільник 1 */
    TWBR = (uint8_t)(((F_CPU / I2C_SCL_HZ) - 16) / 2);
    TWCR = (1 << TWEN);
}

/* Очікування TWINT з обмеженням у часі. */
static i2c_status_t twi_wait(void)
{
    for (uint16_t us = 0; us < I2C_TIMEOUT_US; ++us) {
        if (TWCR & (1 << TWINT)) {
            return I2C_OK;
        }
        _delay_us(1);
    }
    return I2C_ERR_TIMEOUT;
}

static void twi_stop(void)
{
    TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWSTO);

    /* STOP теж може не завершитися на побитій шині — і тут чекаємо з межею. */
    for (uint16_t us = 0; us < I2C_TIMEOUT_US; ++us) {
        if (!(TWCR & (1 << TWSTO))) {
            return;
        }
        _delay_us(1);
    }
}

static i2c_status_t twi_start(uint8_t expected)
{
    TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);

    const i2c_status_t st = twi_wait();
    if (st != I2C_OK) {
        return st;
    }
    return (TW_STATUS == expected) ? I2C_OK : I2C_ERR_BUS;
}

/* Передавання одного байта (адреса або дані) з очікуваним статусом ACK. */
static i2c_status_t twi_write_byte(uint8_t data, uint8_t expected)
{
    TWDR = data;
    TWCR = (1 << TWINT) | (1 << TWEN);

    const i2c_status_t st = twi_wait();
    if (st != I2C_OK) {
        return st;
    }
    if (TW_STATUS != expected) {
        /* Найчастіша причина — веденого просто немає на цій адресі. */
        return I2C_ERR_NACK;
    }
    return I2C_OK;
}

static i2c_status_t twi_read_byte(uint8_t *dst, uint8_t ack)
{
    TWCR = (1 << TWINT) | (1 << TWEN) | (ack ? (1 << TWEA) : 0);

    const i2c_status_t st = twi_wait();
    if (st != I2C_OK) {
        return st;
    }

    const uint8_t expected = ack ? TW_MR_DATA_ACK : TW_MR_DATA_NACK;
    if (TW_STATUS != expected) {
        return I2C_ERR_BUS;
    }

    *dst = TWDR;
    return I2C_OK;
}

i2c_status_t i2c_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t value)
{
    i2c_status_t st = twi_start(TW_START);
    if (st != I2C_OK) goto fail;

    st = twi_write_byte((uint8_t)(dev_addr << 1) | TW_WRITE, TW_MT_SLA_ACK);
    if (st != I2C_OK) goto fail;

    st = twi_write_byte(reg, TW_MT_DATA_ACK);
    if (st != I2C_OK) goto fail;

    st = twi_write_byte(value, TW_MT_DATA_ACK);
    if (st != I2C_OK) goto fail;

    twi_stop();
    return I2C_OK;

fail:
    /* Шину віддаємо в будь-якому разі: недоведений обмін залишив би SDA
     * притиснутою, і наступна спроба почалася б із зависання. */
    twi_stop();
    return st;
}

i2c_status_t i2c_read_regs(uint8_t dev_addr, uint8_t reg, uint8_t *dst, uint8_t len)
{
    if (len == 0) {
        return I2C_OK;
    }

    /* Фаза запису: називаємо ведному адресу регістра, з якого читати. */
    i2c_status_t st = twi_start(TW_START);
    if (st != I2C_OK) goto fail;

    st = twi_write_byte((uint8_t)(dev_addr << 1) | TW_WRITE, TW_MT_SLA_ACK);
    if (st != I2C_OK) goto fail;

    st = twi_write_byte(reg, TW_MT_DATA_ACK);
    if (st != I2C_OK) goto fail;

    /* Повторний START без відпускання шини — інакше між фазами вклиниться
     * чужий майстер і лічильник регістра з'їде. */
    st = twi_start(TW_REP_START);
    if (st != I2C_OK) goto fail;

    st = twi_write_byte((uint8_t)(dev_addr << 1) | TW_READ, TW_MR_SLA_ACK);
    if (st != I2C_OK) goto fail;

    for (uint8_t i = 0; i < len; ++i) {
        /* Останній байт квитуємо NACK — це сигнал ведному замовкнути. */
        const uint8_t ack = (i + 1 < len) ? 1 : 0;
        st = twi_read_byte(&dst[i], ack);
        if (st != I2C_OK) goto fail;
    }

    twi_stop();
    return I2C_OK;

fail:
    twi_stop();
    return st;
}

void i2c_bus_recover(void)
{
    /* Відпускаємо апарат TWI: далі смикаємо ніжки руками. */
    TWCR = 0;

    /* SCL — вихід, SDA лишається входом із підтяжкою, щоб бачити, коли
     * ведений нарешті відпустить лінію. */
    DDRC  |=  (1 << I2C_SCL_BIT);
    DDRC  &= ~(1 << I2C_SDA_BIT);
    PORTC |=  (1 << I2C_SDA_BIT) | (1 << I2C_SCL_BIT);

    /* Дев'ять імпульсів — рівно на байт плюс такт квитанції: скільки б
     * бітів ведений не недоговорив, за дев'ять він договорить усі. */
    for (uint8_t i = 0; i < 9; ++i) {
        if (PINC & (1 << I2C_SDA_BIT)) {
            break;   /* SDA вже висока — шина вільна */
        }
        PORTC &= ~(1 << I2C_SCL_BIT);
        _delay_us(5);
        PORTC |=  (1 << I2C_SCL_BIT);
        _delay_us(5);
    }

    /* Ручний STOP: на високому SCL переводимо SDA з низького в високий. */
    DDRC  |=  (1 << I2C_SDA_BIT);
    PORTC &= ~(1 << I2C_SDA_BIT);
    _delay_us(5);
    PORTC |=  (1 << I2C_SCL_BIT);
    _delay_us(5);
    PORTC |=  (1 << I2C_SDA_BIT);
    _delay_us(5);

    /* Ніжки назад під керування TWI. */
    DDRC &= ~((1 << I2C_SDA_BIT) | (1 << I2C_SCL_BIT));

    i2c_init();
}
