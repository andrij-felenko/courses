#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MLX90614_I2C_ADDR       0x5A
#define MLX90614_CMD_RAM_TA     0x06
#define MLX90614_CMD_RAM_TOBJ1  0x07

typedef enum {
    IR_STATUS_OK = 0,
    IR_STATUS_ERR_BUS,
    IR_STATUS_ERR_PEC,
    IR_STATUS_ERR_OVERFLOW,
    IR_STATUS_ERR_INVALID_PARAM
} ir_status_t;

typedef struct {
    uint8_t i2c_addr;
    float emissivity;          // 0.01f .. 1.0f
    float reflected_temp_c;    // температура відбитого фону, °C
    bool use_reflected_comp;   // прапорець увімкнення компенсації T_amb
} ir_thermometer_t;

// Низькорівневий інтерфейс платформи (реалізується під конкретний MCU)
extern bool i2c_master_transmit(uint8_t addr, const uint8_t *data, uint16_t len);
extern bool i2c_master_receive(uint8_t addr, uint8_t *data, uint16_t len);

// Розрахунок апаратного PEC (CRC-8 з поліномом x^8 + x^2 + x^1 + 1, poly = 0x07)
static uint8_t mlx90614_crc8_byte(uint8_t crc, uint8_t byte) {
    crc ^= byte;
    for (uint8_t i = 0; i < 8; i++) {
        if (crc & 0x80) {
            crc = (uint8_t)((crc << 1) ^ 0x07);
        } else {
            crc <<= 1;
        }
    }
    return crc;
}

// Зчитування 16-бітного регістра RAM з перевіркою контрольної суми PEC
static ir_status_t mlx90614_read_ram_reg(uint8_t i2c_addr, uint8_t reg_cmd, uint16_t *out_val) {
    uint8_t tx_buf[1] = { reg_cmd };
    uint8_t rx_buf[3] = { 0 }; // LSB, MSB, PEC

    if (!i2c_master_transmit(i2c_addr, tx_buf, 1)) {
        return IR_STATUS_ERR_BUS;
    }
    if (!i2c_master_receive(i2c_addr, rx_buf, 3)) {
        return IR_STATUS_ERR_BUS;
    }

    // Перевірка PEC за стандартом SMBus:
    // CRC охоплює: [Addr_W] + [Command] + [Addr_R] + [Data_LSB] + [Data_MSB]
    uint8_t calc_pec = 0;
    calc_pec = mlx90614_crc8_byte(calc_pec, (uint8_t)(i2c_addr << 1));        // Write Addr (0xB4)
    calc_pec = mlx90614_crc8_byte(calc_pec, reg_cmd);                          // Command
    calc_pec = mlx90614_crc8_byte(calc_pec, (uint8_t)((i2c_addr << 1) | 1));  // Read Addr (0xB5)
    calc_pec = mlx90614_crc8_byte(calc_pec, rx_buf[0]);                        // Data LSB
    calc_pec = mlx90614_crc8_byte(calc_pec, rx_buf[1]);                        // Data MSB

    if (calc_pec != rx_buf[2]) {
        return IR_STATUS_ERR_PEC;
    }

    uint16_t raw = (uint16_t)(rx_buf[0] | ((uint16_t)rx_buf[1] << 8));
    if (raw & 0x8000) { // Старший біт сигналізує про апаратну помилку або переповнення
        return IR_STATUS_ERR_OVERFLOW;
    }

    *out_val = raw;
    return IR_STATUS_OK;
}

// Ініціалізація структури драйвера
ir_status_t ir_thermometer_init(ir_thermometer_t *dev, uint8_t i2c_addr, float emissivity) {
    if (!dev || emissivity <= 0.01f || emissivity > 1.0f) {
        return IR_STATUS_ERR_INVALID_PARAM;
    }
    dev->i2c_addr = i2c_addr;
    dev->emissivity = emissivity;
    dev->reflected_temp_c = 25.0f;
    dev->use_reflected_comp = false;
    return IR_STATUS_OK;
}

// Зчитування температури навколишнього середовища (кристала сенсора), °C
ir_status_t ir_read_ambient_temp(ir_thermometer_t *dev, float *temp_c) {
    if (!dev || !temp_c) return IR_STATUS_ERR_INVALID_PARAM;

    uint16_t raw_ta = 0;
    ir_status_t status = mlx90614_read_ram_reg(dev->i2c_addr, MLX90614_CMD_RAM_TA, &raw_ta);
    if (status != IR_STATUS_OK) return status;

    // Розрахунок за паспортом: крок 0.02 K, відлік від 0 K
    float t_kelvin = (float)raw_ta * 0.02f;
    *temp_c = t_kelvin - 273.15f;
    return IR_STATUS_OK;
}

// Зчитування температури об'єкта з динамічною корекцією ε та відбитого фону T_amb
ir_status_t ir_read_object_temp(ir_thermometer_t *dev, float *temp_c) {
    if (!dev || !temp_c) return IR_STATUS_ERR_INVALID_PARAM;

    uint16_t raw_tobj = 0;
    ir_status_t status = mlx90614_read_ram_reg(dev->i2c_addr, MLX90614_CMD_RAM_TOBJ1, &raw_tobj);
    if (status != IR_STATUS_OK) return status;

    // Первинна радіаційна температура, виміряна сенсором (K)
    float t_rad_k = (float)raw_tobj * 0.02f;

    // Якщо випромінювальна здатність близька до 1.0 та корекція фону вимкнена
    if (dev->emissivity >= 0.999f && !dev->use_reflected_comp) {
        *temp_c = t_rad_k - 273.15f;
        return IR_STATUS_OK;
    }

    // Радіаційний перерахунок:
    // E_meas = T_rad^4 = ε · T_obj^4 + (1 - ε) · T_amb^4
    // T_obj = ((T_rad^4 - (1 - ε) · T_amb^4) / ε)^(1/4)
    float eps = dev->emissivity;
    float t_amb_k;

    if (dev->use_reflected_comp) {
        t_amb_k = dev->reflected_temp_c + 273.15f;
    } else {
        // Якщо точна температура фону не задана, беремо власну температуру сенсора
        float t_sensor_c = 25.0f;
        ir_read_ambient_temp(dev, &t_sensor_c);
        t_amb_k = t_sensor_c + 273.15f;
    }

    double t_rad_4 = pow((double)t_rad_k, 4.0);
    double t_amb_4 = pow((double)t_amb_k, 4.0);

    double num = t_rad_4 - (1.0 - (double)eps) * t_amb_4;
    if (num <= 0.0) {
        // Об'єкт настільки холодний або низькоемісійний, що сигнал нижче фонового порогу
        return IR_STATUS_ERR_OVERFLOW;
    }

    double t_obj_k = pow(num / (double)eps, 0.25);
    *temp_c = (float)(t_obj_k - 273.15);
    return IR_STATUS_OK;
}
