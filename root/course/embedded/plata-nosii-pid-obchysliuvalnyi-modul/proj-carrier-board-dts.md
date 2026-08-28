# ⚙️ Розробка DTS та динамічних оверлеїв для власної плати-носія

Коли розробник проєктує власну плату-носій під готовий обчислювальний модуль (SoM), залізо на платі — шини, мікросхеми годинника реального часу (RTC), термодатчики, контролери CAN-шини та світлодіоди індикації — залишається невидимим для ядра Linux, доки його не описано у структурі Дерева Пристроїв (Device Tree). Замість модифікації C-коду ядра та повторної збірки монолітного образу системи створюється окремий файл вихідного опису (`.dts`), що підключає базовий опис модуля (`.dtsi`), вмикає потрібні контролери інтерфейсів, призначає режими виводів (pinmux) та оголошує топологію підключених мікросхем.

Нижче наведено робочий процес побудови повного дерева пристроїв для промислової плати-носія на базі модуля Raspberry Pi Compute Module 4 (CM4), створення динамічного оверлею (`.dtso`), компіляції за допомогою `dtc`, перевірки зареєстрованих пристроїв через `/proc/device-tree` та прикладу взаємодії з апаратними вузлами з простору користувача.

## 1. Архітектурне завдання та склад плати-носія

Плата-носій приймає модуль CM4 через два 100-контактні роз'єми Hirose DF40 і розводить такі периферійні вузли:

1. **Шина I2C1 (контакти GPIO2 / GPIO3):**
   - Мікросхема годинника реального часу NXP PCF85063A (адреса `0x51`) із лінією переривання на GPIO24.
   - Цифровий датчик температури TI TMP102 (адреса `0x48`).
   - Енергонезалежна пам'ять EEPROM Microchip 24LC64 (адреса `0x50`, розмір 8 КБ, сторінка запису 32 байти).

2. **Шина SPI0 (контакти GPIO9–GPIO11, вибір чіпа GPIO8):**
   - Контролер CAN-FD Microchip MCP2518FD із зовнішнім кварцовим генератором на 40 МГц та лінією переривання на GPIO25.

3. **Дискретні лінії GPIO:**
   - Системний світлодіод стану (Heartbeat) на GPIO16 (активний високий рівень).
   - Аварійний світлодіод помилки на GPIO26 (активний високий рівень).
   - Користувацька кнопка керування на GPIO17 (активний низький рівень, внутрішня підтяжка до живлення).
   - Керування комутатором живлення периферії 3.3 В через польовий транзистор на GPIO22.

## 2. Базовий файл дерева пристроїв плати-носія (`carrier-board.dts`)

Файл підключає заголовочні файли ядра з константами переривань та режимів виводів, базовий опис процесора BCM2711 (`bcm2711.dtsi`), опис модуля (`bcm2711-rpi-cm4.dtsi`) і накладає конфігурацію плати-носія.

