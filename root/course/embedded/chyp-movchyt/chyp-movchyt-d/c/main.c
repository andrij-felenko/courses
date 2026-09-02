/* Оживлення шини: сканер адрес I2C і розбір пастки «7 біт проти 8 біт».
   Прошивка нічого не налаштовує в сенсорі — вона лише з'ясовує, хто взагалі
   озивається, і чи можна вірити тому, що озвалося. */
#include <stdio.h>

#include "i2c_scan.h"
#include "stm32f4xx_hal.h"

I2C_HandleTypeDef hi2c1;

void SystemClock_Config(void); /* із згенерованого CubeMX модуля */
void Error_Handler(void);

/* Підказка «що зазвичай сидить за цією адресою» — саме підказка: збіги
   адрес у різних родин мікросхем цілком звичайні, і саме вони збивають
   з пантелику, коли шукаєш свій сенсор. */
typedef struct {
    uint8_t addr7;
    const char *text;
} addr_hint_t;

static const addr_hint_t kHints[] = {
    { 0x0D, "QMC5883L (магнітометр)" },
    { 0x1E, "HMC5883L (магнітометр)" },
    { 0x23, "BH1750 (люксметр)" },
    { 0x27, "PCF8574 (розширювач портів, типовий модуль LCD)" },
    { 0x39, "APDS-9960 (жести й освітленість)" },
    { 0x3C, "SSD1306 (OLED-дисплей)" },
    { 0x40, "INA219 (монітор струму)" },
    { 0x48, "ADS1115 (зовнішній АЦП)" },
    { 0x50, "AT24Cxx (EEPROM, займає весь блок 0x50..0x57)" },
    { 0x53, "ADXL345 (акселерометр; конфлікт з блоком EEPROM)" },
    { 0x5A, "MLX90614 (безконтактний термометр)" },
    { 0x68, "MPU6050 з AD0=0 або DS3231 (годинник)" },
    { 0x69, "MPU6050 з AD0=1" },
    { 0x76, "BMP280/BME280 з SDO=0" },
    { 0x77, "BMP280/BME280 з SDO=1" },
};

static const char *hint_for(uint8_t addr7)
{
    for (size_t i = 0; i < sizeof kHints / sizeof kHints[0]; ++i) {
        if (kHints[i].addr7 == addr7) {
            return kHints[i].text;
        }
    }
    return "";
}

static void init_i2c(void)
{
    hi2c1.Instance = I2C1;
    /* Для першого оживлення беремо 100 кГц: на 400 кГц завалені фронти
       вбивають кадр раніше, ніж ми встигнемо побачити ACK. */
    hi2c1.Init.ClockSpeed = 100000;
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.OwnAddress2 = 0;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    /* Ведений має право притримати SCL: заборонити розтягування такту
       означає обірвати обмін з повільним АЦП чи криптомікросхемою. */
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;

    if (HAL_I2C_Init(&hi2c1) != HAL_OK) {
        Error_Handler();
    }
}

/* Даташити друкують адресу по-різному: одні 7-бітну (0x68), інші вже
   зсунуті байти кадру (0xD0/0xD1). Розбираємо число, перш ніж комусь
   його віддати, — інакше бібліотека зсуне його вдруге. */
static void explain_datasheet_value(uint8_t printed)
{
    if (printed > 0x7Fu) {
        const uint8_t real7 = (uint8_t)(printed >> 1);
        const uint8_t twice = (uint8_t)((uint8_t)(printed << 1) >> 1);
        printf("0x%02X — це вже байт кадру, а не адреса: чіп сидить на 0x%02X.\r\n",
               printed, real7);
        printf("  Другий зсув перетворив би його на 0x%02X — стукали б у чужу EEPROM.\r\n",
               twice);
        return;
    }
    if (printed < I2C_ADDR_FIRST || printed > I2C_ADDR_LAST) {
        printf("0x%02X — службовий діапазон стандарту, пристрою тут бути не може.\r\n",
               printed);
        return;
    }
    printf("0x%02X — 7-бітна адреса: у кадрі запис 0x%02X, читання 0x%02X.\r\n",
           printed, (uint8_t)(printed << 1), (uint8_t)((printed << 1) | 1u));
    printf("  Wire / ESP-IDF / i2c-dev беруть 0x%02X, STM32 HAL — 0x%02X.\r\n",
           printed, (uint8_t)(printed << 1));
}

static void print_report(const i2c_scan_report_t *report)
{
    printf("\r\n--- Прохід шини: опитано %u адрес, збоїв %u ---\r\n",
           (unsigned)report->probed, (unsigned)report->errors);

    if (report->bus_stuck) {
        printf("ШИНА ЗАВИСЛА: SDA тримається в нулі, START не проходить.\r\n");
        printf("  Ведений не добіг до кінця байта й чекає такту SCL.\r\n");
        printf("  Лікує не перезапуск прошивки, а апаратне вивільнення:\r\n");
        printf("  дев'ять тактів на SCL у режимі GPIO та примусовий STOP.\r\n");
        return;
    }

    if (report->found_count == 0) {
        printf("Тиша на всіх адресах. Спускаємося на рівень нижче:\r\n");
        printf("  1. VDD і GND — осцилографом на НІЖКАХ чіпа, не мультиметром;\r\n");
        printf("  2. nRST / EN — у високому рівні, а не в повітрі;\r\n");
        printf("  3. зовнішні підтяжки 2.2..4.7 кОм на SDA і SCL;\r\n");
        printf("  4. SDA і SCL не переплутані місцями.\r\n");
        return;
    }

    if (i2c_scan_looks_fake(report)) {
        printf("УВАГА: підтверджено %u адрес — стільки пристроїв на шині немає.\r\n",
               (unsigned)report->found_count);
        printf("  Замкнена на землю SDA дає ACK на кожній адресі.\r\n");
    }

    for (uint8_t i = 0; i < report->found_count; ++i) {
        const i2c_device_t *dev = &report->found[i];
        printf("0x%02X  запис 0x%02X  читання 0x%02X  %s\r\n",
               dev->addr7, dev->write_byte, dev->read_byte, hint_for(dev->addr7));
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    init_i2c();

    printf("\r\n=== Сканер шини I2C ===\r\n");
    explain_datasheet_value(0x68); /* так адресу друкує один даташит */
    explain_datasheet_value(0xD0); /* а так — інший, і це те саме залізо */

    i2c_scan_report_t report;
    for (;;) {
        (void)i2c_scan(&hi2c1, &report);
        print_report(&report);
        HAL_Delay(2000);
    }
}

void Error_Handler(void)
{
    __disable_irq();
    for (;;) {
    }
}
