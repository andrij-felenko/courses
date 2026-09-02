/*
 * Модульні тести адаптера на хості: жодного заліза, лише програмний мок
 * шини, який вдає кремній і за командою ламається.
 *
 * Збірка: cc -std=c11 -Wall -Wextra -o test_adapter \
 *            test_adapter.c sensor_adapter.c rtos_port.c vendor/vendor_sensor.c -pthread
 */
#include "sensor_adapter.h"
#include "sys_i2c.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

#define REG_CALIB00   0x88
#define REG_CHIP_ID   0xD0
#define REG_RESET     0xE0
#define REG_STATUS    0xF3
#define REG_CTRL_MEAS 0xF4
#define REG_PRESS_MSB 0xF7

#define NO_FAIL_REG (-1)

/* --- Програмний емулятор чипа на шині --- */

typedef struct {
    uint8_t nvm[256];   /* заводський образ: переживає скидання чипа */
    uint8_t regs[256];  /* робочі регістри: наповнюються з NVM при скиданні */
    /* Прапорці генерації апаратних збоїв. */
    bool nack_all;        /* чип не відповідає взагалі: обрив або немає підтяжок */
    int fail_reg;         /* збій читання конкретного регістрового пакета */
    bool stuck_measuring; /* перетворення ніколи не завершується */
    /* Спостереження. */
    uint32_t reads;
    uint32_t writes;
    uint8_t measuring_left;  /* скільки опитувань статусу ще покажуть «зайнято» */
    uint8_t im_update_left;  /* копіювання NVM після скидання */
} mock_chip_t;

/* Коефіцієнти й ідентифікатор лежать у NVM, тож пишемо їх саме туди:
   м'яке скидання, яке робить драйвер, перезаллє регістри з цього образу. */
static void mock_put_u16(mock_chip_t *m, uint8_t addr, uint16_t value)
{
    m->nvm[addr] = (uint8_t)(value & 0xFFU);
    m->nvm[(uint8_t)(addr + 1U)] = (uint8_t)(value >> 8);
}

/* Двадцятибітний відлік лягає в три регістри, молодші чотири біти — у xlsb. */
static void mock_put_adc(mock_chip_t *m, uint8_t addr, uint32_t adc)
{
    m->nvm[addr] = (uint8_t)(adc >> 12);
    m->nvm[(uint8_t)(addr + 1U)] = (uint8_t)((adc >> 4) & 0xFFU);
    m->nvm[(uint8_t)(addr + 2U)] = (uint8_t)((adc << 4) & 0xF0U);
}

/*
 * Заводський стан примірника: ідентифікатор, коефіцієнти компенсації
 * і сирі відліки. Числа — з прикладу в технічному описі BME280, щоб
 * очікуваний результат можна було звірити з документом виробника.
 */
static void mock_load_defaults(mock_chip_t *m)
{
    memset(m->nvm, 0, sizeof(m->nvm));
    m->nvm[REG_CHIP_ID] = 0x60;

    mock_put_u16(m, REG_CALIB00 + 0,  27504);          /* dig_T1 */
    mock_put_u16(m, REG_CALIB00 + 2,  (uint16_t)26435);
    mock_put_u16(m, REG_CALIB00 + 4,  (uint16_t)-1000);
    mock_put_u16(m, REG_CALIB00 + 6,  36477);          /* dig_P1 */
    mock_put_u16(m, REG_CALIB00 + 8,  (uint16_t)-10685);
    mock_put_u16(m, REG_CALIB00 + 10, (uint16_t)3024);
    mock_put_u16(m, REG_CALIB00 + 12, (uint16_t)2855);
    mock_put_u16(m, REG_CALIB00 + 14, (uint16_t)140);
    mock_put_u16(m, REG_CALIB00 + 16, (uint16_t)-7);
    mock_put_u16(m, REG_CALIB00 + 18, (uint16_t)15500);
    mock_put_u16(m, REG_CALIB00 + 20, (uint16_t)-14600);
    mock_put_u16(m, REG_CALIB00 + 22, (uint16_t)6000);

    mock_put_adc(m, REG_PRESS_MSB, 415148U);      /* ≈ 1006.5 гПа */
    mock_put_adc(m, REG_PRESS_MSB + 3, 519888U);  /* ≈ 25.08 °C */
}

