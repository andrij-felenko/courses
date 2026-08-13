# 📋 Інтерфейси вичитування рівнів сигналу: AT-команди та системні API

Отримання метрик рівня сигналу у промислових бездротових пристроях, стільникових модемах та мобільних операційних системах здійснюється через багаторівневий стек програмно-апаратних інтерфейсів. На нижньому рівні хост-процесор взаємодіє з радіочипсетом через текстові або двійкові команди послідовного порту (UART/USB CDC-ACM). На вищих рівнях операційна система (Linux, Android) надає системні демони та об'єктно-орієнтовані API для моніторингу якості каналу в реальному часі.

## 1. Текстовий протокол 3GPP AT-команд

Стандарт 3GPP TS 27.007 регламентує набір команд для опитування стану стільникового модуля. Взаємодія відбувається за принципом «Запит — Відповідь» через послідовний порт модема.

### Спадкова команда `AT+CSQ` (Signal Quality Query)

Команда `AT+CSQ` була створена для перших мереж GSM та 3G UMTS. Вона повертає узагальнений показник рівня сигналу `RSSI` та коефіцієнт помилок у бітах `BER`.

**Формат синтаксису:**
```text
Запит:  AT+CSQ
Відповідь: +CSQ: <rssi>,<ber>
        OK
```

#### Детальна декодувальна таблиця параметра `<rssi>`:

| Значення `<rssi>` | Обчислена потужність RSSI (дБм) | Категорія рівня сигналу | Характеристика якості |
| :---: | :---: | :---: | :---: |
| `0` | `<= -113 дБм` | Граничний / Немає сигналу | Висока ймовірність обриву зв'язку. |
| `1` | `-111 дБм` | Дуже слабкий | Можливий виклик voice, але дані не проходять. |
| `2 … 9` | `-109 … -95 дБм` | Слабкий (Poor) | Низька швидкість EDGE/3G, висока затримка. |
| `10 … 14` | `-93 … -85 дБм` | Середній (Fair) | Задовільна робота голосових та текстових послуг. |
| `15 … 19` | `-83 … -75 дБм` | Добрий (Good) | Впевнений прийом у місті. |
| `20 … 30` | `-73 … -53 дБм` | Відмінний (Excellent) | Близька відстань до базової станції. |
| `31` | `>= -51 дБм` | Максимальний | Безпосередня видимість антени. |
| `99` | Невідомо / Немає мережі | Відсутність реєстрації | Модем шукає мережу або відсутня SIM-карта. |

Переведення числового значення `<rssi>` у фізичні децибели виражається математичною залежністю:

```
RSSI_dBm = -113 + 2 · <rssi>
```

Параметр `<ber>` кодує рівень помилок у каналах з розширеним спектром від `0` (менше ніж 0.2% помилок) до `7` (понад 12.8% помилок), де `99` означає відсутність даних вимірювання.

### Розширена команда `AT+CESQ` (Extended Signal Quality)

Із появою мереж 4G LTE та 5G NR спадкова команда `AT+CSQ` втратила актуальність, оскільки вона не здатна передавати вибіркові значення RSRP та RSRQ. У специфікації 3GPP Release 11 введено команду `AT+CESQ`.

**Формат синтаксису:**
```text
Запит:  AT+CESQ
Відповідь: +CESQ: <rxlev>,<ber>,<rscp>,<ecno>,<rsrq>,<rsrp>
        OK
```

Залежно від поточного режиму роботи модема (2G, 3G, 4G або 5G), активними є відповідні поля (неактивні поля повертають граничні значення `99` або `255`).

#### Поля стандарту LTE та 5G NR:
1. **Показник `<rsrq>` (Reference Signal Received Quality):**
   - Діапазон значень: від `0` до `34` (або `255` = відсутність даних).
   - Формула розрахунку: `RSRQ_dB = -20 + 0.5 · <rsrq>`.
   - Приклад: значення `<rsrq> = 22` відповідає `RSRQ = -20 + 0.5 · 22 = -9.0 дБ`.
