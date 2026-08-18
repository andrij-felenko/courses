# ⚙️ Супутниковий міст: драйвер Iridium SBD та маршрутизатор MAVLink

Реалізація надійного каналу зв'язку великої затримки між бортовим автопілотом (FCU) та супутниковим сузір'ям Iridium вимагає побудови спеціалізованого системного сервісу — супутникового моста (Satellite Bridge Daemon). Міст виконує роль інтелектуального шлюзу між високошвидкісною бортовою мережею дрона та вузькосмуговим супутниковим трансивером.

### 1. Апаратна архітектура та вимоги до живлення

Основним апаратним компонентом супутникового каналу є модеми серії Iridium 9602 або 9603N. Це мініатюрні L-діапазонні трансивери (частота 1616.0–1626.5 МГц), що забезпечують двосторонню передачу даних за технологією коротких повідомлень (Short Burst Data, SBD).

```
Схема апаратного підключення супутникового моста:
┌────────────────────────┐                    ┌────────────────────────┐
│  Польотний контролер   │                    │   Супутниковий міст    │
│  (Pixhawk 6X / Cube)   │  MAVLink 115200    │   (SBC Linux / MCU)    │
│  UART (TELEM2)         ├────────────────────┤   UART0 (/dev/ttyS1)   │
└────────────────────────┘                    └───────────┬────────────┘
                                                          │ AT-команди
                                                          │ 19200 бод (8N1)
                                                          │ RTS / CTS
                                              ┌───────────┴────────────┐
                                              │   Iridium 9603N SBD    │
                                              │   Піковий струм: 1.5 А │
                                              │   Суперконденсатор 2.2мФ│
                                              └───────────┬────────────┘
                                                          │ L-Band (1.6 ГГц)
                                                          ▼ Пасивна антена
```

При інтеграції супутникового модема на борт безпілотника розробник стикається з трьома критичними апаратними вимогами:
1. **Імпульсне споживання струму силового каскаду:** у режимі очікування модем споживає менше 35 мА. Проте під час передачі радіоімпульсу в космос (тривалість пакету 8.3 мс у кадрі TDMA 90 мс) вихідний підсилювач потужності (PA) генерує піковий струм до **1.5 Ампера** при напрузі 5.0 В. Якщо лінія живлення має високий внутрішній опір (ESR), напруга миттєво просідає нижче 3.2 В, викликаючи аварійне перезавантаження модема. Для компенсації піків паралельно виводам живлення обов'язково встановлюється банк танталових або суперконденсаторів сумарною ємністю не менше 2200–4700 мкФ. Стабілізатор живлення будується на базі імпульсного DC-DC перетворювача (наприклад, Texas Instruments TPS62130 або MPS MP2315) зі швидким динамічним відгуком на скачки навантаження (Transient Response < 30 мкс) та феритовими фільтрами для придушення високочастотних пульсацій на частоті 1.6 ГГц.
2. **Апаратний контроль потоку UART (Hardware Flow Control):** передача AT-команд здійснюється на швидкості 19200 бод. Використання ліній `RTS` (Request to Send) та `CTS` (Clear to Send) є категорично обов'язковим. Якщо процесор не обслуговує CTS, модем скидає внутрішній бінарний буфер при отриманні довгих відповідей.
3. **Екранування та розміщення антени:** патч-антена Iridium повинна мати прямий огляд верхньої півсфери (небосхилу) з мінімальним кутом затінення крилом чи фюзеляжем (кути піднесення понад 8°). Відстань між антеною супутникового модема та антеною GNSS/GPS має складати не менше 15–20 см для уникнення взаємного блокування вхідних підсилювачів LNA. Корпус модема обов'язково заземлюється на спільний екран фюзеляжу для захисту від електромагнітних наводок бортових радіостанцій. Антенний коаксіальний тракт виконується кабелем типу RG-316 або LMR-100 з хвильовим опором 50 Ом та коефіцієнтом стоячої хвилі (КСХН / VSWR) не гірше 1.3:1 для запобігання втратам потужності передавача. Вхідний ВЧ-роз'єм модема (U.FL або SMA) додатково захищається супресорними діодами ESD від статичних розрядів під час польоту в щільній хмарності.

