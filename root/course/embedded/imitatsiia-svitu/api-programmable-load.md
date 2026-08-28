# 📋 Програмний інтерфейс керованого джерела живлення та електронного навантаження

Керування живильними приладами на стенді апаратного тестування вимагає суворого програмного контракту. Будь-яка помилка в послідовності ініціалізації, пропущений таймаут або некоректно виставлена межа апаратного захисту за струмом може за мікросекунди випалити захисні діоди чи стабілізатори випробуваної плати (DUT).

Нижче наведено систему команд міжнародного стандарту SCPI (Standard Commands for Programmable Instruments) для автоматизованого джерела живлення з функцією емуляції внутрішнього опору акумулятора та швидкодіючого динамічного електронного навантаження постійного струму, а також закінчену бібліотеку-драйвер мовами C та C++.

---

## 1. Архітектура зв'язку та фізичні інтерфейси керування

Стендові вимірювальні прилади підтримують кілька фізичних рівнів сполучення з хост-комп'ютером:
1. **Ethernet (LXI / VXI-11 / Raw TCP Socket порт 5025):** базовий протокол для сучасних автоматизованих стендів. Забезпечує гальванічну розв'язку між комп'ютером і вимірювальним трактом, передачу команд по локальній мережі та низьку затримку (латентність надсилання команди від 200 мкс до 1 мс).
2. **USBTMC (USB Test & Measurement Class):** швидкісний клас USB-пристроїв, який емулює інтерфейс IEEE-488 (GPIB) поверх шини USB 2.0. Використовується для настільних установок.
3. **Послідовний інтерфейс RS-232 / RS-485:** застосовується у промислових стійках. Вимагає обов'язкового налаштування апаратного керування потоком (RTS/CTS), щоб уникнути переповнення буфера команд мікроконтролера приладу.

Кожна команда SCPI являє собою текстовий ASCII-рядок ієрархічної структури, де вузли дерева відокремлюються двокрапкою, параметри — пробілом, а кінець повідомлення позначається символом переводу рядка `\n` (LF) або парою `\r\n` (CRLF).

---

## 2. Довідкова таблиця команд SCPI

Усі команди поділяються на дві категорії: загальні команди стандарту IEEE 488.2 (починаються із зірочки `*`) та функціональні підсистеми конфігурації вихідних каналів.

### Команди джерела живлення (Battery Simulator / Power Supply)

| Команда SCPI | Призначення | Приклад використання | Очікувана відповідь |
|---|---|---|---|
| `*IDN?` | Запит ідентифікатора приладу (виробник, модель, серійний номер, версія прошивки) | `*IDN?\n` | `RIGOL TECHNOLOGIES,DP832A,DP8B0001,00.01.16` |
| `*RST` | Повне скидання приладу в заводський безпечний стан (вимикає всі виходи) | `*RST\n` | Немає |
| `:SOURce:VOLTage <V>` | Встановлення вихідної напруги холостого ходу (ЕРС) у вольтах | `:SOUR:VOLT 14.8\n` | Немає (або перевірка `*OPC?`) |
| `:SOURce:CURRent <A>` | Встановлення обмеження струму (струм відсікання) в амперах | `:SOUR:CURR 5.0\n` | Немає |
| `:SOURce:RESistance <Ohm>`| Програмне встановлення внутрішнього опору батареї `R_int` (0.001..2.000 Ом) | `:SOUR:RES 0.045\n` | Вмикає падіння напруги `V_out = E - I * R` |
| `:OUTPut:STATe <ON\|OFF>`| Увімкнення або вимкнення силових вихідних клем | `:OUTP:STAT ON\n` | Подає напругу на DUT |
| `:MEASure:VOLTage?` | Точний апаратний вимір поточної вихідної напруги на клемах | `:MEAS:VOLT?\n` | `14.623` |
| `:MEASure:CURRent?` | Точний апаратний вимір миттєвого споживаного струму | `:MEAS:CURR?\n` | `1.458` |
| `:PROTection:VOLTage <V>`| Апаратний захист від перенапруги (Over-Voltage Protection, OVP) | `:PROT:VOLT 16.8\n` | Миттєве вимкнення реле при перевищенні |
| `:PROTection:CURRent <A>`| Апаратний захист від перевантаження за струмом (OCP) | `:PROT:CURR 8.0\n` | Відсікання при короткому замиканні |

### Команди електронного навантаження (DC Electronic Load)

