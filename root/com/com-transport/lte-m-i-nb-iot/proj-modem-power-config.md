# ⚙️ Програмне керування енергозбереженням модема на C та C++

При розробці автономного телеметричного вузла на мікроконтролері керування стільниковим модемом вимагає суворого дотримання часових інтервалів передачі AT-команд, коректного двійкового кодування масок таймерів 3GPP, асинхронного розбору відповідей (URC) та апаратного введення модема й процесора в режим наднизького споживання після відправки пакетів даних.

Практична складність взаємодії зі стільниковим LPWAN-модулем полягає в тому, що модем є асинхронним пристроєм: він може повертати проміжні сповіщення про зміну стану радіоканалу, вимагати повторного надсилання команд або затримувати відповідь на час сканування базових станцій. Спроба писати блокуючий лінійний код без контролю таймаутів та перевірки мережевих підтверджень неминуче призводить до зависання пристрою та передчасного вичерпання ресурсу батареї.

Нижче наведено повнофункціональний драйвер керування стільниковим модулем (на прикладі модулів категорій LTE Cat-M1 та NB-IoT виробництва Quectel BG95/BG96 або Nordic Semiconductor nRF9160). Програма реалізує двійкове кодування таймерів 3GPP TS 24.008, надсилання конфігурації PSM та eDRX, перевірку реєстрації в мережі, відправку UDP-дейтаграми з телеметрією датчиків та коректне введення системи в режим глибокого сну.

---

### Апаратне узгодження рівнів та розведення ліній керування

Більшість сучасних промислових LPWAN-модулів (Quectel BG95, SIMCom SIM7080G, u-blox SARA-R4) мають цифровий логічний рівень введення-виведення `1.8 В` (напруга внутрішнього стабілізатора `V_INT` / `VIO`). Якщо хост-мікроконтролер (наприклад, STM32 або ESP32) працює від шини живлення `3.3 В`, пряме з'єднання ліній UART призведе до електричного пробою захисних діодів вхідних каскадів модема.

Для надійної роботи застосовують двонаправлені перетворювачі логічних рівнів (Level Shifters, наприклад TXB0104 або дискретні пари польових транзисторів BSS138).

```
   ┌─────────────────────────────────────────────────────────────┐
   │            СХЕМА АПАРАТНОГО З'ЄДНАННЯ MCU ТА МОДЕМА         │
   └─────────────────────────────────────────────────────────────┘
   
    Хост-MCU (3.3 В)        Перетворювач рівнів       LPWAN-модем (1.8 В)
    ┌──────────────┐         ┌──────────────┐          ┌──────────────┐
    │          TXD ├────────►│ 3.3V ──► 1.8V├─────────►│ RXD          │
    │          RXD │◄────────┤ 3.3V ◄── 1.8V│◄─────────┤ TXD          │
    │          DTR ├────────►│ 3.3V ──► 1.8V├─────────►│ DTR (Сон)    │
    │     RI / WAKE│◄────────┤ 3.3V ◄── 1.8V│◄─────────┤ RI (Пейджинг)│
    │       PWRKEY ├────────►│ Відкритий    ├─────────►│ PWRKEY       │
    │        RESET ├────────►│ колектор     ├─────────►│ RESET_N      │
    └──────────────┘         └──────────────┘          └──────────────┘
```

Функціональне призначення сигнальних ліній керування:
- **DTR (Data Terminal Ready):** керування режимом енергозбереження. Низький рівень (0 В) пробуджує UART-інтерфейс модема; високий рівень (1.8 В) дозволяє модему зупинити внутрішні генератори частоти та заснути в режимі PSM.
- **RI (Ring Indicator):** вихідний пін переривання модема. Коли в період активного вікна eDRX базова станція передає пейджинговий виклик або вхідний UDP-пакет, пін RI формує низький імпульс (тривалістю 120 мс), який пробуджує хост-мікроконтролер із режиму глибокого сну.
- **PWRKEY:** пін увімкнення та вимкнення модуля. Для ввімкнення лінія притягується до землі на 500 мс, після чого переводиться у високоімпедансний стан (Hi-Z).

---

### Архітектура та послідовність операцій

Програмний конвеєр передачі телеметрії базується на скінченному автоматі станів (Finite State Machine, FSM), що мінімізує час активності процесора:

```
 ┌──────────┐    DTR Low     ┌──────────────┐    AT+CEREG?    ┌──────────────┐
 │ PSM Sleep│ ─────────────► │ Ініціалізація│ ──────────────► │ Реєстрація в │
 │  (<5 мкА)│                │  UART та PSM │                 │    мережі    │
 └──────────┘                └──────────────┘                 └──────┬───────┘
      ▲                                                              │ OK
      │                                                              ▼
 ┌────┴─────┐   AT+QICLOSE   ┌──────────────┐   AT+QISEND     ┌──────────────┐
 │ Сон хоста│ ◄───────────── │ Закриття UDP │ ◄────────────── │ Відправка    │
 │ (Standby)│   DTR High     │    сокета    │                 │ телеметрії   │
 └──────────┘                └──────────────┘                 └──────────────┘
```

Повний цикл передачі даних складається з таких обов'язкових кроків:
1. **Апаратне пробудження модема:** переведення лінії DTR у низький логічний рівень (0 В) для увімкнення приймача UART модема або подача імпульсу тривалістю 500 мс на пін `PWRKEY`;
2. **Конфігурація таймерів 3GPP:** кодування бажаного інтервалу періодичного звітування (наприклад, 24 години) та активного часу доступності для вхідних команд (наприклад, 10 секунд) у двійкові 8-бітові маски та надсилання команди `AT+CPSMS`;
3. **Налаштування eDRX:** вибір періоду переривчастого прийому для зниження струму в межах активного вікна за допомогою команди `AT+CEDRXS`;
4. **Очікування реєстрації (Network Attachment):** періодичне опитування статусу через `AT+CEREG?` або очікування асинхронного повідомлення URC з обов'язковою перевіркою погоджених базовою станцією параметрів;
5. **Відправка UDP-пакета:** відкриття сокета через вбудований стек модема (`AT+QIOPEN`), надсилання бінарного масиву телеметрії датчиків (`AT+QISEND`) та очікування квитанції передачі;
6. **Завершення сесії:** закриття сокета, переведення лінії DTR у високий логічний стан (VCC) для дозволу входу в сон та перехід керівного мікроконтролера в режим Deep Sleep до наступного системного таймера або зовнішнього переривання.

---

### Реалізація драйвера на мовах C та C++

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define AT_BUF_SIZE        256
#define UART_TIMEOUT_MS    5000

typedef enum {
    MODEM_OK = 0,
    MODEM_ERROR_TIMEOUT,
    MODEM_ERROR_RESPONSE,
    MODEM_ERROR_REGISTRATION
} modem_status_t;

/* Структура конфігурації таймерів PSM */
typedef struct {
    uint32_t periodic_tau_sec;  /* Бажаний інтервал Periodic TAU в секундах */
    uint32_t active_time_sec;   /* Бажаний інтервал Active Time в секундах */
} psm_config_t;

/* Функції низькорівневого вводу-виводу UART (платформозалежні заглушки) */
extern void platform_uart_send(const char *data, size_t len);
extern size_t platform_uart_receive_line(char *buf, size_t max_len, uint32_t timeout_ms);
extern void platform_delay_ms(uint32_t ms);
extern void platform_gpio_set_dtr(bool high);

/* Кодування інтервалу в 8-бітний рядок GPRS Timer 3 (T3412-ext) за 3GPP TS 24.008 */
static bool encode_t3412(uint32_t seconds, char *out_str) {
    uint8_t unit_bits = 0;
    uint32_t value = 0;

    if (seconds <= 62) {
        unit_bits = 0b011; /* Крок 2 с */
        value = seconds / 2;
    } else if (seconds <= 31 * 60) {
        unit_bits = 0b101; /* Крок 1 хв */
        value = seconds / 60;
    } else if (seconds <= 31 * 600) {
        unit_bits = 0b000; /* Крок 10 хв */
        value = seconds / 600;
    } else if (seconds <= 31 * 3600) {
        unit_bits = 0b001; /* Крок 1 год */
        value = seconds / 3600;
    } else if (seconds <= 31 * 36000) {
        unit_bits = 0b010; /* Крок 10 год */
        value = seconds / 36000;
    } else if (seconds <= 31 * 320 * 3600) {
        unit_bits = 0b110; /* Крок 320 год */
        value = seconds / (320 * 3600);
    } else {
        return false; /* Перевищення ліміту 413 днів */
    }

    if (value > 31) value = 31;
    if (value == 0) value = 1;

    /* Формування 8-бітного рядка "b8b7b6b5b4b3b2b1" */
    for (int i = 2; i >= 0; i--) {
        *out_str++ = ((unit_bits >> i) & 1) ? '1' : '0';
    }
    for (int i = 4; i >= 0; i--) {
        *out_str++ = ((value >> i) & 1) ? '1' : '0';
    }
    *out_str = '\0';
    return true;
}