```dts
/dts-v1/;
#include "bcm2711.dtsi"
#include "bcm2711-rpi-cm4.dtsi"
#include <dt-bindings/interrupt-controller/irq.h>
#include <dt-bindings/gpio/gpio.h>
#include <dt-bindings/pinctrl/bcm2835.h>

/ {
    model = "Custom Industrial Carrier Board for Raspberry Pi CM4";
    compatible = "custom,carrier-cm4", "raspberrypi,4-compute-module", "brcm,bcm2711";

    /* Фіксований генератор 40 МГц для зовнішнього CAN-контролера */
    can_osc_40m: can-oscillator-40m {
        compatible = "fixed-clock";
        #clock-cells = <0>;
        clock-frequency = <40000000>;
        clock-output-names = "can_osc";
    };

    /* Керований стабілізатор живлення периферійних датчиків 3.3 В */
    reg_sensor_3v3: regulator-sensor-3v3 {
        compatible = "regulator-fixed";
        regulator-name = "sensor_3v3";
        regulator-min-microvolt = <3300000>;
        regulator-max-microvolt = <3300000>;
        gpio = <&gpio 22 GPIO_ACTIVE_HIGH>;
        enable-active-high;
        regulator-always-on;
    };

    /* Індикаторні світлодіоди через ядерну підсистему leds-gpio */
    leds {
        compatible = "gpio-leds";

        led_heartbeat: led-0 {
            label = "carrier:green:heartbeat";
            gpios = <&gpio 16 GPIO_ACTIVE_HIGH>;
            linux,default-trigger = "heartbeat";
            default-state = "on";
        };

        led_fault: led-1 {
            label = "carrier:red:fault";
            gpios = <&gpio 26 GPIO_ACTIVE_HIGH>;
            linux,default-trigger = "none";
            default-state = "off";
        };
    };

    /* Користувацькі кнопки через підсистему gpio-keys */
    gpio_keys {
        compatible = "gpio-keys";
        autorepeat;

        btn_user: button-user {
            label = "User Button";
            linux,code = <256>; /* BTN_0 */
            gpios = <&gpio 17 GPIO_ACTIVE_LOW>;
            debounce-interval = <20>; /* 20 мс апаратне заглушення брязкоту */
            wakeup-source;
        };
    };
};

/* Конфігурація мультиплексування виводів (Pinctrl) */
&gpio {
    pinctrl_i2c1_custom: i2c1-pins {
        brcm,pins = <2 3>;
        brcm,function = <BCM2835_FSEL_ALT0>; /* ALT0 = SDA1, SCL1 */
        brcm,pull = <BCM2835_PUD_UP>;        /* Внутрішня підтяжка */
    };

    pinctrl_spi0_custom: spi0-pins {
        brcm,pins = <9 10 11>;
        brcm,function = <BCM2835_FSEL_ALT0>; /* ALT0 = MISO0, MOSI0, SCLK0 */
        brcm,pull = <BCM2835_PUD_OFF>;
    };

    pinctrl_spi0_cs: spi0-cs-pins {
        brcm,pins = <8>;
        brcm,function = <BCM2835_FSEL_OUTP>; /* Керування Chip Select через GPIO */
        brcm,pull = <BCM2835_PUD_OFF>;
    };

    pinctrl_mcp2518_irq: mcp2518-irq-pins {
        brcm,pins = <25>;
        brcm,function = <BCM2835_FSEL_INPT>;
        brcm,pull = <BCM2835_PUD_UP>;
    };

    pinctrl_rtc_irq: rtc-irq-pins {
        brcm,pins = <24>;
        brcm,function = <BCM2835_FSEL_INPT>;
        brcm,pull = <BCM2835_PUD_UP>;
    };
};

/* Ввімкнення та конфігурація шини I2C1 */
&i2c1 {
    status = "okay";
    clock-frequency = <400000>; /* Fast-mode 400 кГц */
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_i2c1_custom>;

    /* Годинник реального часу */
    rtc_pcf: rtc@51 {
        compatible = "nxp,pcf85063a";
        reg = <0x51>;
        pinctrl-names = "default";
        pinctrl-0 = <&pinctrl_rtc_irq>;
        interrupt-parent = <&gpio>;
        interrupts = <24 IRQ_TYPE_EDGE_FALLING>;
        status = "okay";
    };

    /* Датчик температури */
    temp_sensor: sensor@48 {
        compatible = "ti,tmp102";
        reg = <0x48>;
        status = "okay";
    };

    /* Енергонезалежна пам'ять конфігурації плати */
    eeprom_board: eeprom@50 {
        compatible = "atmel,24c64";
        reg = <0x50>;
        pagesize = <32>;
        read-only; /* Захист калібрувальних даних плати */
        status = "okay";
    };
};

/* Ввімкнення та конфігурація шини SPI0 */
&spi0 {
    status = "okay";
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_spi0_custom &pinctrl_spi0_cs>;
    cs-gpios = <&gpio 8 GPIO_ACTIVE_LOW>;

    can_mcp2518: can@0 {
        compatible = "microchip,mcp2518fd";
        reg = <0>; /* CS0 */
        spi-max-frequency = <20000000>; /* 20 МГц тактування SPI */
        interrupt-parent = <&gpio>;
        interrupts = <25 IRQ_TYPE_LEVEL_LOW>;
        clocks = <&can_osc_40m>;
        pinctrl-names = "default";
        pinctrl-0 = <&pinctrl_mcp2518_irq>;
        status = "okay";
    };
};
```

## 3. Динамічний оверлей для модуля розширення (`sensor-hat.dtso`)

Якщо на плату-носій встановлюється додатковий мезонінний модуль (наприклад, плата кліматичного моніторингу з сенсором Bosch BME280 та аналого-цифровим перетворювачем ADS1115 на I2C1), його не обов'язково зашивати у загальне дерево пристроїв. Для цього формується динамічний оверлей:

