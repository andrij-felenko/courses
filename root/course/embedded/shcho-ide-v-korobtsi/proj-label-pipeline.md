# ⚙️ Конвеєр верифікації та автоматизованого друку маркування

Цей проєкт демонструє повний виробничий конвеєр для валідації ідентифікаторів вбудованого вузла, перевірки контрольних сум серійних номерів та генерації узгоджених етикеток під час пакування на складальній лінії. Без програмної верифікації неминуче виникає людська помилка, коли плата з одним серійним номером потрапляє в коробку з іншим, що руйнує гарантійний облік і блокує реєстрацію пристрою у хмарі.

---

## 1. Архітектура та послідовність верифікації під час пакування

На пакувальній ділянці діє правило обов'язкового подвійного сканування (Match-Scan). Ця процедура унеможливлює випуск продукції з невідповідністю маркування завдяки замкненому контуру перевірки між фізичним носієм, базою даних прошивання та принтером етикеток.

```
+----------------+      1. Scan Device DataMatrix      +---------------------+
| Плата в зборі  | ----------------------------------> |  Скрипт пакування   |
+----------------+                                     +---------------------+
                                                                  |
                                              2. Перевірка Luhn / | 3. Запит до бази
                                                 структури S/N    |    прошивання
                                                                  v
                                                       +---------------------+
                                                       |  База тестів заводу |
                                                       +---------------------+
                                                                  | Status == PASS
                                                                  v
+----------------+      5. Match Check OK              +---------------------+
| Готова коробка | <---------------------------------- |   Принтер етикеток  |
+----------------+                                     +---------------------+
```

### Покроковий регламент робочого місця:

1. **Сканування пристрою:** оператор ручним 2D-сканером зчитує DataMatrix безпосередньо з металевого або пластикового шильдика зібраної плати.
2. **Локальна валідація структури:** вбудований парсер перевіряє довжину рядка, префікс лінійки, коректність тижня виробництва (01..53) та контрольну цифру за алгоритмом Луна (Luhn mod 10). Якщо контрольна цифра не сходиться, сканування відхиляється миттєво без звернення до мережі.
3. **Запит до бази провізіонування:** скрипт виконує транзакційний запит до виробничої бази даних, перевіряючи, що дана комбінація S/N та MAC-адреси пройшла всі етапи функціонального тестування (FCT, Wireless Calibration) та має підсумковий статус `QA_PASS`.
4. **Генерація та друк коробкової етикетки:** тільки після підтвердження статусу з бази скрипт генерує завдання друку мовою ZPL і надсилає його через сокет на мережевий принтер Zebra.
5. **Контрольне сканування коробки (Match Verification):** оператор наклеює надруковану етикетку на зовнішню коробку та сканує її штрихкод. Якщо серійний номер коробки хоча б на один символ відрізняється від раніше відсканованої плати, система подає аварійний звуковий сигнал і блокує рух конвеєра.

---

## 2. Апаратні інтерфейси оптичних сканерів на конвеєрі

На складальних лініях використовують оптичні сканери штрихкодів, підключені за одним із трьох стандартних протоколів:

- **USB HID Keyboard Emulation:** сканер емулює швидке введення з клавіатури, завершуючи рядок символом повернення каретки (`CR` або `CR+LF`). Цей режим простий у налаштуванні, але вразливий до випадкового перемикання розкладки клавіатури на хост-комп'ютері, коли символи ASCII замінюються кирилицею.
- **USB CDC-ACM / Virtual COM Port:** сканер передає сирі байти через віртуальний послідовний порт. Це рекомендований промисловий режим, оскільки він повністю незалежний від системної мови введення хоста і дозволяє керувати світлодіодною підсвіткою та зумером сканера через спеціальні керуючі ESC-послідовності.
- **Промисловий RS-232 / RS-422:** пряме підключення до програмованих логічних контролерів (ПЛК) або одноплатних керуючих комп'ютерів із гальванічною розв'язкою.

---