| Команда SCPI | Режим | Призначення та поведінка | Приклад |
|---|---|---|---|
| `:MODE <CC\|CV\|CR\|CP>` | Режим роботи | `CC` — постійний струм (імітація мотора); `CV` — постійна напруга; `CR` — опір; `CP` — потужність. | `:MODE CC\n` |
| `:CURRent:STATic <A>` | CC Mode | Базове споживання струму в статичному режимі | `:CURR:STAT 2.5\n` |
| `:TRANsient:MODE <PULSE>`| Динамічний | Увімкнення імпульсного режиму навантаження | `:TRAN:MODE PULSE\n` |
| `:TRANsient:ALEVel <A>` | Динамічний | Початковий рівень струму (рівень A) | `:TRAN:ALEV 1.0\n` |
| `:TRANsient:BLEVel <A>` | Динамічний | Піковий рівень струму (рівень B під час стрибка тяги) | `:TRAN:BLEV 25.0\n` |
| `:TRANsient:AWIDth <s>` | Динамічний | Тривалість утримання струму рівня A в секундах | `:TRAN:AWID 0.05\n` |
| `:TRANsient:BWIDth <s>` | Динамічний | Тривалість утримання струму рівня B (наприклад, 10 мс) | `:TRAN:BWID 0.01\n` |
| `:TRANsient:SLEW <A/us>` | Динамічний | Швидкість наростання фронту струму в А/мкс | `:TRAN:SLEW 5.0\n` |
| `:INPut:STATe <ON\|OFF>` | Клеми | Підключення навантаження до виходу DC-DC або батареї | `:INP:STAT ON\n` |

---

## 3. Чотирипровідне підключення Кельвіна (Remote Sense)

Під час динамічних випробувань зі струмами 10–30 А опір підвідних кабелів стає головним джерелом вимірювальних похибок. Мідний дріт перерізом 1.5 мм² довжиною 1 м має опір близько 0.024 Ом. Для двох дротів (прямого та зворотного) загальний опір складає майже 0.05 Ом. При протіканні струму 20 А падіння напруги на кабелях досягає:

```
V_кабель = I · R_дріт = 20 А · 0.05 Ом = 1.0 В
```

Якщо джерело живлення контролює напругу лише на власних вихідних клемах, плата DUT отримає замість 14.8 В лише 13.8 В. Для компенсації цієї втрати використовують схему віддаленого контролю (Remote Sense):
- Силові виходи (Force+, Force-) живлять пристрій основним струмом.
- Окремі тонкі вимірювальні виводи (Sense+, Sense-) підключаються безпосередньо до вхідного роз'єму плати DUT. Оскільки по вимірювальних лініях тече незначний струм (менше 1 мкА), падіння напруги на них дорівнює нулю, і внутрішній стабілізатор джерела автоматично піднімає напругу на клемах Force, компенсуючи спад на проводах.

```
 Джерело живлення                      Кабельна траса                      Плата DUT
┌────────────────┐                    Силовий Force +                    ┌────────────┐
│ Force +  ──────┼───────────────────────────────────────────────────────┼──> V_IN    │
│ Sense +  ──────┼─────────────────── Вимірювальний Sense + ─────────────┼──> V_SENSE │
│ Sense −  ──────┼─────────────────── Вимірювальний Sense − ─────────────┼──> GND_SENS│
│ Force −  ──────┼───────────────────────────────────────────────────────┼──> GND     │
└────────────────┘                    Силовий Force −                    └────────────┘
```

---

## 4. Програмна реалізація драйвера автоматизації

Драйвер реалізує безпечний протокол ініціалізації: спочатку виставляються апаратні ліміти `:PROT:VOLT` та `:PROT:CURR`, потім параметри джерела, і лише останньою дією активуються силові ключі. У C++ версії використовується ідіома RAII (Resource Acquisition Is Initialization) — деструктор гарантовано знеструмлює клеми при будь-якому аварійному виході чи генерації винятку.