```dts
/dts-v1/;
/plugin/;

/ {
    compatible = "brcm,bcm2711";

    fragment@0 {
        target = <&i2c1>;
        __overlay__ {
            #address-cells = <1>;
            #size-cells = <0>;

            bme280: weather-sensor@76 {
                compatible = "bosch,bme280";
                reg = <0x76>;
                status = "okay";
            };

            ads1115: adc@49 {
                compatible = "ti,ads1115";
                reg = <0x49>;
                #io-channel-cells = <1>;
                status = "okay";
            };
        };
    };
};
```

## 4. Компіляція та розгортання бінарних блобів

Збірка вихідних текстів Device Tree виконується компілятором `dtc` у два етапи: препроцесування директив C-препроцесора (`#include`, `#define`) та бінарне пакування.

Оскільки файли `.dts` використовують макроси з системних заголовків ядра (`dt-bindings`), перед викликом `dtc` вихідний файл зазвичай пропускають через `cpp`:

```bash
# Препроцесування вихідного файлу DTS із заголовками ядра
cpp -nostdinc -I /usr/src/linux-headers-$(uname -r)/include -undef -x assembler-with-cpp carrier-board.dts carrier-board.preprocessed.dts

# Компіляція базового дерева пристроїв плати-носія з генерацією символів (-@)
dtc -@ -I dts -O dtb -o carrier-board.dtb carrier-board.preprocessed.dts

# Компіляція динамічного оверлею
dtc -@ -I dts -O dtb -o sensor-hat.dtbo sensor-hat.dtso
```

Прапорець `-@` є обов'язковим для базового дерева, якщо планується подальше використання оверлеїв. Він наказує компілятору згенерувати спеціальний вузол `__symbols__`, у якому зберігаються відповідності між текстовими мітками (наприклад, `&i2c1`) та їхніми числовими ідентифікаторами `phandle`. Без таблиці `__symbols__` завантажувач або ядро не зможуть визначити цільовий вузол `target` під час динамічного злиття оверлею.

У системах Raspberry Pi скомпільований блоб `carrier-board.dtb` розміщується у завантажувальному розділі `/boot/firmware/`, а в файлі `config.txt` задається ім'я пристрою та активація оверлею:

```ini
# /boot/firmware/config.txt
device_tree=carrier-board.dtb
dtoverlay=sensor-hat
```

Для систем під керуванням U-Boot завантаження та злиття оверлеїв виконується у командному рядку завантажувача перед передачею керування ядру:

```text
# Завантаження образу ядра, базового DTB та оверлею в оперативну пам'ять
load mmc 0:1 0x80000000 Image
load mmc 0:1 0x83000000 carrier-board.dtb
load mmc 0:1 0x83100000 sensor-hat.dtbo

# Застосування оверлею до базового DTB засобами U-Boot
fdt addr 0x83000000
fdt resize 8192
fdt apply 0x83100000

# Запуск ядра Linux
booti 0x80000000 - 0x83000000
```

## 5. Інспектування та верифікація заліза в Linux

Після завантаження ядра перевірка стану всіх вузлів виконується у просторі користувача безпосередньо через файлові інтерфейси віртуальних файлових систем.

### 1. Перевірка розгорнутого дерева через `/proc/device-tree`
Каталог `/proc/device-tree` є символьним посиланням на `/sys/firmware/devicetree/base`. Кожен каталог у ньому відповідає вузлу, а кожен файл — властивості:

```bash
# Перевірка моделі зареєстрованої плати
cat /proc/device-tree/model
# Custom Industrial Carrier Board for Raspberry Pi CM4

# Перевірка сумісності термодатчика
cat /proc/device-tree/soc/i2c@7e804000/sensor@48/compatible
# ti,tmp102

# Зворотне декомпілювання активного дерева ядра у вихідний текст
dtc -I fs -O dts /proc/device-tree > current-running-tree.dts
```

### 2. Діагностика прив'язки драйверів до пристроїв
Журнал ядра (`dmesg`) дозволяє простежити успішність виклику функції `probe()` кожного зареєстрованого драйвера:

```bash
dmesg | grep -E "pcf85063|tmp102|mcp251dxfd|at24"
```

Типовий успішний вивід у консоль:
```text
[    1.421034] rtc-pcf85063 1-0051: rtc core: registered rtc-pcf85063 as rtc0
[    1.435112] tmp102 1-0048: initialized
[    1.458920] at24 1-0050: 8192 byte 24c64 EEPROM, read-only
[    1.892014] mcp251dxfd spi0.0 can0: MCP2518FD successfully initialized
```