## 3. Модуль розбору та валідації серійного номера

Для вбудованого тестового стенда, портативного термінала або мікроконтролера станції пакування перевірка структури виконується високоефективним кодом без динамічного виділення пам'яті. Нижче наведено еталонну реалізацію мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

#define SN_LENGTH 14

typedef struct {
    char prefix[3];       // "SN", "GW", "CT"
    uint8_t year;         // 26 -> 2026
    uint8_t week;         // 01..53
    uint16_t model_code;  // 001..999
    uint16_t sequence;    // 0001..9999
    uint8_t checksum;     // 0..9
} device_sn_t;

/* Обчислення контрольної цифри за алгоритмом Луна для цифрової частини */
static bool validate_luhn_digit(const char *digits, size_t len) {
    int sum = 0;
    bool alternate = false;

    for (int i = (int)len - 1; i >= 0; i--) {
        if (!isdigit((unsigned char)digits[i])) {
            return false;
        }
        int n = digits[i] - '0';
        if (alternate) {
            n *= 2;
            if (n > 9) {
                n = (n % 10) + 1;
            }
        }
        sum += n;
        alternate = !alternate;
    }
    return (sum % 10 == 0);
}

/* Розбір та перевірка цілісності серійного номера */
bool parse_and_validate_sn(const char *raw_sn, device_sn_t *out_sn) {
    if (!raw_sn || strlen(raw_sn) != SN_LENGTH || !out_sn) {
        return false;
    }

    // Перевірка префікса
    if (!isupper((unsigned char)raw_sn[0]) || !isupper((unsigned char)raw_sn[1])) {
        return false;
    }
    out_sn->prefix[0] = raw_sn[0];
    out_sn->prefix[1] = raw_sn[1];
    out_sn->prefix[2] = '\0';

    // Перевірка алгоритмом Луна цифрової частини (позиції 2..13)
    if (!validate_luhn_digit(raw_sn + 2, SN_LENGTH - 2)) {
        return false;
    }

    // Видобування числових полів
    out_sn->year = (uint8_t)((raw_sn[2] - '0') * 10 + (raw_sn[3] - '0'));
    out_sn->week = (uint8_t)((raw_sn[4] - '0') * 10 + (raw_sn[5] - '0'));
    out_sn->model_code = (uint16_t)((raw_sn[6] - '0') * 100 + 
                                    (raw_sn[7] - '0') * 10 + 
                                    (raw_sn[8] - '0'));
    out_sn->sequence = (uint16_t)((raw_sn[9] - '0') * 1000 + 
                                  (raw_sn[10] - '0') * 100 + 
                                  (raw_sn[11] - '0') * 10 + 
                                  (raw_sn[12] - '0'));
    out_sn->checksum = (uint8_t)(raw_sn[13] - '0');

    if (out_sn->week < 1 || out_sn->week > 53) {
        return false;
    }
    return true;
}
```
```cpp
#include <string_view>
#include <optional>
#include <array>
#include <cstdint>
#include <cctype>

struct DeviceSerialNumber {
    std::array<char, 3> prefix{};
    uint8_t year{0};
    uint8_t week{0};
    uint16_t modelCode{0};
    uint16_t sequence{0};
    uint8_t checksum{0};
};

class SerialNumberValidator {
public:
    static constexpr size_t kLength = 14;

    static constexpr bool ValidateLuhn(std::string_view digits) noexcept {
        int sum = 0;
        bool alternate = false;

        for (auto it = digits.rbegin(); it != digits.rend(); ++it) {
            if (!std::isdigit(static_cast<unsigned char>(*it))) {
                return false;
            }
            int n = *it - '0';
            if (alternate) {
                n *= 2;
                if (n > 9) {
                    n = (n % 10) + 1;
                }
            }
            sum += n;
            alternate = !alternate;
        }
        return (sum % 10 == 0);
    }