:::tabs
```c
/* power_rig_driver.c - Драйвер керування живленням та навантаженням на C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int socket_fd;
    char ip_address[32];
    double max_voltage_limit;
    double max_current_limit;
    bool is_output_enabled;
} power_supply_t;

typedef struct {
    int socket_fd;
    char ip_address[32];
    bool is_input_enabled;
} electronic_load_t;

/* Допоміжна функція надсилання SCPI команди */
static bool scpi_send(int sock_fd, const char *cmd) {
    /* У реальному стенді: return send(sock_fd, cmd, strlen(cmd), 0) > 0; */
    printf("[SCPI OUT] %s", cmd);
    return true;
}

/* Ініціалізація симулятора батареї */
bool power_supply_init(power_supply_t *ps, const char *ip, double ovp, double ocp) {
    if (!ps || !ip) return false;
    strncpy(ps->ip_address, ip, sizeof(ps->ip_address) - 1);
    ps->max_voltage_limit = ovp;
    ps->max_current_limit = ocp;
    ps->is_output_enabled = false;

    char cmd[64];
    /* Вимкнення виходу перед конфігурацією для безпеки */
    scpi_send(ps->socket_fd, ":OUTP:STAT OFF\n");

    /* Встановлення апаратних порогів захисту */
    snprintf(cmd, sizeof(cmd), ":PROT:VOLT %.2f\n", ovp);
    scpi_send(ps->socket_fd, cmd);
    snprintf(cmd, sizeof(cmd), ":PROT:CURR %.2f\n", ocp);
    scpi_send(ps->socket_fd, cmd);

    return true;
}

/* Налаштування параметрів батареї: ЕРС та внутрішнього опору R_int */
bool power_supply_set_battery_profile(power_supply_t *ps, double vocv, double r_int) {
    if (!ps || vocv > ps->max_voltage_limit) return false;

    char cmd[64];
    snprintf(cmd, sizeof(cmd), ":SOUR:VOLT %.3f\n", vocv);
    scpi_send(ps->socket_fd, cmd);

    snprintf(cmd, sizeof(cmd), ":SOUR:RES %.4f\n", r_int);
    scpi_send(ps->socket_fd, cmd);

    return true;
}

/* Запуск імпульсного навантаження для тестування просідання напруги */
bool electronic_load_trigger_pulse(electronic_load_t *load, double base_a, double peak_a, double pulse_sec) {
    if (!load) return false;

    char cmd[64];
    scpi_send(load->socket_fd, ":MODE CC\n");
    
    snprintf(cmd, sizeof(cmd), ":TRAN:MODE PULSE\n");
    scpi_send(load->socket_fd, cmd);

    snprintf(cmd, sizeof(cmd), ":TRAN:ALEV %.2f\n", base_a);
    scpi_send(load->socket_fd, cmd);

    snprintf(cmd, sizeof(cmd), ":TRAN:BLEV %.2f\n", peak_a);
    scpi_send(load->socket_fd, cmd);

    snprintf(cmd, sizeof(cmd), ":TRAN:BWID %.4f\n", pulse_sec);
    scpi_send(load->socket_fd, cmd);

    scpi_send(load->socket_fd, ":INP:STAT ON\n");
    return true;
}
```
```cpp
/* power_rig_driver.hpp / .cpp - RAII обгортка та інтерфейс керування на C++20 */
#include <iostream>
#include <string>
#include <format>
#include <expected>
#include <chrono>
#include <thread>

class PowerSupplyDriver {
public:
    enum class Error {
        ConnectionFailed,
        SafetyLimitExceeded,
        CommandRejected
    };

    PowerSupplyDriver(std::string ip_address, double ovp_volts, double ocp_amps)
        : ip_{std::move(ip_address)}, ovp_{ovp_volts}, ocp_{ocp_amps} {
        // У конструкторі вимикаємо вихід для гарантії безпеки (Fail-Safe)
        send_raw(":OUTP:STAT OFF\n");
        send_raw(std::format(":PROT:VOLT {:.2f}\n", ovp_));
        send_raw(std::format(":PROT:CURR {:.2f}\n", ocp_));
    }

    ~PowerSupplyDriver() {
        // Деструктор гарантовано знеструмлює клеми при виході з зони видимості
        send_raw(":OUTP:STAT OFF\n");
    }

    // Заборона копіювання для запобігання дублюванню сесії приладу
    PowerSupplyDriver(const PowerSupplyDriver&) = delete;
    PowerSupplyDriver& operator=(const PowerSupplyDriver&) = delete;
    PowerSupplyDriver(PowerSupplyDriver&&) noexcept = default;
    PowerSupplyDriver& operator=(PowerSupplyDriver&&) noexcept = default;

    [[nodiscard]] std::expected<void, Error> set_battery_model(double ocv_volts, double r_internal_ohms) noexcept {
        if (ocv_volts > ovp_ || ocv_volts < 0.0) {
            return std::unexpected(Error::SafetyLimitExceeded);
        }
        send_raw(std::format(":SOUR:VOLT {:.3f}\n", ocv_volts));
        send_raw(std::format(":SOUR:RES {:.4f}\n", r_internal_ohms));
        return {};
    }

    [[nodiscard]] std::expected<void, Error> enable_output(bool enable) noexcept {
        send_raw(enable ? ":OUTP:STAT ON\n" : ":OUTP:STAT OFF\n");
        output_enabled_ = enable;
        return {};
    }

private:
    void send_raw(const std::string& scpi_cmd) noexcept {
        std::cout << "[SCPI C++ RIG] " << scpi_cmd;
    }

    std::string ip_;
    double ovp_{0.0};
    double ocp_{0.0};
    bool output_enabled_{false};
};

class ElectronicLoadDriver {
public:
    explicit ElectronicLoadDriver(std::string ip_address) : ip_{std::move(ip_address)} {
        send_raw(":INP:STAT OFF\n");
    }

    ~ElectronicLoadDriver() {
        send_raw(":INP:STAT OFF\n");
    }

    void execute_step_response_test(double base_current_a, double step_current_a, 
                                   std::chrono::milliseconds pulse_duration) noexcept {
        send_raw(":MODE CC\n");
        send_raw(":TRAN:MODE PULSE\n");
        send_raw(std::format(":TRAN:ALEV {:.2f}\n", base_current_a));
        send_raw(std::format(":TRAN:BLEV {:.2f}\n", step_current_a));
        send_raw(std::format(":TRAN:BWID {:.4f}\n", pulse_duration.count() / 1000.0));
        send_raw(":TRAN:SLEW 5.0\n"); // 5 А/мкс швидкість наростання
        send_raw(":INP:STAT ON\n");
    }

private:
    void send_raw(const std::string& scpi_cmd) noexcept {
        std::cout << "[SCPI C++ LOAD] " << scpi_cmd;
    }

    std::string ip_;
};
```
:::