### 3. Перевірка призначення виводів (Pinctrl DebugFS)
Якщо датчик або шина не відповідають, першим кроком перевіряють, чи правильно мультиплексор процесора скерував виводи:

```bash
# Перевірка поточного призначення функцій пінам
cat /sys/kernel/debug/pinctrl/fe200000.gpio/pinmux-pins | grep -E "gpio2|gpio3|gpio8|gpio9"
```

Вивід підтверджує налаштування альтернативних функцій ALT0:
```text
pin 2 (gpio2): function alt0 group gpio2
pin 3 (gpio3): function alt0 group gpio3
pin 8 (gpio8): function output group gpio8
pin 9 (gpio9): function alt0 group gpio9
```

## 6. Програмна взаємодія з пристроями плати-носія

Після того як Device Tree коректно налаштував залізо, прикладний софт звертається до нього через стандартні підсистеми ядра: `hwmon` для температури, `rtc` для часу, `SocketCAN` для промислової шини та `libgpiod` для аварійного світлодіода.

Сучасні версії Linux використовують інтерфейс символьних пристроїв `libgpiod` (`/dev/gpiochip*`), що прийшов на заміну застарілому `sysfs GPIO` (`/sys/class/gpio`). Старий механізм `sysfs` вимагав експорту номерів ліній у текстові файли, не підтримував безпечного володіння лінією процесом і страждав від гонок станів (race conditions). Новий інтерфейс `libgpiod` резервує лінію через дескриптор файлу, автоматично звільняє вивід у разі падіння процесу та підтримує швидкісне опитування подій переривань через системний виклик `poll()`.

Нижче наведено програму опитування сенсорів та сигналізації, реалізовану мовами C та ідіоматичною C++.