/* Кодування інтервалу в 8-бітний рядок GPRS Timer 2 (T3324) за 3GPP TS 24.008 */
static bool encode_t3324(uint32_t seconds, char *out_str) {
    uint8_t unit_bits = 0;
    uint32_t value = 0;

    if (seconds == 0) {
        strcpy(out_str, "11100000"); /* Деактивовано: миттєвий перехід у PSM */
        return true;
    } else if (seconds <= 62) {
        unit_bits = 0b000; /* Крок 2 с */
        value = seconds / 2;
    } else if (seconds <= 31 * 60) {
        unit_bits = 0b001; /* Крок 1 хв */
        value = seconds / 60;
    } else if (seconds <= 31 * 360) {
        unit_bits = 0b010; /* Крок 6 хв (декада) */
        value = seconds / 360;
    } else {
        return false; /* Перевищення максимального значення 186 хв */
    }

    if (value > 31) value = 31;
    if (value == 0) value = 1;

    for (int i = 2; i >= 0; i--) {
        *out_str++ = ((unit_bits >> i) & 1) ? '1' : '0';
    }
    for (int i = 4; i >= 0; i--) {
        *out_str++ = ((value >> i) & 1) ? '1' : '0';
    }
    *out_str = '\0';
    return true;
}

/* Надсилання AT-команди та очікування відповіді "OK" */
modem_status_t modem_send_cmd_expect_ok(const char *cmd, uint32_t timeout_ms) {
    char rx_buf[AT_BUF_SIZE];
    platform_uart_send(cmd, strlen(cmd));
    platform_uart_send("\r\n", 2);

    uint32_t elapsed = 0;
    while (elapsed < timeout_ms) {
        size_t len = platform_uart_receive_line(rx_buf, sizeof(rx_buf) - 1, 500);
        if (len > 0) {
            rx_buf[len] = '\0';
            if (strstr(rx_buf, "OK") != NULL) {
                return MODEM_OK;
            }
            if (strstr(rx_buf, "ERROR") != NULL || strstr(rx_buf, "+CME ERROR") != NULL) {
                return MODEM_ERROR_RESPONSE;
            }
        }
        elapsed += 500;
    }
    return MODEM_ERROR_TIMEOUT;
}

/* Конфігурація режимів енергозбереження PSM та eDRX */
modem_status_t modem_configure_power_saving(const psm_config_t *cfg) {
    char t3412_str[9];
    char t3324_str[9];
    char at_cmd[128];

    if (!encode_t3412(cfg->periodic_tau_sec, t3412_str) ||
        !encode_t3324(cfg->active_time_sec, t3324_str)) {
        return MODEM_ERROR_RESPONSE;
    }

    /* Налаштування PSM: AT+CPSMS=1,,,"<T3412>","<T3324>" */
    snprintf(at_cmd, sizeof(at_cmd), "AT+CPSMS=1,,,\"%s\",\"%s\"", t3412_str, t3324_str);
    modem_status_t status = modem_send_cmd_expect_ok(at_cmd, UART_TIMEOUT_MS);
    if (status != MODEM_OK) return status;

    /* Налаштування eDRX: AT+CEDRXS=1,5,"0010" (AcT=5 NB-IoT, цикл 40.96 с) */
    status = modem_send_cmd_expect_ok("AT+CEDRXS=1,5,\"0010\"", UART_TIMEOUT_MS);
    return status;
}