/* Те, що робить чип на команду 0xB6: піднімає регістри із заводського образу. */
static void mock_reset(mock_chip_t *m)
{
    memcpy(m->regs, m->nvm, sizeof(m->regs));
    m->measuring_left = 0U;
    m->im_update_left = 2U;   /* NVM копіюється не миттєво */
}

static bool mock_read(void *ctx, uint8_t dev_addr, uint8_t reg,
                      uint8_t *buf, size_t len)
{
    mock_chip_t *m = (mock_chip_t *)ctx;

    (void)dev_addr;
    if (m->nack_all) {
        return false;
    }
    if (m->fail_reg >= 0 && (int)reg == m->fail_reg) {
        /* Збій посеред транзакції: частина байтів уже пішла, решта — ні. */
        return false;
    }
    m->reads++;

    if (reg == REG_STATUS && len == 1U) {
        uint8_t status = 0U;
        if (m->im_update_left > 0U) {
            m->im_update_left--;
            status |= 0x01U;
        }
        if (m->stuck_measuring) {
            status |= 0x08U;
        } else if (m->measuring_left > 0U) {
            m->measuring_left--;
            status |= 0x08U;
        }
        buf[0] = status;
        return true;
    }

    for (size_t i = 0; i < len; ++i) {
        buf[i] = m->regs[(uint8_t)(reg + i)];
    }
    return true;
}

static bool mock_write(void *ctx, uint8_t dev_addr, uint8_t reg,
                       const uint8_t *buf, size_t len)
{
    mock_chip_t *m = (mock_chip_t *)ctx;

    (void)dev_addr;
    if (m->nack_all) {
        return false;
    }
    m->writes++;

    if (reg == REG_RESET && len == 1U && buf[0] == 0xB6U) {
        mock_reset(m);
        return true;
    }
    for (size_t i = 0; i < len; ++i) {
        m->regs[(uint8_t)(reg + i)] = buf[i];
    }
    /* Команда одиничного вимірювання: чип зайнятий два опитування поспіль. */
    if (reg == REG_CTRL_MEAS && len == 1U && (buf[0] & 0x03U) == 0x01U) {
        m->measuring_left = 2U;
    }
    return true;
}

static void mock_init(mock_chip_t *m, sys_i2c_bus_t *bus)
{
    memset(m, 0, sizeof(*m));
    m->fail_reg = NO_FAIL_REG;
    mock_load_defaults(m);
    mock_reset(m);
    bus->read_reg = mock_read;
    bus->write_reg = mock_write;
    bus->bus_ctx = m;
}

/* --- Самі перевірки --- */

static int g_checks;

static void check(bool cond, const char *what)
{
    g_checks++;
    if (!cond) {
        printf("  ПРОВАЛ: %s\n", what);
        assert(cond);
    }
}

static void test_happy_path(void)
{
    mock_chip_t chip;
    sys_i2c_bus_t bus;
    sensor_adapter_t *adapter = NULL;
    sensor_data_t data;

    mock_init(&chip, &bus);
    check(sensor_adapter_acquire(&bus, 0x76, &adapter) == SYS_OK, "ініціалізація");
    check(sensor_adapter_read(adapter, &data) == SYS_OK, "читання відліку");
    check(data.temperature_centi_deg > 2400 && data.temperature_centi_deg < 2600,
          "температура біля 25 °C");
    check(data.pressure_pa > 99000U && data.pressure_pa < 102000U,
          "тиск біля 1006 гПа");

    chip.writes = 0U;
    sensor_adapter_release(adapter);
    check(chip.writes > 0U, "звільнення пише режим сну в чип");
}

static void test_bus_nack(void)
{
    mock_chip_t chip;
    sys_i2c_bus_t bus;
    sensor_adapter_t *adapter = NULL;

    mock_init(&chip, &bus);
    chip.nack_all = true;
    check(sensor_adapter_acquire(&bus, 0x76, &adapter) == SYS_ERR_COMM,
          "мовчазна шина дає ERR_COMM");
    check(adapter == NULL, "дескриптор не видано");
}