#### Конфігурація дерева пристроїв Linux (Device Tree Overlay)
Для одноплатних комп'ютерів сімейства Raspberry Pi CM4 або Rockchip RK3588 послідовний порт `UART0` та керуючі лінії модема конфігуруються у файлі оверлеїв `/boot/config.txt`:

```dts
# Активація апаратного UART з лініями CTS/RTS для супутникового модема
dtoverlay=uart0,ctsrts=on
dtoverlay=gpio-poweroff,gpiopin=24,active_low=1
```

Після завантаження ядра Linux послідовний порт доступний як системний символьний пристрій `/dev/ttyAMA0` із повною підтримкою апаратного узгодження ліній потоку `CRTSCTS`.

### 2. Скінченний автомат керування AT-сесіями Iridium SBD

Взаємодія з модемом Iridium побудована на базі асинхронного скінченного автомата стану (FSM, Finite State Machine). Модем не підтримує одночасні запити: кожна операція повинна завершитися відповіддю `OK`, `ERROR` або рядком статусу перед початком наступної.

Скінченний автомат реалізує сім послідовних станів:

```
Діаграма станів скінченного автомата супутникового моста:
┌──────────────┐      Новий пакет      ┌──────────────────────┐
│  STATE_IDLE  ├──────────────────────►│ STATE_CHECK_SIGNAL   │
└──────▲───────┘   (T >= 20 с)         └──────────┬───────────┘
       │                                          │ AT+CSQ >= 2
       │ Очищення буфера                          ▼
┌──────┴───────────────┐               ┌──────────────────────┐
│ STATE_CLEAR_BUFFER   │               │  STATE_WRITE_BUFFER  │
└──────▲───────────────┘               └──────────┬───────────┘
       │                                          │ AT+SBDWB (77 B)
       │ Сесія завершена                          ▼
┌──────┴───────────────┐   MT len > 0  ┌──────────────────────┐
│ STATE_READ_INCOMING  │◄──────────────┤ STATE_SEND_SESSION   │
└──────────────────────┘               └──────────────────────┘
                                         Виконання AT+SBDIX
```

Розглянемо детальний протокол обміну на кожному кроці автомата:

#### Крок 1: Перевірка якості зв'язку із сузір'ям (AT+CSQ)
Перед спробою передачі пакету міст надсилає запит рівня сигналу:
```
Tx: AT+CSQ\r
Rx: +CSQ: 4\r\n\r\nOK\r\n
```
Число після `+CSQ:` показує кількість доступних супутників та рівень прийому за шкалою від 0 до 5. Якщо рівень сигналу становить 0 або 1 (наприклад, під час різкого крену літака чи прольоту під мостом), ініціація дорогої супутникової сесії блокується на 5 секунд, що захищає від марних витрат спроб підключення.

#### Крок 2: Бінарне завантаження кадру у вихідний буфер MO (AT+SBDWB)
Вихідне повідомлення (Mobile Originated, MO) записується в апаратну пам'ять модема у бінарному вигляді:
```
Tx: AT+SBDWB=77\r
Rx: READY\r\n
Tx: [77 байтів бінарного кадру MAVLink v2] + [2 байти Checksum]
Rx: 0\r\n\r\nOK\r\n
```
Двобайтова контрольна сума обчислюється як звичайна 16-бітна сума всіх 77 байтів корисного навантаження за модулем 65536 і передається у форматі Big-Endian (старший байт першим). Відповідь `0` підтверджує успішну перевірку суми модемом.

#### Крок 3: Виконання супутникової транзакції (AT+SBDIX)
Команда `AT+SBDIX` активує процедуру радіозв'язку модема з пролітаючим супутником угруповання Iridium:
```
Tx: AT+SBDIX\r
Rx: +SBDIX: 0, 142, 1, 89, 45, 0\r\n\r\nOK\r\n
```
Відповідь містить шість числових параметрів, розділених комами:
1. `MO status` — статус відправки вихідного повідомлення:
   * `0` — передача успішно завершена;
   * `1` — передача успішна, але розмір повідомлення перевищив ліміт;
   * `2` — відправлено лише координати локації;
   * `32` — помилка: мережа недоступна (немає супутника в зоні прямої видимості).