/* Перевірка реєстрації в мережі оператора */
modem_status_t modem_wait_network_registration(uint32_t timeout_sec) {
    char rx_buf[AT_BUF_SIZE];
    uint32_t elapsed = 0;

    while (elapsed < timeout_sec) {
        platform_uart_send("AT+CEREG?\r\n", 12);
        size_t len = platform_uart_receive_line(rx_buf, sizeof(rx_buf) - 1, 1000);
        if (len > 0) {
            rx_buf[len] = '\0';
            /* Статуси 1 (Home) та 5 (Roaming) свідчать про успішну реєстрацію */
            if (strstr(rx_buf, "+CEREG: 4,1") != NULL || strstr(rx_buf, "+CEREG: 4,5") != NULL ||
                strstr(rx_buf, "+CEREG: 1") != NULL || strstr(rx_buf, "+CEREG: 5") != NULL) {
                return MODEM_OK;
            }
        }
        platform_delay_ms(1000);
        elapsed += 1;
    }
    return MODEM_ERROR_REGISTRATION;
}

/* Відправка UDP дейтаграми з телеметрією */
modem_status_t modem_send_udp_telemetry(const char *server_ip, uint16_t port,
                                        const uint8_t *payload, size_t payload_len) {
    char cmd[128];
    /* Відкриття UDP сокета: AT+QIOPEN=1,0,"UDP","<IP>",<PORT>,0,0 */
    snprintf(cmd, sizeof(cmd), "AT+QIOPEN=1,0,\"UDP\",\"%s\",%u,0,0", server_ip, port);
    if (modem_send_cmd_expect_ok(cmd, UART_TIMEOUT_MS) != MODEM_OK) {
        return MODEM_ERROR_RESPONSE;
    }

    /* Підготовка до передачі даних фіксованої довжини */
    snprintf(cmd, sizeof(cmd), "AT+QISEND=0,%zu", payload_len);
    platform_uart_send(cmd, strlen(cmd));
    platform_uart_send("\r\n", 2);
    platform_delay_ms(100);

    /* Надсилання сирого бінарного корисного навантаження */
    platform_uart_send((const char *)payload, payload_len);
    platform_delay_ms(200);

    /* Закриття сокета після підтвердження відправки */
    modem_send_cmd_expect_ok("AT+QICLOSE=0", UART_TIMEOUT_MS);
    return MODEM_OK;
}

/* Повний робочий цикл вимірювання та сну */
void telemetry_node_run_cycle(void) {
    /* 1. Апаратне пробудження модема через лінію DTR */
    platform_gpio_set_dtr(false);
    platform_delay_ms(50);

    /* 2. Ініціалізація модема */
    modem_send_cmd_expect_ok("AT", UART_TIMEOUT_MS);
    modem_send_cmd_expect_ok("AT+CEREG=4", UART_TIMEOUT_MS);

    /* 3. Встановлення конфігурації сну: TAU = 24 год, Active Time = 10 с */
    psm_config_t psm = { .periodic_tau_sec = 86400, .active_time_sec = 10 };
    modem_configure_power_saving(&psm);

    /* 4. Очікування мережі та відправка пакету */
    if (modem_wait_network_registration(60) == MODEM_OK) {
        uint8_t telemetry_data[8] = { 0xAA, 0x01, 0x18, 0x2A, 0x0C, 0x55, 0x00, 0xFF };
        modem_send_udp_telemetry("198.51.100.42", 5683, telemetry_data, sizeof(telemetry_data));
    }

    /* 5. Дозвіл модему перейти в режим сну: піднімаємо DTR у високий стан */
    platform_gpio_set_dtr(true);
}
```
```cpp
#include <string>
#include <string_view>
#include <array>
#include <chrono>
#include <expected>
#include <span>
#include <format>
#include <cstdint>

namespace cellular {

using namespace std::chrono_literals;

enum class ModemError {
    Timeout,
    InvalidResponse,
    RegistrationFailed,
    InvalidParameter
};

struct PsmConfig {
    std::chrono::seconds periodic_tau{86400s}; // 24 години
    std::chrono::seconds active_time{10s};      // 10 секунд
};

class TimerEncoder {
public:
    static std::expected<std::string, ModemError> encode_t3412(std::chrono::seconds sec) noexcept {
        const auto total = sec.count();
        uint8_t unit_bits = 0;
        int64_t val = 0;

        if (total <= 62) {
            unit_bits = 0b011; // 2 с
            val = total / 2;
        } else if (total <= 31 * 60) {
            unit_bits = 0b101; // 1 хв
            val = total / 60;
        } else if (total <= 31 * 600) {
            unit_bits = 0b000; // 10 хв
            val = total / 600;
        } else if (total <= 31 * 3600) {
            unit_bits = 0b001; // 1 год
            val = total / 3600;
        } else if (total <= 31 * 36000) {
            unit_bits = 0b010; // 10 год
            val = total / 36000;
        } else if (total <= 31 * 320 * 3600) {
            unit_bits = 0b110; // 320 год
            val = total / (320 * 3600);
        } else {
            return std::unexpected(ModemError::InvalidParameter);
        }

        val = std::clamp<int64_t>(val, 1, 31);
        return format_bitmask(unit_bits, static_cast<uint8_t>(val));
    }