2. **Показник `<rsrp>` (Reference Signal Received Power):**
   - Діапазон значень: від `0` до `97` (або `255` = відсутність даних).
   - Формула розрахунку: `RSRP_dBm = -141 + <rsrp>`.
   - Приклад: значення `<rsrp> = 51` відповідає `RSRP = -141 + 51 = -90.0 дБм`.

### Вендорські пропрієтарні розширення (Quectel, SIMCom, Huawei)

Виробники стільникових модулів надають власні розширені AT-команди, які дозволяють вичитати розширені метрики (включаючи SINR та індекс активної несучої в режимі агрегації Carrier Aggregation):

- **Quectel (команда `AT+QENG="servingcell"`):**
  ```text
  +QENG: "servingcell","NOCONN","LTE","FDD",255,01,1A2B3,450,6400,20,5,5,"1C02",-92,-9,-65,15,12
  ```
  Повертає стан реєстрації, тип мережі, ID соти, номер каналу EARFCN, а також чіткий рядок метрик: `RSRP (-92 dBm)`, `RSRQ (-9 dB)`, `RSSI (-65 dBm)`, `SINR (15 dB)`.
- **SIMCom (команда `AT+CPSI?`):**
  Повертає текстовий опис стану тракту: `System Mode: LTE, Operation Mode: Online, MCC-MNC: 255-01, RSRP: -88, RSRQ: -8, RSSI: -61, SNR: 18`.

## 2. Системний стек Linux: ModemManager, QMI та MBIM

У промислових роутерах, бортових комп'ютерах та операційних системах Linux взаємодія з модемом через AT-команди є незручною, оскільки послідовний порт може бути зайнятий PPP-сесією або викликами PPP/NDIS. Для цього в Linux розроблено архітектуру викликів через DBus-демон `ModemManager`.

### Низькорівневі протоколи QMI та MBIM

Сучасні модеми з'єднуються з хостом через USB-інтерфейс і створюють віртуальні пристрої керування `/dev/cdc-wdm0`:
- **QMI (Qualcomm MSM Interface):** Двійковий пакетний протокол розробки Qualcomm.
- **MBIM (Mobile Broadband Interface Model):** Відкритий стандарт Microsoft/USB IF.

Для прямого випитування інформації про сигнал у протоколі QMI використовується утиліта `qmicli`:

```bash
qmicli -d /dev/cdc-wdm0 --nas-get-signal-info
```

**Відповідь утиліти QMI:**
```text
[/dev/cdc-wdm0] Successfully got signal info:
	LTE:
		RSSI: '-65 dBm'
		RSRP: '-91 dBm'
		RSRQ: '-8 dB'
		SNR: '16.4 dB'
	5GNR:
		RSRP: '-84 dBm'
		RSRQ: '-10 dB'
		SINR: '21.0 dB'
```

### Високрівневий DBus API ModemManager (`mmcli`)

Демон ModemManager опитує модем у фоновому режимі та надає уніфікований DBus-інтерфейс `org.freedesktop.ModemManager1.Modem.Signal`.

Виклик із командного рядка:
```bash
mmcli -m 0 --signal-get
```

Програмні опитування з Python чи C/C++ через бібліотеку `libmm-glib`:
:::tabs
```c
#include <libmm-glib.h>

void read_signal_metrics(MMModemSignal *signal_object) {
    MMSignalLte *lte_info = mm_modem_signal_get_lte(signal_object);
    if (lte_info) {
        gdouble rsrp = mm_signal_lte_get_rsrp(lte_info);
        gdouble rsrq = mm_signal_lte_get_rsrq(lte_info);
        gdouble rssi = mm_signal_lte_get_rssi(lte_info);
        gdouble snr  = mm_signal_lte_get_snr(lte_info);

        g_print("LTE Metrics -> RSRP: %.1f dBm, RSRQ: %.1f dB, RSSI: %.1f dBm, SINR: %.1f dB\n",
                rsrp, rsrq, rssi, snr);
        g_object_unref(lte_info);
    }
}
```
```cpp
#include <libmm-glib.h>
#include <iostream>
#include <memory>

void read_signal_metrics(MMModemSignal *signal_object) {
    // Використання RAII-обгортки для управління ресурсами GLib об'єкта
    using LteSignalPtr = std::unique_ptr<MMSignalLte, decltype([](MMSignalLte* p) { g_object_unref(p); })>;
    LteSignalPtr lte_info{mm_modem_signal_get_lte(signal_object)};

    if (lte_info) {
        const double rsrp = mm_signal_lte_get_rsrp(lte_info.get());
        const double rsrq = mm_signal_lte_get_rsrq(lte_info.get());
        const double rssi = mm_signal_lte_get_rssi(lte_info.get());
        const double snr  = mm_signal_lte_get_snr(lte_info.get());

        std::cout << "LTE Metrics -> RSRP: " << rsrp << " dBm, RSRQ: " << rsrq
                  << " dB, RSSI: " << rssi << " dBm, SINR: " << snr << " dB\n";
    }
}
```
:::

