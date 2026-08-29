/* mock_bus.h — віртуальний чип у пам'яті комп'ютера.
 *
 * Це не «заглушка, яка щось повертає», а модель кремнію: у неї є адресний
 * простір, реакція на біт автоінкременту, регістри лише для читання,
 * прапорець готовності даних, який гасне після забирання відліку, — і
 * кнопка, якою тест зумисне ламає шину.
 */
#ifndef MOCK_BUS_H
#define MOCK_BUS_H

#include <stdbool.h>
#include <stdint.h>

#include "chip_driver.h"

#define MOCK_REG_COUNT     128
#define MOCK_MAX_WRITE_LOG 64

/* Один зафіксований байт запису. applied = false означає, що адреса
 * належить регістру лише для читання й кремній цей байт проковтнув мовчки:
 * саме так виглядає найпідступніша помилка в бітових масках. */
typedef struct {
    uint32_t seq; /* наскрізний номер транзакції, у якій стався запис */
    uint8_t  reg;
    uint8_t  val;
    bool     applied;
} mock_write_entry_t;

typedef struct {
    uint8_t  dev_addr; /* адреса, на яку віртуальний чип відгукується */
    uint8_t  registers[MOCK_REG_COUNT];

    /* Журнал транзакцій запису */
    mock_write_entry_t write_log[MOCK_MAX_WRITE_LOG];
    uint32_t write_count;    /* скільки байтів записів зафіксовано в журналі */
    uint32_t log_overflow;   /* скільки не влізло: журнал не бреше про це    */

    /* Лічильники транзакцій */
    uint32_t seq;
    uint32_t read_transactions;
    uint32_t write_transactions;

    /* Генератор апаратних збоїв */
    int32_t  fail_reads_countdown;  /* стільки найближчих читань дадуть збій */
    int32_t  fail_writes_countdown; /* те саме для записів                   */
    bool     nack_device_address;   /* чипа на шині нема: NACK на адресу     */
    uint16_t break_read_at_byte;    /* одноразовий обрив пакетного читання   */
} mock_bus_ctx_t;

/* Скидає стан і садить віртуальний чип на задану адресу. Заводський
 * ідентифікатор виставляється сам — тест псує його явно, коли треба. */
void mock_bus_reset(mock_bus_ctx_t *mock, uint8_t dev_addr);

/* Прямий доступ до кремнію повз шину — так тест грає роль фізики. */
void    mock_poke(mock_bus_ctx_t *mock, uint8_t reg, uint8_t value);
uint8_t mock_peek(const mock_bus_ctx_t *mock, uint8_t reg);

/* Генератор синтетичних даних: сирі відліки або одразу прискорення в g
 * для заданого діапазону повної шкали. Обидва підіймають прапорець ZYXDA. */
void mock_set_raw_xyz(mock_bus_ctx_t *mock, int16_t x, int16_t y, int16_t z);
void mock_set_accel_g(mock_bus_ctx_t *mock, uint8_t range_g,
                      float gx, float gy, float gz);

/* Розбір журналу: останнє записане в регістр значення й кількість спроб. */
bool     mock_last_write(const mock_bus_ctx_t *mock, uint8_t reg, uint8_t *value);
uint32_t mock_writes_to(const mock_bus_ctx_t *mock, uint8_t reg);

/* Реалізація контракту chip_bus_ops_t. */
int32_t mock_bus_read(void *user_ctx, uint8_t dev_addr,
                      uint8_t reg, uint8_t *data, uint16_t len);
int32_t mock_bus_write(void *user_ctx, uint8_t dev_addr,
                       uint8_t reg, const uint8_t *data, uint16_t len);
void    mock_delay_ms(uint32_t ms);

/* Готова таблиця для передавання в chip_init(). */
const chip_bus_ops_t *mock_bus_ops(void);

#endif /* MOCK_BUS_H */