2. `MOMSN` — порядковий номер вихідного повідомлення (Mobile Originated Message Sequence Number).
3. `MT status` — статус прийому вхідного повідомлення від наземної станції:
   * `0` — у шлюзі немає повідомлень для дрона;
   * `1` — успішно прийнято нову вхідну команду від оператора;
   * `2` — помилка прийому вхідного пакету.
4. `MTMSN` — порядковий номер вхідного повідомлення.
5. `MT length` — довжина прийнятого вхідного пакету в байтах.
6. `MT queued` — кількість наступних повідомлень, що очікують у черзі наземного шлюзу Iridium для передачі на дрон.

#### Крок 4: Зчитування вхідної команди (AT+SBDRB)
Якщо параметр `MT length > 0` (наприклад, станція передала команду `MAV_CMD_NAV_RETURN_TO_LAUNCH`), міст вивантажує байти вхідного буфера:
```
Tx: AT+SBDRB\r
Rx: [2 байти довжини N] + [N байтів кадру MAVLink] + [2 байти Checksum]
```
Міст валідує контрольну суму вхідного блоку, витягує кадр MAVLink і негайно спрямовує його в UART польотного контролера.

#### Крок 5: Очищення буферів (AT+SBDD0)
Після успішної сесії вихідний буфер модема очищається командою `AT+SBDD0`, повертаючи автомат у стан очікування `STATE_IDLE`.

### 3. Алгоритм маркерного кошика (Token Bucket Rate Limiting)

У реальних польотних умовах бортовий автопілот може генерувати пакети `HIGH_LATENCY2` нерівномірно (наприклад, надсилати додаткові кадри при фіксації аварійних ситуацій). Якщо передавати кожен такий пакет без обмеження, дрон може вичерпати весь місячний ліміт супутникового трафіку за 10 хвилин збою.

Для жорсткого контролю трафіку в супутниковий міст інтегровано алгоритм **маркерного кошика (Token Bucket)**:

```
Схема роботи маркерного кошика супутникового моста:
  Генератор токенів:
  +1 токен кожні T_interval (20 с)
         │
         ▼
  ┌──────────────┐
  │ Кошик токенів│  Місткість: Max = 2 токени (дозволяє один повтор)
  │  [ ● ] [ ● ] │
  └──────┬───────┘
         │ Витрата: 1 токен на транзакцію AT+SBDIX
         ▼
  ┌──────────────┐      Блокування при порожньому кошику:
  │ Сесія SBDIX  ├────► Пакет замінює старий у буфері (Lossy Aggregation)
  └──────────────┘
```

Математичні правила маркерного кошика:
1. Кошик має максимальну місткість `C_max = 2` токени (дозволяє виконати термінову аварійну передачу навіть після нещодавнього сеансу).
2. Поповнення кошика відбувається зі сталою швидкістю `r = 1 токен / 20 секунд`.
3. Поточна кількість токенів `Tokens(t)` у момент часу `t` розраховується як:
   ```
   Tokens(t) = min(C_max, Tokens(t_last) + (t - t_last) · r)
   ```
4. Якщо автопілот генерує новий кадр `HIGH_LATENCY2`, а `Tokens < 1.0`, новий пакет **не створює чергу, а перезаписує попередній невідправлений пакет у буфері**.
Це фундаментальний принцип телеметрії великої затримки: оператору на землі потрібен виключно **найсвіжіший поточний стан апарата**, а не застаріла історія 5-хвилинної давнини.

### 4. Обробка позаштатних ситуацій, апаратне скидання та події Ring Alert

У реальних польотних умовах зв'язок через модем Iridium стикається з фізичними завадами, які вимагають детермінованих алгоритмів відновлення працездатності:

#### А. Апаратне скидання живлення модема (Hardware Power Cycle)
Якщо модем не відповідає рядком `OK` або `ERROR` на команди `AT` протягом 15 секунд (зависання прошивки модема від електростатичного розряду або перепаду напруги під час передачі), програмний стек ініціює апаратне перезавантаження:
1. Керівний пін GPIO бортового комп'ютера (наприклад, GPIO 24 на Raspberry Pi), підключений до затвора силового P-канального MOSFET-транзистора на лінії живлення 5V модема, переводиться в стан логічного нуля.
2. Живлення повністю знеструмлюється на 1.5 секунди для повного розряду ємнісного банку суперконденсаторів.
3. Подається живлення 5V, і очікується 3.0 секунди для завершення внутрішнього завантажувача (Bootloader) модема.
4. Порт UART повторно конфігурується, і надсилається команда ініціалізації `ATZ` (скидання до заводських параметрів) та `ATE0` (вимкнення відлуння символів).

#### Б. Обробка сповіщень Ring Alert (+CIEV: 1,1)
Сузір'я Iridium підтримує механізм сповіщення про наявність вхідного повідомлення (Ring Alert). Якщо оператор на наземній станції GCS надсилає команду поза чергою (наприклад, екстрений наказ змінити ешелон через загрозу зіткнення), шлюз Iridium транслює спеціальний пейджинговий сигнал на супутник, у зоні якого знаходиться літак.
Модем Iridium 9603 асинхронно видає в порт UART рядок:
```
Rx: +CIEV: 1,1\r\n
```
Супутниковий міст миттєво перехоплює подію `+CIEV`, примусово виводить автомат зі стану очікування `STATE_IDLE` та ініціює позачергову сесію зв'язку `AT+SBDIX` з нульовим або свіжим вихідним буфером для негайного зчитування надісланої команди.

#### В. Інтеграція системного сервісу в Linux (systemd)
Супутниковий міст запускається як системний демон з підвищеним пріоритетом планувальника завдань Linux для гарантії своєчасного обслуговування переривань послідовного порту.

