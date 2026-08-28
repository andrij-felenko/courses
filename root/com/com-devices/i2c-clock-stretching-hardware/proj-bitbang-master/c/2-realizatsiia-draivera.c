#include <stdint.h>
#include <stdbool.h>

// Типи помилок шини I2C
typedef enum {
    I2C_BB_OK = 0,
    I2C_BB_ERROR_NACK = -1,
    I2C_BB_ERROR_SCL_TIMEOUT = -2,
    I2C_BB_ERROR_BUS_BUSY = -3
} i2c_bb_status_t;

// Структура конфігурації апаратних портів та функцій затримки
typedef struct {
    void (*set_scl_low)(void);
    void (*set_scl_high_z)(void);
    bool (*read_scl)(void);
    void (*set_sda_low)(void);
    void (*set_sda_high_z)(void);
    bool (*read_sda)(void);
    void (*delay_half_period_us)(void);
    uint32_t (*get_tick_us)(void);
    uint32_t stretch_timeout_us;
} i2c_bitbang_bus_t;

// Очікування переходу лінії SCL у стан логічної одиниці з таймаутом
static i2c_bb_status_t i2c_bb_wait_scl_high(const i2c_bitbang_bus_t *bus) {
    bus->set_scl_high_z();
    uint32_t start_time = bus->get_tick_us();
    
    // Цикл опитування стану лінії SCL
    while (!bus->read_scl()) {
        uint32_t elapsed = bus->get_tick_us() - start_time;
        if (elapsed >= bus->stretch_timeout_us) {
            return I2C_BB_ERROR_SCL_TIMEOUT;
        }
    }
    return I2C_BB_OK;
}

// Формування умови START на шині
i2c_bb_status_t i2c_bb_start(const i2c_bitbang_bus_t *bus) {
    bus->set_sda_high_z();
    if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
        return I2C_BB_ERROR_SCL_TIMEOUT;
    }
    bus->delay_half_period_us();
    
    if (!bus->read_sda()) {
        return I2C_BB_ERROR_BUS_BUSY;
    }
    
    // Спад SDA при високому рівні SCL -> умова START
    bus->set_sda_low();
    bus->delay_half_period_us();
    bus->set_scl_low();
    bus->delay_half_period_us();
    return I2C_BB_OK;
}

// Формування умови STOP на шині
i2c_bb_status_t i2c_bb_stop(const i2c_bitbang_bus_t *bus) {
    bus->set_sda_low();
    bus->delay_half_period_us();
    
    if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
        return I2C_BB_ERROR_SCL_TIMEOUT;
    }
    bus->delay_half_period_us();
    
    // Наростання SDA при високому рівні SCL -> умова STOP
    bus->set_sda_high_z();
    bus->delay_half_period_us();
    return I2C_BB_OK;
}

// Запис одного байта з контролем розтягування та квитанції ACK/NACK
i2c_bb_status_t i2c_bb_write_byte(const i2c_bitbang_bus_t *bus, uint8_t byte) {
    for (uint8_t i = 0; i < 8; i++) {
        if (byte & 0x80) {
            bus->set_sda_high_z();
        } else {
            bus->set_sda_low();
        }
        byte <<= 1;
        bus->delay_half_period_us();
        
        // Піднімаємо SCL і перевіряємо, чи ведений не заблокував такт
        if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
            return I2C_BB_ERROR_SCL_TIMEOUT;
        }
        bus->delay_half_period_us();
        bus->set_scl_low();
    }
    
    // 9-й такт: Зчитування біта підтвердження ACK від веденого
    bus->set_sda_high_z();
    bus->delay_half_period_us();
    
    if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
        return I2C_BB_ERROR_SCL_TIMEOUT;
    }
    
    bool nack = bus->read_sda();
    bus->delay_half_period_us();
    bus->set_scl_low();
    bus->delay_half_period_us();
    
    return nack ? I2C_BB_ERROR_NACK : I2C_BB_OK;
}

// Зчитування одного байта з генерацією ACK/NACK
i2c_bb_status_t i2c_bb_read_byte(const i2c_bitbang_bus_t *bus, uint8_t *byte, bool send_ack) {
    uint8_t received = 0;
    bus->set_sda_high_z();
    
    for (uint8_t i = 0; i < 8; i++) {
        received <<= 1;
        bus->delay_half_period_us();
        
        // Ведений виставляє біт даних під час LOW або розтягує SCL
        if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
            return I2C_BB_ERROR_SCL_TIMEOUT;
        }
        
        if (bus->read_sda()) {
            received |= 0x01;
        }
        bus->delay_half_period_us();
        bus->set_scl_low();
    }
    
    *byte = received;
    
    // 9-й такт: Формування відповіді ACK (0) або NACK (1) ведучим
    if (send_ack) {
        bus->set_sda_low();
    } else {
        bus->set_sda_high_z();
    }
    bus->delay_half_period_us();
    
    if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
        return I2C_BB_ERROR_SCL_TIMEOUT;
    }
    bus->delay_half_period_us();
    bus->set_scl_low();
    bus->set_sda_high_z();
    bus->delay_half_period_us();
    
    return I2C_BB_OK;
}

// 9-тактова процедура відновлення завислої шини
void i2c_bb_recover_bus(const i2c_bitbang_bus_t *bus) {
    bus->set_sda_high_z();
    bus->set_scl_high_z();
    bus->delay_half_period_us();
    
    // Генеруємо до 9 імпульсів SCL для виштовхування бітів із веденого
    for (uint8_t i = 0; i < 9; i++) {
        if (bus->read_sda()) {
            break; // Ведений відпустив лінію даних
        }
        bus->set_scl_low();
        bus->delay_half_period_us();
        bus->set_scl_high_z();
        bus->delay_half_period_us();
    }
    
    // Формуємо примусовий STOP
    bus->set_sda_low();
    bus->delay_half_period_us();
    bus->set_scl_high_z();
    bus->delay_half_period_us();
    bus->set_sda_high_z();
    bus->delay_half_period_us();
}