## 3. Telephony Framework в Android

В операційній системі Android прямий доступ до AT-команд модема заблоковано з міркувань безпеки. Отримання метрик здійснюється через системну службу Telephony Framework (Vendor RIL -> Radio HAL -> TelephonyManager).

### Об'єктна модель `CellSignalStrength`

Пакет `android.telephony` містить абстрактний клас `CellSignalStrength`, від якого успадковано специфічні класи для кожної технології: `CellSignalStrengthLte`, `CellSignalStrengthNr`, `CellSignalStrengthWcdma`.

#### Приклад вичитування метрик у Java / Kotlin:

```kotlin
import android.telephony.CellInfoLte
import android.telephony.CellSignalStrengthLte
import android.telephony.TelephonyManager

fun processLteSignalInfo(cellInfo: CellInfoLte) {
    val lteSignal: CellSignalStrengthLte = cellInfo.cellSignalStrength

    val rsrpDbm: Int = lteSignal.rsrp     // Діапазон: -140..-44 dBm
    val rsrqDb: Int = lteSignal.rsrq       // Діапазон: -20..-3 dB
    val rssiDbm: Int = lteSignal.rssi     // Загальний RSSI у dBm
    val snrDb: Int = lteSignal.rssnr       // Відношення сигнал/шум (SNR)
    val level: Int = lteSignal.level       // 5-бальна оцінка статусу (0..4)

    println("Android Telephony -> RSRP: $rsrpDbm dBm, RSRQ: $rsrqDb dB, Level: $level/4")
}
```

Обчислений метод `getLevel()` розраховує кількість «паличок» (signal bars) для графічного інтерфейсу системи. Алгоритм Android порівнює RSRP та RSQN із порогами, заданими в конфігураційному файлі оператора `carrier_config.xml`, що запобігає маніпуляціям вендорів із штучним завищенням рівня сигналу.

## 4. Зведена таблиця відповідності інтерфейсів та діапазонів

| Параметр | Одиниця виміру | Стандарт 3GPP AT (`AT+CESQ`) | Linux ModemManager | Android Telephony API |
| :--- | :--- | :--- | :--- | :--- |
| **RSSI** | дБм | `0 … 31` (`AT+CSQ`) | `mm_signal_lte_get_rssi()` | `CellSignalStrengthLte.getRssi()` |
| **RSRP** | дБм | `0 … 97` (`-141 + val`) | `mm_signal_lte_get_rsrp()` | `CellSignalStrengthLte.getRsrp()` |
| **RSRQ** | дБ | `0 … 34` (`-20 + 0.5·val`) | `mm_signal_lte_get_rsrq()` | `CellSignalStrengthLte.getRsrq()` |
| **SINR** | дБ | N/A (Вендорські розширення) | `mm_signal_lte_get_snr()` | `CellSignalStrengthLte.getRssnr()` |

Розуміння специфіки кожного з цих інтерфейсів дозволяє розробникам створювати кросплатформні системи моніторингу радіопокриття, які коректно інтерпретують дані як на вбудованих мікроконтролерах із прямою AT-командною взаємодією, так і на високорівневих серверах Linux та мобільних ОС.
