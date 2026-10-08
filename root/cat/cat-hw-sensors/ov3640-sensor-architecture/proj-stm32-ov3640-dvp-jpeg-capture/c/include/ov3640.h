#ifndef OV3640_H
#define OV3640_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file ov3640.h
 * @brief Оголошення низькорівневого C-драйвера сенсора зображення Omnivision OV3640.
 *
 * Драйвер підтримує ініціалізацію через послідовну шину SCCB, налаштування роздільної
 * здатності (VGA, 1080p, QXGA), вибір форматів вихідного потоку даних (YUV422, JPEG),
 * а також керування лініями живлення (PWDN) та системного скидання (RESET).
 */

/* Базова 7-бітна та 8-бітна адреса шини SCCB для сенсора OV3640 */
#define OV3640_SCCB_ADDR_7BIT          0x3C
#define OV3640_SCCB_ADDR_WRITE         0x78
#define OV3640_SCCB_ADDR_READ          0x79

/* Очікуваний ідентифікатор мікросхеми OV3640 (Chip ID) */
#define OV3640_CHIP_ID                 0x3640

/* Основні регістри системного керування та конфігурації OV3640 (16-бітна адресація) */
#define OV3640_REG_CHIP_ID_HIGH        0x300A
#define OV3640_REG_CHIP_ID_LOW         0x300B
#define OV3640_REG_SYS_RESET           0x3010
#define OV3640_REG_SYS_CLK_CTRL        0x3011
#define OV3640_REG_SYS_CTRL0           0x3012
#define OV3640_REG_FORMAT_CTRL         0x3600
#define OV3640_REG_DSP_CTRL            0x5000
#define OV3640_REG_GAMMA_CTRL_BASE     0x5300
#define OV3640_REG_COLOR_MATRIX_BASE   0x5380
#define OV3640_REG_PCLK_DIV            0x300D

/**
 * @brief Перелічення доступних роздільних здатностей матриці.
 */
typedef enum {
    OV3640_RES_VGA = 0,    /**< 640 x 480 пікселів */
    OV3640_RES_1080P,      /**< 1920 x 1080 пікселів */
    OV3640_RES_QXGA        /**< 2048 x 1536 пікселів (максимальна роздільна здатність) */
} ov3640_res_t;

/**
 * @brief Перелічення підтримки вихідних форматів даних.
 */
typedef enum {
    OV3640_FMT_YUV422 = 0, /**< Нестиснутий формат YUV 4:2:2 (2 байти на піксель) */
    OV3640_FMT_JPEG        /**< Стиснутий бінарний потік JPEG з маркерами SOI/EOI */
} ov3640_format_t;

/**
 * @brief Коди результатів виконання функцій драйвера OV3640.
 */
typedef enum {
    OV3640_OK = 0,              /**< Операцію виконано успішно */
    OV3640_ERR_PARAM = -1,      /**< Некоректні вхідні параметри */
    OV3640_ERR_SCCB = -2,       /**< Помилка обміну даними по шині SCCB */
    OV3640_ERR_ID_MISMATCH = -3,/**< Ідентифікатор мікросхеми не відповідає 0x3640 */
    OV3640_ERR_TIMEOUT = -4     /**< Перевищено тайм-аут апаратного відгуку */
} ov3640_status_t;

/**
 * @brief Структурна пара регістр-значення для масового конфігурування.
 */
typedef struct {
    uint16_t reg; /**< 16-бітна адреса регістру OV3640 */
    uint8_t val;  /**< 8-бітне значення для запису */
} ov3640_reg_val_t;

/**
 * @brief Абстракція периферійного інтерфейсу вводу/виводу та шини SCCB.
 */
typedef struct {
    uint8_t sccb_addr; /**< 8-бітна адреса SCCB пристрою */
    ov3640_status_t (*sccb_write)(uint8_t dev_addr, uint16_t reg, uint8_t data);
    ov3640_status_t (*sccb_read)(uint8_t dev_addr, uint16_t reg, uint8_t *data);
    void (*set_pwdn)(bool active);
    void (*set_reset)(bool active);
    void (*delay_ms)(uint32_t ms);
} ov3640_io_t;

/**
 * @brief Контекстний дескриптор сенсора OV3640.
 */
typedef struct {
    ov3640_io_t io;            /**< Апаратні інтерфейси вводу/виводу */
    ov3640_res_t resolution;   /**< Поточна роздільна здатність */
    ov3640_format_t format;    /**< Поточний формат вихідних даних */
    bool is_initialized;       /**< Прапор успішної ініціалізації */
} ov3640_handle_t;

/* --- Прототипи публічних функцій --- */

/**
 * @brief Ініціалізація сенсора OV3640, перевірка Chip ID та завантаження базової конфігурації.
 * @param handle Вказівник на дескриптор сенсора.
 * @param io Налаштовані апаратні функції вводу/виводу та SCCB.
 * @return OV3640_OK у разі успіху, інакше відповідний код помилки.
 */
ov3640_status_t ov3640_init(ov3640_handle_t *handle, const ov3640_io_t *io);

/**
 * @brief Виконання апаратного та програмного скидання OV3640.
 * @param handle Вказівник на дескриптор сенсора.
 * @return OV3640_OK у разі успіху.
 */
ov3640_status_t ov3640_reset(ov3640_handle_t *handle);

/**
 * @brief Керування режимом зниженого енергоспоживання (PWDN).
 * @param handle Вказівник на дескриптор сенсора.
 * @param enable true — увімкнути режим сну, false — нормальна робота.
 * @return OV3640_OK у разі успіху.
 */
ov3640_status_t ov3640_set_power(ov3640_handle_t *handle, bool enable);

/**
 * @brief Зчитування та перевірка ідентифікатора сенсора (0x3640).
 * @param handle Вказівник на дескриптор сенсора.
 * @param chip_id Буфер для збереження вичитаного значення ID.
 * @return OV3640_OK або OV3640_ERR_ID_MISMATCH.
 */
ov3640_status_t ov3640_read_chip_id(ov3640_handle_t *handle, uint16_t *chip_id);

/**
 * @brief Встановлення роздільної здатності кадру.
 * @param handle Вказівник на дескриптор сенсора.
 * @param res Обрана роздільна здатність (VGA, 1080p, QXGA).
 * @return OV3640_OK у разі успіху.
 */
ov3640_status_t ov3640_set_resolution(ov3640_handle_t *handle, ov3640_res_t res);

/**
 * @brief Конфігурування формату вихідного потоку пікселів.
 * @param handle Вказівник на дескриптор сенсора.
 * @param fmt Обраний формат (YUV422 або JPEG).
 * @return OV3640_OK у разі успіху.
 */
ov3640_status_t ov3640_set_format(ov3640_handle_t *handle, ov3640_format_t fmt);

/**
 * @brief Послідовний запис масиву конфігураційних регістрів у сенсор.
 * @param handle Вказівник на дескриптор сенсора.
 * @param list Масив пар адреса-значення.
 * @param count Кількість елементів у масиві.
 * @return OV3640_OK у разі успіху.
 */
ov3640_status_t ov3640_write_reg_list(ov3640_handle_t *handle, const ov3640_reg_val_t *list, size_t count);

#endif /* OV3640_H */