---

## 5. Стійкість петлі стабілізації та захист від індуктивного викиду

Під час випробувань перехідних процесів (стрибки струму зі швидкістю наростання `5 А/мкс`) індуктивність з'єднувальних проводів `L_дріт` викликає різкий індуктивний викид напруги за формулою:

```
V_викид = L_дріт · (di / dt)
```

При типовій індуктивності кабельної коси 1 мкГн і стрибку струму 20 А за 4 мкс амплітуда перенапруги на клемах досягає 5 В понад напругу живлення. Якщо плата не має вхідних супресорів (TVS-діодів) або RC-демпферів (Snubber), цей імпульс пробиває вхідні транзистори перетворювача.

Крім того, підключення електронного навантаження в режимі постійного струму (CC) до імпульсного DC-DC перетворювача плати може викликати генерацію автоколивань:
- Вхідний імпульсний перетворювач у статичному режимі має **негативний диференційний опір** `R_diff = -V_in / I_in` (зі зниженням напруги вхідний струм зростає для підтримки постійної вихідної потужності).
- Якщо вихідний опір джерела живлення перевищує абсолютне значення `|R_diff|` перетворювача на частоті резонансу вхідного LC-фільтра, система втрачає стійкість за критерієм Найквіста. Стенд дозволяє виявити цю приховану нестабільність до підключення реальних моторів.

---

## 6. Реєстри стану та черга системних помилок (Status Byte & Error Queue)

Надійне промислове керування вимагає постійного моніторингу апаратного стану приладів. За стандартом SCPI прилад підтримує ієрархію статусних регістрів:

1. **Реєстр байта стану (Status Byte, `*STB?`):** повертає 8-бітну маску, де біт 3 (QUE) вказує на наявність повідомлень у черзі помилок, біт 5 (ESB) — на виникнення стандартної помилки (синтаксична помилка, перевищення діапазону), а біт 7 (OPER) — на поточну активність вихідних каскадів.
2. **Черга системних помилок (`:SYSTem:ERRor?`):** повертає код та текстовий опис найстарішої зареєстрованої помилки за принципом FIFO (First-In, First-Out). Якщо черга порожня, прилад повертає рядок `+0,"No error"`.
3. **Очищення стану (`*CLS`):** очищає чергу помилок та скидає статусні регістри перед запуском нового тестового сценарію.

Драйвер зобов'язаний опитувати `:SYST:ERR?` після кожного блоку конфігураційних команд для миттєвої реєстрації відхилень та захисту стендового обладнання.

---

## 7. Перевірочний контрольний список інтеграції в стенд

1. **Порядок увімкнення:** Спочатку задаються апаратні ліміти `:PROT:VOLT` та `:PROT:CURR`, потім напруга `:SOUR:VOLT`, і лише останньою командою вмикається вихід `:OUTP:STAT ON`.
2. **Компенсація опору кабелів (4-Wire Remote Sense):** Під час струмів понад 5 А використання окремих вимірювальних ліній зворотного зв'язку (Sense+, Sense-) безпосередньо біля роз'єму DUT обов'язкове.
3. **Аварійний інтерлок (Emergency Stop):** Силові клеми джерел живлення повинні бути підключені через апаратне реле безпеки, кероване сторожовою лінією стенда: у разі зависання керуючого ПК реле автоматично розриває коло живлення.