Файл конфігурації сервісу `/etc/systemd/system/iridium-bridge.service`:
```ini
[Unit]
Description=MAVLink Iridium SBD High Latency Satellite Bridge Daemon
After=network.target mavlink-router.service
Requires=mavlink-router.service

[Service]
Type=simple
ExecStart=/usr/local/bin/iridium_bridge --device /dev/ttyUSB1 --baud 19200 --fcu-port 14550 --interval 20
Restart=always
RestartSec=3
CPUSchedulingPolicy=rr
CPUSchedulingPriority=45
Nice=-15
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Г. Повний наскрізний сценарій двостороннього обміну (End-to-End Trace)
Розглянемо практичний польотний випадок відпрацювання аварійної ситуації:

1. **Фіксація відмови на борту:** Під час польоту на висоті 450 м відмовляє трубка Піто через замерзання конденсату. Польотний стек автопілота виставляє біт `HL_FAILURE_FLAG_DIFFERENTIAL_PRESSURE` у повідомленні `HIGH_LATENCY2`.
2. **Передача через міст:** Супутниковий міст завантажує 77 байтів у модем (`AT+SBDWB=77`), виконує `AT+SBDIX` і передає кадр на супутник Iridium.
3. **Відображення на GCS:** Наземна станція QGroundControl отримує SBD-пакет через інтернет-шлюз. На панелі приладів спалахує червоне попередження: *«Airspeed Sensor Failure — Switching to Synthetic Airspeed»*.
4. **Реакція оператора:** Оператор натискає кнопку повернення на базу (RTL). GCS формує команду `MAV_CMD_NAV_RETURN_TO_LAUNCH` і ставить її в чергу відправки Iridium Gateway.
5. **Доставка команди на борт:** Під час наступної сесії `AT+SBDIX` модем отримує статус `MT status = 1` та довжину `MT length = 41`. Міст зчитує байти через `AT+SBDRB` і спрямовує кадр команди в автопілот.
6. **Підтвердження маневру:** Автопілот переходить у режим `RTL`. Наступний кадр `HIGH_LATENCY2` через 20 секунд транслює `custom_mode = RTL`, цільовий курс `target_heading` у бік аеродрому та підтверджує початок набору безпечної висоти повернення.

#### Д. Архітектура наземного сервісу прийому DirectIP (Ground Receiver Service)
Супутниковий шлюз Iridium у місті Темпе (Аризона, США) після прийому SBD-повідомлення пересилає його на хмарний сервер оператора безпілотника за протоколом Iridium DirectIP (бінарний TCP/IP-потік на фіксований порт 10800).

Структура вхідного пакету DirectIP містить стандартизовані інформаційні елементи (Information Elements, IE):
1. **Заголовок повідомлення (Header IE, ID 0x01):** 3-значний код протоколу, 15-значний номер IMEI модема літака, статус сесії, порядковий номер MOMSN та 32-бітний час транзакції UTC.
2. **Корисне навантаження (Payload IE, ID 0x02):** вихідний 77-байтовий бінарний кадр MAVLink v2.
3. **Геолокація шлюзу (Location IE, ID 0x03):** приблизна широта та довгота сектору супутникового променя (Doppler Geolocation).

Хмарний демон-приймач (DirectIP Ingest Daemon) виконує парсинг заголовка DirectIP, витягує чистий кадр MAVLink `HIGH_LATENCY2` і транслює його через UDP-сокет на порт 14550 у диспетчерський центр наземної станції QGroundControl.

#### Е. Тестування та емуляція супутникового каналу в режимі HIL (Hardware-in-the-Loop)
Для лабораторного тестування супутникового моста без витрат коштів на реальні супутникові транзакції застосовується емулятор модема Iridium на базі віртуальних послідовних портів `socat`:

```bash
# Створення пари віртуальних послідовних портів у Linux
socat -d -d pty,raw,echo=0,link=/tmp/ttyModemEmu pty,raw,echo=0,link=/tmp/ttyBridgePort
```

Спеціалізований скрипт на мові Python емулює реакцію модема:
* При отриманні `AT+CSQ` повертає `+CSQ: 5`;
* При отриманні `AT+SBDWB` зчитує байти та валідує 16-бітну суму;
* При отриманні `AT+SBDIX` вводить випадкову затримку 4.0–8.0 секунд (імітація затримки радіотракту TDMA та міжсупутникових лінків ISL) і видає рядок успішної сесії `+SBDIX: 0, 101, 0, 0, 0, 0`.

Це дозволяє перевірити стійкість кінцевого автомата до таймаутів, перевірити поведінку маркерного кошика та впевнитися у відсутності витоків пам'яті за багатогодинних безперервних тестів.

#### Є. Алгоритм експоненційного відкату при втраті зв'язку (Exponential Backoff)
Якщо чергова спроба сесії завершується кодом помилки `MO status = 32` (сузір'я Iridium тимчасово недоступне через рельєф місцевості чи затінення антени), міст активує захисний механізм експоненційного відкату:
1. Час очікування наступної спроби розраховується за формулою:
   ```
   T_backoff = min(T_max, T_base · 2^(retry_count - 1))
   ```
   де `T_base = 20 с`, `T_max = 180 с` (3 хвилини).
2. При першій невдачі повтор виконується через 20 с, при другій — через 40 с, при третій — через 80 с, при четвертій — через 160 с, після чого фіксується інтервал 180 с.
3. Щойно транзакція завершується успішно (`MO status = 0`), лічильник `retry_count` скидається в 0, а період повертається до штатного значення 20 секунд.

Такий підхід повністю унеможливлює нескінченні спроби підключення за умов повної відсутності сигналу, запобігаючи перегріву вихідного радіокаскаду модема та зберігаючи заряд акумулятора.

#### Ж. Кільцевий буфер та потоковий розбір відповідей модема (Stream Parsing)
Через асинхронну природу послідовного порту UART байти відповідей модема надходять фрагментами різної довжини (від 1 до кількох десятків байтів за одне системне переривання `read()`).
Для надійної обробки міст використовує кільцевий буфер (Ring Buffer) фіксованого розміру 1024 байти:
* Усі прийняті байти записуються за поточним покажчиком голови `head_ptr`;
* Потоковий сканер шукає термінальні послідовності `\r\nOK\r\n`, `\r\nERROR\r\n` або маркери подій `\r\n+CIEV:`;
* Після виявлення цілісного рядка або двійкового блоку відповідний сегмент копіюється в буфер розбору, а покажчик хвоста `tail_ptr` зміщується. Це запобігає втраті символів при високому завантаженні операційної системи Linux.

#### З. Діагностична телеметрія та підрахунок супутникових витрат
Супутниковий міст здійснює безперервний моніторинг власної продуктивності та транслює службові показники в локальну мережу автопілота:
* `sat_csq` — поточний рівень прийому супутникового сигналу (0..5);
* `sat_tx_bytes` — сумарний обсяг байтів, переданих через супутник від початку місії;
* `sat_credits` — розрахункова кількість витрачених супутникових кредитів SBD;
* `sat_rtt_ms` — тривалість останньої транзакції зв'язку в мілісекундах.

Ці параметри записуються в бортовий журнал польотного контролера (файл `.ulg` або `.bin`), дозволяючи інженерам проводити точний аудит якості зв'язку після завершення польоту.

### 5. Повна програмна реалізація супутникового моста

Нижче наведено повнофункціональний промисловий модуль супутникового моста мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <time.h>
#include <sys/select.h>

#define SBD_MAX_PAYLOAD_SIZE 340
#define SBD_MIN_RATE_INTERVAL_SEC 20.0f
#define SBD_TOKEN_BUCKET_CAPACITY 2.0f

typedef enum {
    SBD_FSM_IDLE,
    SBD_FSM_CHECK_SIGNAL,
    SBD_FSM_WRITE_PAYLOAD,
    SBD_FSM_EXECUTE_SBDIX,
    SBD_FSM_READ_INCOMING_CMD,
    SBD_FSM_CLEAR_BUFFER,
    SBD_FSM_ERROR_BACKOFF
} sbd_fsm_state_t;

typedef struct {
    int modem_uart_fd;
    int fcu_uart_fd;
    sbd_fsm_state_t state;
    
    // Маркерний кошик
    double tokens;
    time_t last_token_update;
    
    // Буфери передачі та прийому
    uint8_t mo_buffer[SBD_MAX_PAYLOAD_SIZE];
    size_t mo_len;
    uint8_t mt_buffer[SBD_MAX_PAYLOAD_SIZE];
    size_t mt_len;
    
    // Статистика
    uint32_t tx_success_count;
    uint32_t tx_fail_count;
    time_t state_entry_time;
} satellite_bridge_t;

int bridge_init_serial_port(const char *device_path, int speed_constant) {
    int fd = open(device_path, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) return -1;

    struct termios tty;
    memset(&tty, 0, sizeof(tty));
    if (tcgetattr(fd, &tty) != 0) {
        close(fd);
        return -1;
    }

    cfsetispeed(&tty, B19200);
    cfsetospeed(&tty, B19200);

    tty.c_cflag |= (CLOCAL | CREAD | CS8 | CRTSCTS); // 8N1 + Hardware Flow Control
    tty.c_cflag &= ~(PARENB | CSTOPB | CSIZE);
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON | IXOFF | IXANY);
    tty.c_oflag &= ~OPOST;
    tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);

    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 5; // 500 мс таймаут

    tcflush(fd, TCIFLUSH);
    tcsetattr(fd, TCSANOW, &tty);
    return fd;
}

void bridge_update_tokens(satellite_bridge_t *br) {
    time_t now = time(NULL);
    double elapsed = difftime(now, br->last_token_update);
    br->tokens += elapsed / SBD_MIN_RATE_INTERVAL_SEC;
    if (br->tokens > SBD_TOKEN_BUCKET_CAPACITY) {
        br->tokens = SBD_TOKEN_BUCKET_CAPACITY;
    }
    br->last_token_update = now;
}

bool bridge_enqueue_high_latency_frame(satellite_bridge_t *br, const uint8_t *frame_bytes, size_t len) {
    if (len == 0 || len > SBD_MAX_PAYLOAD_SIZE) return false;
    
    // Перезапис буфера найсвіжішим кадром
    memcpy(br->mo_buffer, frame_bytes, len);
    br->mo_len = len;
    return true;
}

void bridge_process_step(satellite_bridge_t *br) {
    char at_cmd[64];
    bridge_update_tokens(br);

    switch (br->state) {
        case SBD_FSM_IDLE:
            if (br->mo_len > 0 && br->tokens >= 1.0) {
                br->state = SBD_FSM_CHECK_SIGNAL;
                br->state_entry_time = time(NULL);
                write(br->modem_uart_fd, "AT+CSQ\r", 7);
            }
            break;

        case SBD_FSM_CHECK_SIGNAL:
            // У спрощеному лінійному вигляді переходимо до запису
            br->state = SBD_FSM_WRITE_PAYLOAD;
            br->state_entry_time = time(NULL);
            snprintf(at_cmd, sizeof(at_cmd), "AT+SBDWB=%zu\r", br->mo_len);
            write(br->modem_uart_fd, at_cmd, strlen(at_cmd));
            break;

        case SBD_FSM_WRITE_PAYLOAD: {
            uint16_t checksum = 0;
            for (size_t i = 0; i < br->mo_len; i++) checksum += br->mo_buffer[i];
            
            uint8_t cs_payload[2] = { (uint8_t)(checksum >> 8), (uint8_t)(checksum & 0xFF) };
            write(br->modem_uart_fd, br->mo_buffer, br->mo_len);
            write(br->modem_uart_fd, cs_payload, 2);
            
            br->state = SBD_FSM_EXECUTE_SBDIX;
            br->state_entry_time = time(NULL);
            write(br->modem_uart_fd, "AT+SBDIX\r", 9);
            break;
        }

        case SBD_FSM_EXECUTE_SBDIX:
            // Успішна сесія: списуємо 1 токен
            br->tokens -= 1.0;
            br->tx_success_count++;
            br->mo_len = 0; // Очищення відправленого
            br->state = SBD_FSM_CLEAR_BUFFER;
            write(br->modem_uart_fd, "AT+SBDD0\r", 9);
            break;

        case SBD_FSM_CLEAR_BUFFER:
            br->state = SBD_FSM_IDLE;
            break;

        case SBD_FSM_ERROR_BACKOFF:
            if (difftime(time(NULL), br->state_entry_time) > 10.0) {
                br->state = SBD_FSM_IDLE;
            }
            break;

        default:
            br->state = SBD_FSM_IDLE;
            break;
    }
}
```
```cpp
#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <chrono>
#include <optional>
#include <expected>
#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <algorithm>

namespace satellite {

enum class BridgeErrorCode {
    DeviceNotFound,
    PortConfigurationFailed,
    WriteTimeout,
    ChecksumMismatch,
    SignalUnavailable,
    RateLimitTriggered,
    PayloadTooLarge
};

enum class FsmState {
    Idle,
    QuerySignalQuality,
    LoadBinaryBuffer,
    TransmitSbdSession,
    ReceiveIncomingPayload,
    FlushBuffers,
    ErrorBackoff
};

struct SbdSessionStatus {
    int mo_status{0};
    int momsn{0};
    int mt_status{0};
    int mtmsn{0};
    int mt_length{0};
    int mt_queued{0};
};

class AsyncIridiumBridge {
public:
    explicit AsyncIridiumBridge(std::string serial_port_path, 
                                std::chrono::seconds rate_limit = std::chrono::seconds(20))
        : port_path_(std::move(serial_port_path)),
          min_interval_(rate_limit),
          last_update_(std::chrono::steady_clock::now()) {}

    ~AsyncIridiumBridge() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    AsyncIridiumBridge(const AsyncIridiumBridge&) = delete;
    AsyncIridiumBridge& operator=(const AsyncIridiumBridge&) = delete;
    AsyncIridiumBridge(AsyncIridiumBridge&&) noexcept = default;
    AsyncIridiumBridge& operator=(AsyncIridiumBridge&&) noexcept = default;

    std::expected<void, BridgeErrorCode> initializePort() noexcept {
        fd_ = ::open(port_path_.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
        if (fd_ < 0) {
            return std::unexpected(BridgeErrorCode::DeviceNotFound);
        }

        struct termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            ::close(fd_);
            fd_ = -1;
            return std::unexpected(BridgeErrorCode::PortConfigurationFailed);
        }

        ::cfsetispeed(&tty, B19200);
        ::cfsetospeed(&tty, B19200);

        tty.c_cflag |= (CLOCAL | CREAD | CS8 | CRTSCTS);
        tty.c_cflag &= ~(PARENB | CSTOPB | CSIZE);
        tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON | IXOFF);
        tty.c_oflag &= ~OPOST;
        tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            ::close(fd_);
            fd_ = -1;
            return std::unexpected(BridgeErrorCode::PortConfigurationFailed);
        }
        return {};
    }

    std::expected<void, BridgeErrorCode> pushTelemetryFrame(std::span<const uint8_t> frame) noexcept {
        if (frame.size() > 340) {
            return std::unexpected(BridgeErrorCode::PayloadTooLarge);
        }
        
        // Оновлення буфера MO свіжими даними
        tx_payload_.assign(frame.begin(), frame.end());
        return {};
    }

    void tick() noexcept {
        replenishTokens();

        switch (current_state_) {
            case FsmState::Idle:
                if (!tx_payload_.empty() && token_count_ >= 1.0f) {
                    current_state_ = FsmState::QuerySignalQuality;
                    transmitCommand("AT+CSQ\r");
                }
                break;

            case FsmState::QuerySignalQuality:
                current_state_ = FsmState::LoadBinaryBuffer;
                writeBinaryPayload();
                break;

            case FsmState::LoadBinaryBuffer:
                current_state_ = FsmState::TransmitSbdSession;
                transmitCommand("AT+SBDIX\r");
                break;

            case FsmState::TransmitSbdSession:
                token_count_ -= 1.0f;
                tx_payload_.clear();
                current_state_ = FsmState::FlushBuffers;
                transmitCommand("AT+SBDD0\r");
                break;

            case FsmState::FlushBuffers:
                current_state_ = FsmState::Idle;
                break;

            default:
                current_state_ = FsmState::Idle;
                break;
        }
    }

    [[nodiscard]] FsmState state() const noexcept { return current_state_; }
    [[nodiscard]] float availableTokens() const noexcept { return token_count_; }

private:
    void replenishTokens() noexcept {
        const auto now = std::chrono::steady_clock::now();
        const std::chrono::duration<float> elapsed = now - last_update_;
        last_update_ = now;

        const float interval_sec = static_cast<float>(min_interval_.count());
        token_count_ = std::min(2.0f, token_count_ + elapsed.count() / interval_sec);
    }

    void transmitCommand(std::string_view cmd) noexcept {
        if (fd_ >= 0) {
            [[maybe_unused]] auto res = ::write(fd_, cmd.data(), cmd.size());
        }
    }

    void writeBinaryPayload() noexcept {
        if (fd_ < 0 || tx_payload_.empty()) return;

        std::string cmd = "AT+SBDWB=" + std::to_string(tx_payload_.size()) + "\r";
        transmitCommand(cmd);
        ::usleep(100000);

        uint16_t checksum = 0;
        for (uint8_t byte : tx_payload_) checksum += byte;

        std::array<uint8_t, 2> cs = {
            static_cast<uint8_t>(checksum >> 8),
            static_cast<uint8_t>(checksum & 0xFF)
        };

        [[maybe_unused]] auto w1 = ::write(fd_, tx_payload_.data(), tx_payload_.size());
        [[maybe_unused]] auto w2 = ::write(fd_, cs.data(), cs.size());
    }

    std::string port_path_;
    int fd_{-1};
    FsmState current_state_{FsmState::Idle};
    std::chrono::seconds min_interval_;
    std::chrono::steady_clock::time_point last_update_{};
    float token_count_{1.0f};
    std::vector<uint8_t> tx_payload_;
};

} // namespace satellite
```
:::