static void test_wrong_chip_id(void)
{
    mock_chip_t chip;
    sys_i2c_bus_t bus;
    sensor_adapter_t *adapter = NULL;

    mock_init(&chip, &bus);
    chip.nvm[REG_CHIP_ID] = 0x00;   /* помилка монтажу: стоїть не той чип */
    check(sensor_adapter_acquire(&bus, 0x76, &adapter) == SYS_ERR_DEVICE,
          "чужий Chip ID дає ERR_DEVICE");
}

static void test_zero_calibration(void)
{
    mock_chip_t chip;
    sys_i2c_bus_t bus;
    sensor_adapter_t *adapter = NULL;

    mock_init(&chip, &bus);
    mock_put_u16(&chip, REG_CALIB00 + 6, 0U);   /* dig_P1 = 0 */
    check(sensor_adapter_acquire(&bus, 0x76, &adapter) == SYS_ERR_CALIB,
          "нульове калібрування спинено до ділення на нуль");
}

static void test_fault_mid_transaction(void)
{
    mock_chip_t chip;
    sys_i2c_bus_t bus;
    sensor_adapter_t *adapter = NULL;
    sensor_data_t data;

    mock_init(&chip, &bus);
    check(sensor_adapter_acquire(&bus, 0x76, &adapter) == SYS_OK, "старт");

    chip.fail_reg = REG_PRESS_MSB;   /* обрив саме на пакеті відліку */
    check(sensor_adapter_read(adapter, &data) == SYS_ERR_COMM,
          "збій у транзакції дає ERR_COMM");
    check(data.temperature_centi_deg == 0 && data.pressure_pa == 0U,
          "вихідний буфер очищено");

    /* Найважливіше: м'ютекс звільнено на помилковому шляху, і наступне
       читання проходить, а не вішає задачу назавжди. */
    chip.fail_reg = NO_FAIL_REG;
    check(sensor_adapter_read(adapter, &data) == SYS_OK,
          "після збою адаптер працює далі");

    sensor_adapter_release(adapter);
}

static void test_measure_timeout(void)
{
    mock_chip_t chip;
    sys_i2c_bus_t bus;
    sensor_adapter_t *adapter = NULL;
    sensor_data_t data;

    mock_init(&chip, &bus);
    check(sensor_adapter_acquire(&bus, 0x76, &adapter) == SYS_OK, "старт");

    chip.stuck_measuring = true;
    check(sensor_adapter_read(adapter, &data) == SYS_ERR_TIMEOUT,
          "зависле перетворення дає ERR_TIMEOUT, а не вічний цикл");

    chip.stuck_measuring = false;
    sensor_adapter_release(adapter);
}

static void test_pool_exhaustion(void)
{
    mock_chip_t chip;
    sys_i2c_bus_t bus;
    sensor_adapter_t *a = NULL;
    sensor_adapter_t *b = NULL;
    sensor_adapter_t *c = NULL;

    mock_init(&chip, &bus);
    check(sensor_adapter_acquire(&bus, 0x76, &a) == SYS_OK, "перший слот");
    check(sensor_adapter_acquire(&bus, 0x77, &b) == SYS_OK, "другий слот");
    check(sensor_adapter_acquire(&bus, 0x78, &c) == SYS_ERR_NO_SLOT,
          "третій слот — відмова, а не мовчазне псування пам'яті");

    sensor_adapter_release(a);
    check(sensor_adapter_acquire(&bus, 0x78, &c) == SYS_OK,
          "звільнений слот повертається в пул");
    sensor_adapter_release(b);
    sensor_adapter_release(c);
}

int main(void)
{
    test_happy_path();
    test_bus_nack();
    test_wrong_chip_id();
    test_zero_calibration();
    test_fault_mid_transaction();
    test_measure_timeout();
    test_pool_exhaustion();

    printf("усі %d перевірок пройдено\n", g_checks);
    return 0;
}