    static std::expected<std::string, ModemError> encode_t3324(std::chrono::seconds sec) noexcept {
        const auto total = sec.count();
        if (total == 0) {
            return std::string("11100000"); // Миттєвий перехід у PSM
        }
        uint8_t unit_bits = 0;
        int64_t val = 0;

        if (total <= 62) {
            unit_bits = 0b000; // 2 с
            val = total / 2;
        } else if (total <= 31 * 60) {
            unit_bits = 0b001; // 1 хв
            val = total / 60;
        } else if (total <= 31 * 360) {
            unit_bits = 0b010; // 6 хв
            val = total / 360;
        } else {
            return std::unexpected(ModemError::InvalidParameter);
        }

        val = std::clamp<int64_t>(val, 1, 31);
        return format_bitmask(unit_bits, static_cast<uint8_t>(val));
    }

private:
    static std::string format_bitmask(uint8_t unit, uint8_t val) {
        std::string res;
        res.reserve(8);
        for (int i = 2; i >= 0; --i) res.push_back(((unit >> i) & 1) ? '1' : '0');
        for (int i = 4; i >= 0; --i) res.push_back(((val >> i) & 1) ? '1' : '0');
        return res;
    }
};

/* Апаратний контролер низькорівневих інтерфейсів з RAII керуванням DTR */
class HardwareUartBus {
public:
    void send(std::string_view data);
    std::string receive_line(std::chrono::milliseconds timeout);
    void set_dtr(bool high);
    void sleep_ms(std::chrono::milliseconds ms);
};

/* Керівний клас стільникового модема */
class CellularModemManager {
public:
    explicit CellularModemManager(HardwareUartBus& bus) : bus_(bus) {}

    std::expected<void, ModemError> send_command(std::string_view cmd,
                                                 std::chrono::milliseconds timeout = 3000ms) {
        bus_.send(cmd);
        bus_.send("\r\n");

        auto start = std::chrono::steady_clock::now();
        while (std::chrono::steady_clock::now() - start < timeout) {
            auto line = bus_.receive_line(500ms);
            if (line.find("OK") != std::string::npos) return {};
            if (line.find("ERROR") != std::string::npos || line.find("+CME ERROR") != std::string::npos) {
                return std::unexpected(ModemError::InvalidResponse);
            }
        }
        return std::unexpected(ModemError::Timeout);
    }

    std::expected<void, ModemError> configure_psm_and_edrx(const PsmConfig& cfg) {
        auto t3412_str = TimerEncoder::encode_t3412(cfg.periodic_tau);
        auto t3324_str = TimerEncoder::encode_t3324(cfg.active_time);

        if (!t3412_str || !t3324_str) return std::unexpected(ModemError::InvalidParameter);

        auto cpsms_cmd = std::format("AT+CPSMS=1,,,\"{}\",\"{}\"", *t3412_str, *t3324_str);
        if (auto res = send_command(cpsms_cmd); !res) return res;

        // Конфігурація eDRX для NB-IoT (AcT=5, 40.96 с)
        return send_command("AT+CEDRXS=1,5,\"0010\"");
    }

    std::expected<void, ModemError> wait_registration(std::chrono::seconds timeout = 60s) {
        auto start = std::chrono::steady_clock::now();
        while (std::chrono::steady_clock::now() - start < timeout) {
            bus_.send("AT+CEREG?\r\n");
            auto line = bus_.receive_line(1000ms);
            if (line.find("+CEREG: 4,1") != std::string::npos ||
                line.find("+CEREG: 4,5") != std::string::npos ||
                line.find("+CEREG: 1") != std::string::npos ||
                line.find("+CEREG: 5") != std::string::npos) {
                return {};
            }
            bus_.sleep_ms(1000ms);
        }
        return std::unexpected(ModemError::RegistrationFailed);
    }