    static std::optional<DeviceSerialNumber> Parse(std::string_view raw) noexcept {
        if (raw.size() != kLength) {
            return std::nullopt;
        }

        if (!std::isupper(static_cast<unsigned char>(raw[0])) ||
            !std::isupper(static_cast<unsigned char>(raw[1]))) {
            return std::nullopt;
        }

        // Перевірка контрольної суми Луна для позицій 2..13
        if (!ValidateLuhn(raw.substr(2))) {
            return std::nullopt;
        }

        DeviceSerialNumber sn{};
        sn.prefix[0] = raw[0];
        sn.prefix[1] = raw[1];
        sn.prefix[2] = '\0';

        sn.year = static_cast<uint8_t>((raw[2] - '0') * 10 + (raw[3] - '0'));
        sn.week = static_cast<uint8_t>((raw[4] - '0') * 10 + (raw[5] - '0'));
        sn.modelCode = static_cast<uint16_t>((raw[6] - '0') * 100 + 
                                             (raw[7] - '0') * 10 + 
                                             (raw[8] - '0'));
        sn.sequence = static_cast<uint16_t>((raw[9] - '0') * 1000 + 
                                            (raw[10] - '0') * 100 + 
                                            (raw[11] - '0') * 10 + 
                                            (raw[12] - '0'));
        sn.checksum = static_cast<uint8_t>(raw[13] - '0');

        if (sn.week < 1 || sn.week > 53) {
            return std::nullopt;
        }
        return sn;
    }
};
```
:::

---

## 4. Серверний скрипт автоматизації робочого місця пакування

Скрипт мовою Python керує всім циклом взаємодії з апаратним сканером, виробничою базою SQLite та промисловим термотрансферним принтером Zebra через мережевий порт Raw TCP 9100.

```py
#!/usr/bin/env python3
import socket
import sqlite3
import re
import sys
from datetime import datetime

PRINTER_IP = "192.168.10.50"
PRINTER_PORT = 9100
DB_PATH = "/var/factory/production.db"

def calculate_luhn_checksum(payload: str) -> int:
    """Обчислення контрольної цифри Луна для числового рядка."""
    digits = [int(c) for c in payload if c.isdigit()]
    total = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 0:
            doubled = digit * 2
            total += (doubled % 10) + 1 if doubled > 9 else doubled
        else:
            total += digit
    return (10 - (total % 10)) % 10

def generate_zpl(sn: str, mac: str, batch: str, pin: str, prov_hash: str) -> str:
    """Генерація розмітки ZPL для коробкової етикетки 100x60 мм."""
    uri = f"https://onboard.acme-iot.com/pair?v=1&sn={sn}&mac={mac}&pin={pin}&t={prov_hash[:16]}"
    mac_clean = mac.replace(":", "").upper()
    now_str = datetime.utcnow().strftime("%Y-%m-%d")

    return f"""^XA
^PW1181^LL0708^LH0,0
^FO50,40^A0N,32,32^FDPRO-GATEWAY INDUSTRIAL NODE KIT^FS
^FO50,80^A0N,24,24^FDSKU: GW-500-ETH-LTE-EU   Qty: 1 PC^FS
^FO50,110^GB1080,2,2^FS

^FO50,130^A0N,20,20^FDSerial Number:^FS
^FO50,155^BCN,60,Y,N,N^FD{sn}^FS

^FO50,260^A0N,20,20^FDEthernet MAC Address:^FS
^FO50,285^BCN,60,Y,N,N^FD{mac_clean}^FS

^FO820,140^BQN,2,6^FDQA,{uri}^FS
^FO800,320^A0N,18,18^FDSCAN TO ONBOARD^FS

^FO50,380^GB1080,2,2^FS
^FO50,405^A0N,22,22^FDBatch: {batch}   Date: {now_str}   Test: QA-PASS^FS
^FO50,435^A0N,20,20^FDWeight: 485 g    HW Rev: 2.1        FW: v1.4.0^FS
^FO50,465^A0N,18,18^FDProv Hash: {prov_hash[:16]} (Ed25519 Verified)^FS

^FO50,510^GB1080,75,2^FS
^FO65,525^A0N,20,20^FDUWAGA: S/N and MAC must match internal device plate!^FS
^FO65,555^A0N,18,18^FDVerify tamper seal integrity before installation. RoHS Compliant.^FS
^XZ"""

