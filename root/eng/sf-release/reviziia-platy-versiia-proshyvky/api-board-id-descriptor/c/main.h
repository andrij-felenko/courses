#ifndef BOARD_ID_API_H
#define BOARD_ID_API_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BOARD_ID_MAGIC 0x424F5244U

/* Коди повернення підсистеми ідентифікації */
typedef enum {
    BOARD_ID_OK               =  0,
    BOARD_ID_ERR_I2C_FAULT    = -1,
    BOARD_ID_ERR_BAD_MAGIC    = -2,
    BOARD_ID_ERR_CRC_MISMATCH = -3,
    BOARD_ID_ERR_UNSUPPORTED  = -4,
    BOARD_ID_ERR_CORRUPT_TLV  = -5
} board_id_status_t;

/* Розпакована структура параметрів плати */
typedef struct {
    uint16_t hw_revision;        /* Формат: Major.Minor (0x0200 = Rev B) */
    uint16_t bom_variant;       /* Варіант комплектації сенсорів */
    char serial[17];            /* Null-terminated ASCII рядок */
    uint8_t mac[6];             /* 48-бітний MAC-ідентифікатор */
    uint16_t vref_calib_mv;     /* Калібрована напруга опорного джерела */
    int8_t imu_matrix[9];       /* Матриця трансформації осей IMU */
} board_info_t;

/**
 * @brief Зчитує дескриптор з EEPROM, перевіряє цілісність CRC16 та розпаковує теги.
 * 
 * @param[out] out_info Вказівник на структуру, куди записуються розпарсені параметри.
 * @return BOARD_ID_OK у разі успіху, або від'ємний код помилки.
 */
board_id_status_t board_id_read_and_validate(board_info_t *out_info);

/**
 * @brief Повертає бітову маску апаратних можливостей для зазначеної ревізії.
 */
uint32_t board_id_get_capabilities(uint16_t hw_rev);

#define BOARD_CAP_HAS_IMU_BMI270   (1U << 0)
#define BOARD_CAP_HAS_FLASH_MX25L  (1U << 1)
#define BOARD_CAP_HAS_CAN_FD       (1U << 2)
#define BOARD_CAP_HAS_SECURE_CHIP  (1U << 3)

#ifdef __cplusplus
}
#endif

#endif /* BOARD_ID_API_H */