    std::expected<void, ModemError> send_udp(std::string_view host, uint16_t port,
                                             std::span<const uint8_t> payload) {
        auto open_cmd = std::format("AT+QIOPEN=1,0,\"UDP\",\"{}\",{},0,0", host, port);
        if (auto res = send_command(open_cmd); !res) return res;

        auto send_cmd = std::format("AT+QISEND=0,{}", payload.size());
        bus_.send(send_cmd);
        bus_.send("\r\n");
        bus_.sleep_ms(100ms);

        std::string_view payload_view(reinterpret_cast<const char*>(payload.data()), payload.size());
        bus_.send(payload_view);
        bus_.sleep_ms(200ms);

        return send_command("AT+QICLOSE=0");
    }

private:
    HardwareUartBus& bus_;
};

/* RAII-сесія роботи вузла зв'язку */
class ModemSessionScope {
public:
    explicit ModemSessionScope(HardwareUartBus& bus) : bus_(bus) {
        bus_.set_dtr(false); // Пробудження модема
        bus_.sleep_ms(50ms);
    }

    ~ModemSessionScope() {
        bus_.set_dtr(true); // Дозвіл модему перейти в PSM Deep Sleep
    }

private:
    HardwareUartBus& bus_;
};

void run_telemetry_cycle(HardwareUartBus& bus) {
    ModemSessionScope session(bus);
    CellularModemManager modem(bus);

    if (!modem.send_command("AT")) return;
    if (!modem.send_command("AT+CEREG=4")) return;

    PsmConfig psm{.periodic_tau = 86400s, .active_time = 10s};
    if (!modem.configure_psm_and_edrx(psm)) return;

    if (modem.wait_registration(60s)) {
        constexpr std::array<uint8_t, 8> payload = {0xAA, 0x01, 0x18, 0x2A, 0x0C, 0x55, 0x00, 0xFF};
        (void)modem.send_udp("198.51.100.42", 5683, payload);
    }
}

} // namespace cellular
```
:::

---

### Особливості обробки крайових випадків у реальних пристроях

1. **Неузгоджені значення таймерів мережею:**
   Якщо операторський вузол MME повернув у відповіді `+CEREG` інше значення таймера `Periodic-TAU` (наприклад, 2 години замість запитаних 24 годин), керівний мікроконтролер у жодному разі не повинен намагатися багаторазово перезаписувати конфігурацію в нескінченному циклі. Повторні запити `AT+CPSMS` ініціюють надмірний сигнальний трафік до базової станції, що призводить до тимчасового блокування абонентської SIM-картки за порушення політик мережі (Fair Usage Policy). Пристрій зобов'язаний зберегти виділені значення у внутрішній пам'яті та адаптувати свій графік сну.

2. **Захист від вичерпання енергії під час аварії базової станції:**
   У разі знеструмлення або технічної аварії стільникової вежі модем може нескінченно сканувати доступні частотні діапазони, споживаючи від 60 до 120 мА. Прошивка мікроконтролера повинна реалізовувати жорсткий тайм-аут процедури реєстрації (зазвичай 60–90 секунд). Якщо мережу не знайдено, живлення модема примусово вимикається (через транзисторний ключ або пін `PWRKEY`), а наступна спроба зв'язку планується за алгоритмом експоненційного відкладення (Exponential Backoff): 15 хвилин, 1 година, 6 годин, 24 години.

3. **Коректне закриття сокетів та обробка буферів:**
   Перед дозволом входу в режим PSM (підняття лінії DTR у високий стан) необхідно переконатися, що всі передані байти вийшли з вихідного FIFO-буфера модема, а сокет коректно закрито (`AT+QICLOSE`). Якщо модем засне під час активного мережевого буфера, пакет буде безповоротно втрачено, а сокет на сервері зависне у стані очікування таймауту.

4. **Контроль напруги живлення перед передачею:**
   Перед запуском сеансу зв'язку мікроконтролер зобов'язаний виміряти напругу на батареї за допомогою внутрішнього АЦП. Якщо напруга просіла нижче критичного порогу (наприклад, 3.1 В для елемента 3.6 В), запуск передавача з піковим струмом 400 мА гарантовано спричинить перезавантаження системи (Brownout Reset). У такому стані пристрій повинен записати аварійний прапорець у незалежну пам'ять EEPROM/FRAM і заснути, уникнувши зациклення збоїв.