def pack_station_process(scanned_device_dm: str):
    """Обробка події сканування пристрою на столі пакування."""
    # Приклад вхідного рядка з DataMatrix: "SN263400101237;MAC=001A223B4C5D;HASH=a4f833c188099b12"
    m = re.match(r"(SN\d{12});MAC=([0-9A-Fa-f]{12});HASH=([0-9A-Fa-f]+)", scanned_device_dm)
    if not m:
        print("[ERROR] Невалідний формат DataMatrix на корпусі пристрою!")
        return False

    sn, mac, prov_hash = m.group(1), m.group(2).upper(), m.group(3)

    # Звірка з виробничою БД
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT test_status, batch_id, setup_pin FROM units WHERE sn = ? AND mac = ?", (sn, mac))
    row = cur.fetchone()

    if not row:
        print(f"[REJECT] Пристрій {sn} не знайдено в базі випуску!")
        return False

    status, batch, pin = row
    if status != "PASS":
        print(f"[REJECT] Пристрій {sn} має статус тесту '{status}'. Пакування заборонено!")
        return False

    # Генерація ZPL та відправка на принтер
    zpl_data = generate_zpl(sn, mac, batch, pin, prov_hash)
    try:
        with socket.create_connection((PRINTER_IP, PRINTER_PORT), timeout=3.0) as sock:
            sock.sendall(zpl_data.encode("utf-8"))
        print(f"[SUCCESS] Етикетку для {sn} успішно видрукувано на {PRINTER_IP}")
        return True
    except Exception as e:
        print(f"[ERROR] Помилка зв'язку з принтером Zebra: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pack_station_process(sys.argv[1])
    else:
        # Тестовий запуск
        pack_station_process("SN263400101237;MAC=001A223B4C5D;HASH=a4f833c188099b12")
```

---

## 5. Практичні пастки та крайові випадки на пакувальній лінії

1. **Неузгодженість MAC-адрес при кількох інтерфейсах:** коли пристрій має одночасно Ethernet, Wi-Fi та Bluetooth, кожен трансивер володіє власною апаратною MAC-адресою з виділеного пулу OUI. Якщо на коробці надруковано адресу Wi-Fi, а системний адміністратор на об'єкті налаштовує статичну таблицю маршрутизації за Ethernet MAC, прилад не отримає IP-адресу через DHCP. На шильдику та коробці завжди друкують суворо первинну базову адресу пулу (Base MAC) або явно підписують інтерфейс: `ETH MAC`.
2. **Втрата контрасту прямого термодруку:** використання паперу прямого термодруку (Direct Thermal) на складах тривалого зберігання є неприпустимим, оскільки від нагріву влітку чи дії сонячних променів папір темніє і перестає зчитуватися сканером. Виробничий конвеєр зобов'язаний використовувати термотрансферний друк зі смоляним ріббоном.
3. **Робота лінії при відмові мережі заводу (Offline Resilience):** якщо центральний сервер MES стає недоступним через аварію мережі, робочі місця пакування не повинні зупинятися. Станція пакування підтримує локальний кеш підписаних криптографічних маніфестів поточної партії. Кожен запис про упакований екземпляр записується в локальний WAL-журнал (Write-Ahead Logging) SQLite і автоматично синхронізується з сервером після відновлення зв'язку.
4. **Забуті комплектуючі та відхилення ваги:** людський фактор на пакувальному столі неминуче призводить до того, що оператор забуває покласти антену чи пакет кріплення. Автоматичні конвеєрні ваги (Checkweigher) з точністю `±1 г` зважують закриту коробку: якщо маса відхиляється від технологічної карти більш ніж на `5 г`, коробка автоматично відхиляється пневмоштовхачем на стіл інспекції.