:::tabs
```c
/* main.c — Читання датчика TMP102 (hwmon) та керування LED утилітою C */
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <gpiod.h>

#define TEMP_HWMON_PATH "/sys/class/hwmon/hwmon0/temp1_input"
#define GPIO_CHIP "/dev/gpiochip0"
#define FAULT_LED_LINE 26

int read_temperature_milli_celsius(long *temp_mc) {
    int fd = open(TEMP_HWMON_PATH, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити sysfs вузол температури");
        return -1;
    }

    char buf[32];
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (bytes <= 0) {
        return -1;
    }

    buf[bytes] = '\0';
    *temp_mc = strtol(buf, NULL, 10);
    return 0;
}

int main(void) {
    long temp_mc = 0;
    if (read_temperature_milli_celsius(&temp_mc) != 0) {
        fprintf(stderr, "Помилка зчитування даних із TMP102\n");
        return EXIT_FAILURE;
    }

    double temp_c = temp_mc / 1000.0;
    printf("Поточна температура плати: %.2f °C\n", temp_c);

    /* Якщо температура перевищує поріг 60 °C, запалюємо аварійний світлодіод */
    struct gpiod_chip *chip = gpiod_chip_open(GPIO_CHIP);
    if (!chip) {
        perror("Помилка відкриття gpiochip");
        return EXIT_FAILURE;
    }

    struct gpiod_line *led_line = gpiod_chip_get_line(chip, FAULT_LED_LINE);
    if (!led_line) {
        perror("Помилка отримання лінії GPIO");
        gpiod_chip_close(chip);
        return EXIT_FAILURE;
    }

    if (gpiod_line_request_output(led_line, "carrier-monitor", 0) < 0) {
        perror("Не вдалося налаштувати лінію LED на вихід");
        gpiod_chip_close(chip);
        return EXIT_FAILURE;
    }

    if (temp_c > 60.0) {
        printf("УВАГА: Перегрів! Активація аварійного світлодіода (GPIO%d)\n", FAULT_LED_LINE);
        gpiod_line_set_value(led_line, 1);
    } else {
        printf("Температурний режим у нормі.\n");
        gpiod_line_set_value(led_line, 0);
    }

    gpiod_line_release(led_line);
    gpiod_chip_close(chip);
    return EXIT_SUCCESS;
}
```
```cpp
// main.cpp — Ідіоматична взаємодія через RAII, std::filesystem та libgpiod C++
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <chrono>
#include <gpiod.hpp>

namespace {
    constexpr std::string_view hwmon_path = "/sys/class/hwmon/hwmon0/temp1_input";
    constexpr std::string_view gpio_chip_name = "gpiochip0";
    constexpr unsigned int fault_led_offset = 26;
    constexpr double temp_threshold_celsius = 60.0;
}

class CarrierMonitor {
public:
    explicit CarrierMonitor(std::string_view chip_name)
        : chip_(std::string(chip_name)) {}

    [[nodiscard]] double read_temperature() const {
        if (!std::filesystem::exists(hwmon_path)) {
            throw std::runtime_error("Файл інтерфейсу hwmon не знайдено: " + std::string(hwmon_path));
        }

        std::ifstream file(std::string(hwmon_path));
        if (!file.is_open()) {
            throw std::runtime_error("Не вдалося відкрити sysfs файл температури");
        }

        long milli_celsius = 0;
        if (!(file >> milli_celsius)) {
            throw std::runtime_error("Помилка парсингу значення температури");
        }

        return static_cast<double>(milli_celsius) / 1000.0;
    }

    void set_fault_indicator(bool state) {
        auto line = chip_.get_line(fault_led_offset);
        line.request({
            "carrier-monitor-cpp",
            gpiod::line_request::DIRECTION_OUTPUT,
            0
        }, state ? 1 : 0);
        line.set_value(state ? 1 : 0);
        line.release();
    }

private:
    gpiod::chip chip_;
};

int main() {
    try {
        CarrierMonitor monitor(gpio_chip_name);
        const double current_temp = monitor.read_temperature();
        std::cout << "Поточна температура плати: " << current_temp << " °C\n";

        if (current_temp > temp_threshold_celsius) {
            std::cout << "УВАГА: Перегрів! Активація аварійного світлодіода (GPIO" << fault_led_offset << ")\n";
            monitor.set_fault_indicator(true);
        } else {
            std::cout << "Температурний режим у нормі.\n";
            monitor.set_fault_indicator(false);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка моніторингу: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## 7. Типові пастки та діагностика помилок

1. **Відсутність підтягуючих резисторів (Pull-up) на шині I2C:**
   Лінії I2C вимагають фізичних зовнішніх резисторів 2.2–4.7 кОм на платі-носії до шини 3.3 В. Якщо покладатися лише на внутрішні підтяжки SoC (`BCM2835_PUD_UP`), фронти сигналів на частоті 400 кГц завалюватимуться ємністю трас і кабелів (з'являються помилки `i2c-bcm2835: I2C transfer timed out`).
2. **Конфлікт альтернативних функцій виводів:**
   Якщо два вузли в різних фрагментах DTS одночасно претендують на один і той самий пін (наприклад, GPIO16 як лінія SPI та світлодіод у `gpio-leds`), ядро відхилить реєстрацію пізнішого пристрою з помилкою `-EBUSY`. Перевіряйте зайнятість пінів через `cat /sys/kernel/debug/pinctrl/*/pinmux-pins`.
3. **Невідповідність полярності переривання:**
   Для ліній `interrupts` вказуйте точний тригер згідно з даташитом підключеної мікросхеми. Для мікросхем із виходом Open-Drain (наприклад, RTC PCF85063A) використовується `IRQ_TYPE_EDGE_FALLING` або `IRQ_TYPE_LEVEL_LOW`. Неправильний тип тригера призведе до шторму переривань (IRQ storm) або повної відсутності реакції на події.
4. **Неправильний розрахунок частоти SPI для периферійних чіпів:**
   Властивість `spi-max-frequency = <20000000>;` встановлює верхню межу тактування шини. Якщо траси на платі-носії довгі або не узгоджені за хвильовим імпедансом, на частоті 20 МГц виникатимуть паразитні дзвінкі викиди (ringing), що призведе до помилок CRC в CAN-контролері. На етапі першого запуску знижуйте частоту до 1–5 МГц для підтвердження стабільності обміну даними.
5. **Затримки старту живлення сенсорів (Reset Timings):**
   Якщо периферійні мікросхеми живляться від керованого стабілізатора `reg_sensor_3v3`, деякі мікросхеми вимагають 5–15 мс після подачі напруги для завершення внутрішнього Power-On Reset (POR). Якщо драйвер ядра викличе `.probe()` раніше, мікросхема не відповість на шині I2C. Для запобігання цьому у вузлі регулятора вказують властивість `startup-delay-us = <20000>;`.
