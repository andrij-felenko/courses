# ⚙️ Потоковий кінцевий автомат парсера NMEA 0183 на C та C++

Цей інженерний проєкт демонструє побудову високонадійного потокового парсера навігаційних речень NMEA 0183 на базі скінченного автомата (FSM) без динамічного виділення пам'яті (0 alloc), з побайтовим розрахунком контрольної суми XOR на льоту, безпечною токенізацією полів без руйнування порожніх значень, повним семантичним розбором речень GGA, RMC, GSA та VTG, фільтрацією геометричних факторів точності, синхронізацією часу з апаратним сигналом PPS та перетворенням координат у десяткові градуси.

### Архітектурні виклики та типові помилки парсингу

Прийом та обробка потоку NMEA 0183 у реальних вбудованих системах (польотних контролерах дронів на базі ArduPilot/PX4, автомобільних телематичних трекерах, морських автопілотах) пов'язані з низкою специфічних підводних каменів, які часто ігноруються в простих навчальних реалізаціях:

1. **Пастка функції `strtok()` у стандартній бібліотеці C**: стандартна функція `strtok()` розглядає кілька роздільників поспіль як один-єдиний роздільник. Якщо супутниковий приймач ще не обчислив диференційні поправки, поле віку DGPS та ID станції залишаються порожніми (дві або три коми поспіль `,,,`). Функція `strtok()` повністю знищує такі порожні поля, зміщуючи покажчики всіх наступних полів ліворуч. У результаті парсер зчитує контрольну суму замість висоти або інтерпретує значення HDOP як якість фіксу. Надійний парсер зобов'язаний розбирати поля за прямим індексуванням або власноруч замінювати коми нуль-термінаторами в пам'яті, створюючи масив покажчиків на кожен токен.
2. **Лінійне сміття та апаратні завади перехідних процесів**: під час увімкнення живлення приймача, перемикання швидкості UART або за наявності електромагнітних наведень у буфер потрапляють випадкові байти. Парсер повинен перебувати в стані суворого очікування стартового маркера `$` (або `!`) і безслідно відкидати всі байти до його появи.
3. **Раптовий обрив і миттєвий перезапуск кадру**: якщо передача попереднього речення обірвалася завадою і в лінію надійшов новий символ `$`, автомат зобов'язаний негайно скинути поточний буфер і почати збирання нового повідомлення з першого байта без зависань чи накопичення лічильників блокування.
4. **Захист від переповнення статичного буфера**: якщо термінатор `<CR><LF>` було спотворено або втрачено в каналі зв'язку, парсер не має права записувати символи за межі 84-байтового масиву. При досягненні граничного ліміту довжини 82 байти FSM зобов'язаний скинути стан у початковий та зафіксувати апаратну помилку кадру.
5. **Розрахунок контрольної суми без подвійного проходу по пам'яті**: обчислення проміжного результату XOR безпосередньо в момент отримання кожного байта в обробнику переривань (ISR) або функції `feed()` усуває необхідність повторного читання рядка з оперативної пам'яті після завершення кадру.
6. **Пастка втрати точності чисел із рухомою комою `float` проти `double`**: тип `float` стандарту IEEE 754 має 24-бітну мантису (приблизно 7.2 десяткових знаків точності). Для кутових координат широти `48.123456°` одиниця молодшого розряду становить `48.0 · 2⁻²³ ≈ 0.0000057°`, що на поверхні Землі відповідає дискретності близько **0.63 метра**. Якщо прошивка дрона зберігає широту й довготу в змінних типу `float`, вона принципово втрачає сантиметрову точність RTK-приймача ще до початку розрахунку навігаційного фільтра Калмана. Координати повинні зберігатися та перетворюватися виключно у типі `double` (64 біти, 53 біти мантиси, дискретність менше 0.01 міліметра) або у вигляді цілочисельних наноградусів `int32_t` / `int64_t` (множення на 10⁷).
7. **Похибка дільника тактової частоти UART (Baud Rate Error)**: при високих швидкостях (115200 бод) тактовий генератор мікроконтролера та генератор чипсета GNSS мають незначну розбіжність частоти. Якщо сумарна похибка швидкості передачі перевищує 2.5–3.0%, контролер UART починає фіксувати апаратні помилки кадрування `Framing Error`. Програмний стек зобов'язаний контролювати співвідношення прийнятих і пошкоджених пакетів.

---

### Математика перетворення координат і фізичних величин

У протоколі NMEA 0183 географічні координати передаються у комбінованому форматі «градуси та десяткові частки мінути»:
- Географічна широта: `ddmm.mmmm` (рівно 2 цифри цілих градусів `dd`, залишок — мінути дуги `mm.mmmm`).
- Географічна довгота: `dddmm.mmmm` (рівно 3 цифри цілих градусів `ddd`, залишок — мінути дуги `mm.mmmm`).

Оскільки одне коло містить 360 градусів, а один градус ділиться рівно на 60 кутових мінут (1' = 1/60°), формула перетворення в десяткові градуси (*Decimal Degrees*) має вигляд:

```
Градуси_Десяткові = Градуси_Цілі + (Мінути / 60.0)
```

Якщо індикатор півкулі широти дорівнює `'S'` (Південна півкуля) або індикатор довготи дорівнює `'W'` (Західна півкуля), результуюче значення десяткових градусів множиться на `-1.0`:

```
Десяткова_Широта  = (dd + mm.mmmm / 60.0) · (Півкуля == 'S' ? -1.0 : 1.0)
Десяткова_Довгота = (ddd + mm.mmmm / 60.0) · (Півкуля == 'W' ? -1.0 : 1.0)
```

**Числовий розрахунок на реальному векторі:**
Нехай із речення `$GNGGA` вилучено поля широти `4807.0382,N` та довготи `01131.0000,E`:
- Для широти: `Градуси = 48`, `Мінути = 07.0382`.
  `Широта = 48.0 + (7.0382 / 60.0) = 48.0 + 0.11730333 = +48.1173033°`.
- Для довготи: `Градуси = 011 = 11`, `Мінути = 31.0000`.
  `Довгота = 11.0 + (31.0000 / 60.0) = 11.0 + 0.51666667 = +11.5166667°`.

#### Перерахунок швидкості з морських вузлів у метри за секунду

У реченні RMC шляхова швидкість SOG передається в міжнародних морських вузлах (*knots*). Один морський вузол за міжнародним визначенням дорівнює точно 1 морській милі на годину, тобто 1852 метрам за 3600 секунд:

```
1 вузол = 1852 м / 3600 с = 1852 / 3600 ≈ 0.51444444 м/с
Швидкість_мс = Швидкість_вузли · 0.51444444
```

#### Розрахунок астрономічної мітки часу UNIX Epoch

Речення RMC передає час `hhmmss.sss` та дату `ddmmyy` (наприклад, `123519.00` та `230324`). Для синхронізації системного годинника контролера ці значення перераховуються в секунди епохи UNIX (кількість секунд від 1 січня 1970 року UTC):
1. Виділяються складові: `Години = 12`, `Хвилини = 35`, `Секунди = 19`, `День = 23`, `Місяць = 3`, `Рік = 2024` (до двозначного року додається базове століття 2000).
2. За алгоритмом високосних років обчислюється загальна кількість діб з 1970 року.
3. Додається час доби: `Секунди_Доби = Години · 3600 + Хвилини · 60 + Секунди`.

---

### Синхронізація часу та апаратний сигнал PPS

Послідовна передача речень NMEA 0183 по лінії UART вносить паразитну затримку транспортування (*Transport Jitter*). При швидкості 9600 бод передача блоку з 5 речень (близько 350 байтів) триває `350 · 10 / 9600 ≈ 364 мс`. Якщо автопілот орієнтується суто на момент завершення парсингу речення GGA, часова мітка запізнюється на третину секунди, що на швидкості польоту дрона 20 м/с створює просторову похибку понад 7 метрів.

Для усунення цієї затримки навігаційні модулі формують високоточний апаратний дискретний імпульс **PPS** (*Pulse Per Second*):
1. Апаратний імпульс PPS тривалістю 100 мс подається на окремий вхід переривання мікроконтролера строго на початку кожної фізичної секунди UTC (з точністю до ±20 наносекунд).
2. Обробник переривання фіксує точний таймстемп внутрішнього таймера процесора.
3. Коли через 50–200 мс послідовний порт UART завершує прийом речення `$GNRMC` або `$GNZDA`, парсер співвідносить розпарсену секунду UTC із зафіксованим перед цим фронтом PPS. Це забезпечує абсолютну субмікросекундну синхронізацію бортового комп'ютера.

---

### Стани та логіка переходів скінченного автомата (FSM)

Потоковий декодер функціонує як послідовний автомат Мілі-Мура з шістьма чітко розмежованими станами:

```
[WAIT_START] ──('$')──> [READ_PAYLOAD] ──('*')──> [READ_CS1] ──(Hex)──> [READ_CS2]
      ▲                       │                                            │
      │                  (Переповн.)                                   (CS збігся)
      │                       │                                            │
      │                       ▼                                            ▼
      └──(Помилка)────── [СКИДАННЯ] <──────(Помилка CS)──────────── [WAIT_CR]
      ▲                                                                    │
      │                                                                  ('\r')
      │                                                                    ▼
      └───────────────── [SENTENCE_READY] <─────────('\n')───────── [WAIT_LF]
```

1. `NMEA_STATE_WAIT_START`: автомат скинутий і очікує першого символу `$`. Будь-які інші символи ігноруються.
2. `NMEA_STATE_READ_PAYLOAD`: символи тіла речення копіюються в буфер, а побітовий акумулятор виконує операцію `calc_crc ^= byte`. При отриманні символу `*` рядок нуль-термінується і автомат переходить до читання контрольної суми.
3. `NMEA_STATE_READ_CS1`: зчитується старша шістнадцяткова цифра контрольної суми (символи `0`–`9`, `A`–`F`, `a`–`f`) і зсувається на 4 біти ліворуч: `rx_crc = hex << 4`.
4. `NMEA_STATE_READ_CS2`: зчитується молодша шістнадцяткова цифра: `rx_crc |= hex`. Автомат порівнює `rx_crc == calc_crc`. Якщо суми ідентичні, переходимо до перевірки термінатора.
5. `NMEA_STATE_WAIT_CR`: очікується символ повернення каретки `\r` (`0x0D`). Якщо рядок термінується лише символом `\n` (полегшений варіант деяких Unix-емуляторів), речення також визнається валідним.
6. `NMEA_STATE_WAIT_LF`: очікується завершальний символ переведення рядка `\n` (`0x0A`). Після його отримання виставляється прапорець готовності та викликається функція зворотного виклику (callback) або повертається `true`.

#### Робота з кільцевими буферами та перериваннями UART

В архітектурах реального часу контролер UART налаштовується на роботу з кільцевим буфером (*Ring Buffer*) або прямим доступом до пам'яті (DMA):
- **Схема обробки по перериванню (ISR)**: у мікроконтролері STM32 або ESP32 апаратне переривання UART RX приймає окремий байт і поміщає його в кільцевий буфер ємністю 256–512 байтів. Основний цикл обробки або задача RTOS вичитує байти з буфера та по черзі передає їх у метод `nmea_parser_feed()`.
- **Схема з циклічним DMA**: контролер DMA автоматично записує вхідний потік байтів у циклічний буфер пам'яті без участі процесора. Програма відстежує зміщення покажчика DMA і передає нові блоки даних у FSM-парсер, мінімізуючи навантаження на шину ядра.
- **Подвійна буферизація (Ping-Pong Buffering)**: контролер DMA налаштовується на два чергові буфери по 128 байтів. Коли перший буфер заповнюється, спрацьовує переривання напівпередачі `HTIF`, і процесор обробляє перший блок, поки DMA заповнює другий блок. Це повністю виключає втрату байтів при піковому навантаженні процесора.

---

### Покрокове трасування обробки вхідного потоку

Розглянемо реакцію автомата на типову послідовність байтів, що містить апаратний шум лінії, коректне речення та пошкоджений пакет:

| Крок | Вхідний байт | Поточний стан FSM | Дія автомата | Наступний стан | Значення `calc_crc` |
| :---: | :---: | :--- | :--- | :--- | :---: |
| 1 | `0xFF` | `WAIT_START` | Ігнорування завади | `WAIT_START` | `0x00` |
| 2 | `0x00` | `WAIT_START` | Ігнорування завади | `WAIT_START` | `0x00` |
| 3 | `$` | `WAIT_START` | Скидання буфера, старт | `READ_PAYLOAD` | `0x00` |
| 4 | `G` | `READ_PAYLOAD` | Запис у буфер, `0x00 ^ 'G'` | `READ_PAYLOAD` | `0x47` |
| 5 | `N` | `READ_PAYLOAD` | Запис у буфер, `0x47 ^ 'N'` | `READ_PAYLOAD` | `0x09` |
| ... | `...` | `READ_PAYLOAD` | Накопичення тіла | `READ_PAYLOAD` | `...` |
| 48 | `*` | `READ_PAYLOAD` | Завершення тіла | `READ_CS1` | `0x47` |
| 49 | `4` | `READ_CS1` | `rx_crc = 0x40` | `READ_CS2` | `0x47` |
| 50 | `7` | `READ_CS2` | `rx_crc = 0x47`, збіг! | `WAIT_CR` | `0x47` |
| 51 | `\r` | `WAIT_CR` | Очікування переведення рядка | `WAIT_LF` | `0x47` |
| 52 | `\n` | `WAIT_LF` | Кадр валідний, виклик колбека | `WAIT_START` | `0x00` |
| 53 | `$` | `WAIT_START` | Початок нового кадру | `READ_PAYLOAD` | `0x00` |
| 54 | `G` | `READ_PAYLOAD` | Накопичення тіла | `READ_PAYLOAD` | `0x47` |
| 55 | `$` | `READ_PAYLOAD` | **Колізія! Раптовий перезапуск** | `READ_PAYLOAD` | `0x00` |

---

### Семантичний розбір речень GSA та інтеграція з EKF

Речення `$GNGSA` транслює режим розв'язку (2D/3D), геометричні фактори точності (PDOP, HDOP, VDOP) та маску активних супутників. Розширений фільтр Калмана (EKF) навігаційного контролера використовує ці параметри для розрахунку коваріаційної матриці шуму вимірювань `R`:

```
$GNGSA,A,3,04,05,09,12,24,28,32,,,,,,1.8,1.0,1.5,1*1E
```

Дисперсія горизонтальної позиційної похибки оцінюється за формулою:

```
σ_горизонтальна = HDOP · σ_UERE
```

де `σ_UERE` (*User Equivalent Range Error*) — еквівалентна похибка вимірювання псевдовіддалі до супутника, яка становить близько 2.5 м для стандартного GPS SPS, 0.8 м для систем підсилення SBAS та 0.02 м для RTK Fixed.

Правила валідації сузір'я перед увімкненням автопілота:
1. **Режим розмірності (поле 2)**: має суворо дорівнювати `3` (повноцінний 3D-фікс). Значення `1` (немає фіксу) або `2` (2D-фікс без достовірної висоти) блокують запуск моторів.
2. **Поріг HDOP (поле 16)**: для безпечного утримання точки в режимі Loiter / PosHold горизонтальне зниження точності HDOP повинно бути менше `1.4`–`2.0`. Якщо HDOP перевищує `2.5`, дрон дрейфує через неточність супутникової тріангуляції.
3. **Число активних PRN**: кількість ненульових номерів супутників у полях 3–14 повинна становити щонайменше 6–8 супутників.

---

### Реалізація на мовах C та C++

У реалізації на мові C застосовано сувору парадигму нульового динамічного виділення пам'яті (відсутність `malloc`/`free`) зі статичною структурою парсера. Реалізація на C++ використовує ідіоматичний підхід: структури `std::string_view` та `std::span` для безалокаційного зрізу рядків, `std::optional` для безпечного повернення результатів та типізовані перерахування `enum class`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#define NMEA_MAX_SENTENCE_LEN 84
#define NMEA_MAX_FIELDS       24

typedef enum {
    NMEA_STATE_WAIT_START,
    NMEA_STATE_READ_PAYLOAD,
    NMEA_STATE_READ_CS1,
    NMEA_STATE_READ_CS2,
    NMEA_STATE_WAIT_CR,
    NMEA_STATE_WAIT_LF
} nmea_fsm_state_t;

typedef struct {
    nmea_fsm_state_t state;
    char buffer[NMEA_MAX_SENTENCE_LEN];
    uint8_t buf_idx;
    uint8_t calc_crc;
    uint8_t rx_crc;
    uint32_t sentences_ok;
    uint32_t sentences_err;
} nmea_parser_t;

typedef struct {
    double utc_time;      /* hhmmss.sss */
    double latitude;      /* Десяткові градуси (+N, -S) */
    double longitude;     /* Десяткові градуси (+E, -W) */
    uint8_t fix_quality;  /* 0=Invalid, 1=GPS, 2=DGPS, 4=RTK Fixed, 5=RTK Float */
    uint8_t satellites;   /* Кількість задіяних супутників */
    float hdop;           /* Горизонтальне зниження точності */
    float altitude;       /* Висота над геоїдом (MSL), метри */
    float geoid_sep;      /* Геоїдальне перевищення, метри */
} nmea_gga_data_t;

typedef struct {
    double utc_time;      /* hhmmss.sss */
    bool is_valid;        /* true якщо статус 'A', false якщо 'V' */
    double latitude;      /* Десяткові градуси */
    double longitude;     /* Десяткові градуси */
    float speed_knots;    /* Швидкість у вузлах */
    float speed_mps;      /* Швидкість у м/с */
    float course_deg;     /* Курс над ґрунтом COG у градусах */
    uint32_t date_dmyt;   /* Дата ddmmyy */
    char faa_mode;        /* Режим FAA: 'A', 'D', 'E', 'N' */
} nmea_rmc_data_t;

static inline int hex_digit_to_val(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

void nmea_parser_init(nmea_parser_t *p) {
    memset(p, 0, sizeof(nmea_parser_t));
    p->state = NMEA_STATE_WAIT_START;
}

/* Потокова обробка одного байта. Повертає true, якщо прийнято повне валідне речення */
bool nmea_parser_feed(nmea_parser_t *p, uint8_t byte, char *out_sentence) {
    if (byte == '$' || byte == '!') {
        p->state = NMEA_STATE_READ_PAYLOAD;
        p->buf_idx = 0;
        p->calc_crc = 0;
        return false;
    }

    switch (p->state) {
        case NMEA_STATE_WAIT_START:
            return false;

        case NMEA_STATE_READ_PAYLOAD:
            if (byte == '*') {
                p->buffer[p->buf_idx] = '\0';
                p->state = NMEA_STATE_READ_CS1;
            } else if (byte == '\r' || byte == '\n') {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_err++;
            } else {
                if (p->buf_idx < (NMEA_MAX_SENTENCE_LEN - 4)) {
                    p->buffer[p->buf_idx++] = (char)byte;
                    p->calc_crc ^= byte;
                } else {
                    p->state = NMEA_STATE_WAIT_START;
                    p->sentences_err++;
                }
            }
            return false;

        case NMEA_STATE_READ_CS1: {
            int val = hex_digit_to_val((char)byte);
            if (val >= 0) {
                p->rx_crc = (uint8_t)(val << 4);
                p->state = NMEA_STATE_READ_CS2;
            } else {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_err++;
            }
            return false;
        }

        case NMEA_STATE_READ_CS2: {
            int val = hex_digit_to_val((char)byte);
            if (val >= 0) {
                p->rx_crc |= (uint8_t)val;
                if (p->rx_crc == p->calc_crc) {
                    p->state = NMEA_STATE_WAIT_CR;
                } else {
                    p->state = NMEA_STATE_WAIT_START;
                    p->sentences_err++;
                }
            } else {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_err++;
            }
            return false;
        }

        case NMEA_STATE_WAIT_CR:
            if (byte == '\r') {
                p->state = NMEA_STATE_WAIT_LF;
            } else if (byte == '\n') {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_ok++;
                memcpy(out_sentence, p->buffer, p->buf_idx + 1);
                return true;
            } else {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_err++;
            }
            return false;

        case NMEA_STATE_WAIT_LF:
            p->state = NMEA_STATE_WAIT_START;
            if (byte == '\n') {
                p->sentences_ok++;
                memcpy(out_sentence, p->buffer, p->buf_idx + 1);
                return true;
            }
            p->sentences_err++;
            return false;
    }
    return false;
}

static uint8_t split_fields(char *str, char *fields[], uint8_t max_fields) {
    uint8_t count = 0;
    fields[count++] = str;

    while (*str && count < max_fields) {
        if (*str == ',') {
            *str = '\0';
            fields[count++] = str + 1;
        }
        str++;
    }
    return count;
}

static double parse_coord(const char *val_str, char hemisphere) {
    if (!val_str || !*val_str) return 0.0;
    double raw = atof(val_str);
    int degrees = (int)(raw / 100.0);
    double minutes = raw - (degrees * 100.0);
    double deg = degrees + (minutes / 60.0);
    if (hemisphere == 'S' || hemisphere == 'W') {
        deg = -deg;
    }
    return deg;
}

bool nmea_parse_gga(char *sentence, nmea_gga_data_t *out) {
    char *fields[NMEA_MAX_FIELDS];
    uint8_t num_fields = split_fields(sentence, fields, NMEA_MAX_FIELDS);

    if (num_fields < 10) return false;
    size_t len0 = strlen(fields[0]);
    if (len0 < 3 || strcmp(fields[0] + len0 - 3, "GGA") != 0) {
        return false;
    }

    memset(out, 0, sizeof(nmea_gga_data_t));
    if (*fields[1]) out->utc_time    = atof(fields[1]);
    if (*fields[2] && *fields[3]) out->latitude = parse_coord(fields[2], fields[3][0]);
    if (*fields[4] && *fields[5]) out->longitude = parse_coord(fields[4], fields[5][0]);
    if (*fields[6]) out->fix_quality = (uint8_t)atoi(fields[6]);
    if (*fields[7]) out->satellites  = (uint8_t)atoi(fields[7]);
    if (*fields[8]) out->hdop        = (float)atof(fields[8]);
    if (*fields[9]) out->altitude    = (float)atof(fields[9]);
    if (num_fields > 11 && *fields[11]) out->geoid_sep = (float)atof(fields[11]);

    return true;
}

bool nmea_parse_rmc(char *sentence, nmea_rmc_data_t *out) {
    char *fields[NMEA_MAX_FIELDS];
    uint8_t num_fields = split_fields(sentence, fields, NMEA_MAX_FIELDS);

    if (num_fields < 10) return false;
    size_t len0 = strlen(fields[0]);
    if (len0 < 3 || strcmp(fields[0] + len0 - 3, "RMC") != 0) {
        return false;
    }

    memset(out, 0, sizeof(nmea_rmc_data_t));
    if (*fields[1]) out->utc_time = atof(fields[1]);
    out->is_valid = (fields[2][0] == 'A');
    if (*fields[3] && *fields[4]) out->latitude = parse_coord(fields[3], fields[4][0]);
    if (*fields[5] && *fields[6]) out->longitude = parse_coord(fields[5], fields[6][0]);
    if (*fields[7]) {
        out->speed_knots = (float)atof(fields[7]);
        out->speed_mps = out->speed_knots * 0.51444444f;
    }
    if (*fields[8]) out->course_deg = (float)atof(fields[8]);
    if (*fields[9]) out->date_dmyt = (uint32_t)atoi(fields[9]);
    if (num_fields > 12 && *fields[12]) out->faa_mode = fields[12][0];

    return true;
}

int main(void) {
    nmea_parser_t parser;
    nmea_parser_init(&parser);

    const char stream[] = 
        "NOISE\x1B\x00$GNGGA,123519.00,4807.0382,N,01131.0000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"
        "$GNRMC,123519.00,A,4807.0382,N,01131.0000,E,022.4,084.4,230324,003.1,W,A*1D\r\n";

    char sentence[NMEA_MAX_SENTENCE_LEN];
    nmea_gga_data_t gga;
    nmea_rmc_data_t rmc;

    for (size_t i = 0; i < strlen(stream); i++) {
        if (nmea_parser_feed(&parser, (uint8_t)stream[i], sentence)) {
            printf("Прийнято речення: %s\n", sentence);
            char temp_buf[NMEA_MAX_SENTENCE_LEN];
            
            strcpy(temp_buf, sentence);
            if (nmea_parse_gga(temp_buf, &gga)) {
                printf("  [GGA] Широта: %.6f°, Довгота: %.6f°, Висота: %.1f м\n",
                       gga.latitude, gga.longitude, gga.altitude);
            }
            
            strcpy(temp_buf, sentence);
            if (nmea_parse_rmc(temp_buf, &rmc)) {
                printf("  [RMC] Швидкість: %.2f м/с (%.1f вузлів), Курс: %.1f°, Дата: %06u\n",
                       rmc.speed_mps, rmc.speed_knots, rmc.course_deg, rmc.date_dmyt);
            }
        }
    }

    printf("\nПідсумок FSM: Валідних = %u, Помилок = %u\n", 
           parser.sentences_ok, parser.sentences_err);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <optional>
#include <charconv>
#include <array>
#include <span>
#include <cstdint>
#include <iomanip>

struct NmeaGga {
    double utc_time{0.0};
    double latitude{0.0};
    double longitude{0.0};
    uint8_t fix_quality{0};
    uint8_t satellites{0};
    float hdop{99.9f};
    float altitude{0.0f};
    float geoid_sep{0.0f};
};

struct NmeaRmc {
    double utc_time{0.0};
    bool is_valid{false};
    double latitude{0.0};
    double longitude{0.0};
    float speed_knots{0.0f};
    float speed_mps{0.0f};
    float course_deg{0.0f};
    uint32_t date_dmyt{0};
    char faa_mode{'N'};
};

class NmeaParser {
public:
    enum class State {
        WaitStart,
        ReadPayload,
        ReadCs1,
        ReadCs2,
        WaitCr,
        WaitLf
    };

    std::optional<std::string_view> feed(uint8_t byte) noexcept {
        if (byte == '$' || byte == '!') {
            state_ = State::ReadPayload;
            buf_idx_ = 0;
            calc_crc_ = 0;
            return std::nullopt;
        }

        switch (state_) {
            case State::WaitStart:
                return std::nullopt;

            case State::ReadPayload:
                if (byte == '*') {
                    buffer_[buf_idx_] = '\0';
                    state_ = State::ReadCs1;
                } else if (byte == '\r' || byte == '\n') {
                    state_ = State::WaitStart;
                    errors_++;
                } else {
                    if (buf_idx_ < buffer_.size() - 1) {
                        buffer_[buf_idx_++] = static_cast<char>(byte);
                        calc_crc_ ^= byte;
                    } else {
                        state_ = State::WaitStart;
                        errors_++;
                    }
                }
                return std::nullopt;

            case State::ReadCs1: {
                int v = hexToVal(static_cast<char>(byte));
                if (v >= 0) {
                    rx_crc_ = static_cast<uint8_t>(v << 4);
                    state_ = State::ReadCs2;
                } else {
                    state_ = State::WaitStart;
                    errors_++;
                }
                return std::nullopt;
            }

            case State::ReadCs2: {
                int v = hexToVal(static_cast<char>(byte));
                if (v >= 0) {
                    rx_crc_ |= static_cast<uint8_t>(v);
                    if (rx_crc_ == calc_crc_) {
                        state_ = State::WaitCr;
                    } else {
                        state_ = State::WaitStart;
                        errors_++;
                    }
                } else {
                    state_ = State::WaitStart;
                    errors_++;
                }
                return std::nullopt;
            }

            case State::WaitCr:
                if (byte == '\r') {
                    state_ = State::WaitLf;
                } else if (byte == '\n') {
                    state_ = State::WaitStart;
                    success_++;
                    return std::string_view(buffer_.data(), buf_idx_);
                } else {
                    state_ = State::WaitStart;
                    errors_++;
                }
                return std::nullopt;

            case State::WaitLf:
                state_ = State::WaitStart;
                if (byte == '\n') {
                    success_++;
                    return std::string_view(buffer_.data(), buf_idx_);
                }
                errors_++;
                return std::nullopt;
        }
        return std::nullopt;
    }

    [[nodiscard]] uint32_t successCount() const noexcept { return success_; }
    [[nodiscard]] uint32_t errorCount() const noexcept { return errors_; }

    static std::optional<NmeaGga> parseGga(std::string_view line) noexcept {
        std::array<std::string_view, 20> fields{};
        size_t field_cnt = splitFields(line, fields);

        if (field_cnt < 10 || !fields[0].ends_with("GGA")) {
            return std::nullopt;
        }

        NmeaGga gga{};
        if (!fields[1].empty()) gga.utc_time = parseDouble(fields[1]);
        if (!fields[2].empty() && !fields[3].empty()) {
            gga.latitude = parseCoordinate(fields[2], fields[3][0]);
        }
        if (!fields[4].empty() && !fields[5].empty()) {
            gga.longitude = parseCoordinate(fields[4], fields[5][0]);
        }
        if (!fields[6].empty()) gga.fix_quality = static_cast<uint8_t>(parseInt(fields[6]));
        if (!fields[7].empty()) gga.satellites  = static_cast<uint8_t>(parseInt(fields[7]));
        if (!fields[8].empty()) gga.hdop        = static_cast<float>(parseDouble(fields[8]));
        if (!fields[9].empty()) gga.altitude    = static_cast<float>(parseDouble(fields[9]));
        if (field_cnt > 11 && !fields[11].empty()) {
            gga.geoid_sep = static_cast<float>(parseDouble(fields[11]));
        }

        return gga;
    }

    static std::optional<NmeaRmc> parseRmc(std::string_view line) noexcept {
        std::array<std::string_view, 20> fields{};
        size_t field_cnt = splitFields(line, fields);

        if (field_cnt < 10 || !fields[0].ends_with("RMC")) {
            return std::nullopt;
        }

        NmeaRmc rmc{};
        if (!fields[1].empty()) rmc.utc_time = parseDouble(fields[1]);
        rmc.is_valid = (!fields[2].empty() && fields[2][0] == 'A');
        if (!fields[3].empty() && !fields[4].empty()) {
            rmc.latitude = parseCoordinate(fields[3], fields[4][0]);
        }
        if (!fields[5].empty() && !fields[6].empty()) {
            rmc.longitude = parseCoordinate(fields[5], fields[6][0]);
        }
        if (!fields[7].empty()) {
            rmc.speed_knots = static_cast<float>(parseDouble(fields[7]));
            rmc.speed_mps = rmc.speed_knots * 0.51444444f;
        }
        if (!fields[8].empty()) rmc.course_deg = static_cast<float>(parseDouble(fields[8]));
        if (!fields[9].empty()) rmc.date_dmyt = static_cast<uint32_t>(parseInt(fields[9]));
        if (field_cnt > 12 && !fields[12].empty()) rmc.faa_mode = fields[12][0];

        return rmc;
    }

private:
    static size_t splitFields(std::string_view line, std::span<std::string_view> out) noexcept {
        size_t count = 0;
        size_t start = 0;
        for (size_t i = 0; i <= line.size() && count < out.size(); ++i) {
            if (i == line.size() || line[i] == ',') {
                out[count++] = line.substr(start, i - start);
                start = i + 1;
            }
        }
        return count;
    }

    static int hexToVal(char c) noexcept {
        if (c >= '0' && c <= '9') return c - '0';
        if (c >= 'A' && c <= 'F') return c - 'A' + 10;
        if (c >= 'a' && c <= 'f') return c - 'a' + 10;
        return -1;
    }

    static double parseDouble(std::string_view sv) noexcept {
        double val = 0.0;
        #if defined(__cpp_lib_to_chars) && __cpp_lib_to_chars >= 201611L
            std::from_chars(sv.data(), sv.data() + sv.size(), val);
        #else
            char tmp[32]{};
            size_t len = std::min(sv.size(), sizeof(tmp) - 1);
            sv.copy(tmp, len);
            val = std::strtod(tmp, nullptr);
        #endif
        return val;
    }

    static int parseInt(std::string_view sv) noexcept {
        int val = 0;
        std::from_chars(sv.data(), sv.data() + sv.size(), val);
        return val;
    }

    static double parseCoordinate(std::string_view sv, char hemisphere) noexcept {
        double raw = parseDouble(sv);
        int degrees = static_cast<int>(raw / 100.0);
        double minutes = raw - (degrees * 100.0);
        double deg = degrees + (minutes / 60.0);
        return (hemisphere == 'S' || hemisphere == 'W') ? -deg : deg;
    }

    State state_{State::WaitStart};
    std::array<char, 84> buffer_{};
    size_t buf_idx_{0};
    uint8_t calc_crc_{0};
    uint8_t rx_crc_{0};
    uint32_t success_{0};
    uint32_t errors_{0};
};

int main() {
    NmeaParser parser;
    std::string_view test_stream = 
        "NOISE\x1B\x00$GNGGA,123519.00,4807.0382,N,01131.0000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"
        "$GNRMC,123519.00,A,4807.0382,N,01131.0000,E,022.4,084.4,230324,003.1,W,A*1D\r\n";

    for (char ch : test_stream) {
        if (auto sentence = parser.feed(static_cast<uint8_t>(ch))) {
            std::cout << "Прийнято NMEA речення: " << *sentence << "\n";
            if (auto gga = NmeaParser::parseGga(*sentence)) {
                std::cout << std::fixed << std::setprecision(6);
                std::cout << "  [GGA] Широта: " << gga->latitude << "°, Довгота: " 
                          << gga->longitude << "°, Висота: " << gga->altitude << " м\n";
            }
            if (auto rmc = NmeaParser::parseRmc(*sentence)) {
                std::cout << "  [RMC] Швидкість: " << rmc->speed_mps << " м/с, Курс: " 
                          << rmc->course_deg << "°, Валідність: " << (rmc->is_valid ? "OK" : "NO") << "\n";
            }
        }
    }

    std::cout << "\nПідсумок C++: Успішно = " << parser.successCount()
              << ", Помилок = " << parser.errorCount() << "\n";
    return 0;
}
```
:::

---

### Збирання багатопакетних блоків речень GSV

Для речень параметрів сузір'я `$GPGSV` / `$GLGSV` / `$GAGSV` / `$GBGSV`, що розбиваються на декілька повідомлень, парсер реалізує проміжний масив накопичення. Кожне речення містить поля `Загальна_кількість` (поле 1) та `Номер_речення` (поле 2).

Алгоритм агрегації супутників:
1. При отриманні першого речення блоку (`Номер_речення == 1`) лічильник знайдених супутників обнуляється, а масив очищається.
2. Дані кожної четвірки (PRN, елевація, азимут, SNR) записуються в статичний масив розміром до 36 супутників.
3. Коли надходить останнє речення групи (`Номер_речення == Загальна_кількість`), сформований список супутників передається в навігаційний інтерфейс користувача або графічний віджет сузір'я.
4. Якщо між реченнями блоку надійшло речення іншого типу або минув таймаут 500 мс, неповний блок відкидається для запобігання змішуванню застарілих даних.

---

### Обробка крайових випадків та стійкість до збоїв

У процесі практичної експлуатації парсера виникають нештатні ситуації, які вимагають детермінованої обробки:

1. **Втрата синхронізації та вхідні завади**: випадкові байти перед початком речення ігноруються до моменту зустрічі маркера `$`.
2. **Спотворення контрольної суми**: якщо завада на лінії змінила хоча б один біт у тілі речення або в полі контрольної суми, FSM відкидає пошкоджений кадр та інкрементує лічильник помилок без передачі сміття навігаційному стеку.
3. **Пропущені необов'язкові поля**: алгоритм токенізації коректно виділяє порожні рядки `""` для полів `,,`, не зсуваючи порядок наступних параметрів.
4. **Переповнення максимального розміру**: кадри довжиною понад 82 байти (наприклад, через втрату термінатора `\r\n`) автоматично скидають автомат у стан очікування наступного стартового маркера.
5. **Проблема переповнення лічильника тижнів GPS (WNRO — Week Number Rollover)**: поле дати в реченні RMC передає рік двома цифрами `yy`. Для захисту від помилок датування програмне забезпечення має підтримувати ковзне вікно століття (наприклад, роки 80–99 відносяться до 1980–1999, а роки 00–79 — до 2000–2079).
6. **Динамічна зміна швидкості порту та збереження конфігурації**: при ініціалізації приймача польотний контролер зазвичай надсилає конфігураційне речення для перемикання порту з 9600 на 115200 бод (наприклад, `$PMTK251,115200*1F` для MTK або `$PUBX,41,1,0003,0003,115200,0*1E` для u-blox), після чого локальний контролер UART перемикає свій дільник частоти baud rate з паузою 50 мс для стабілізації лінії.

---

### Спільна робота з диференційними поправками RTCM

У сучасних геодезичних та аграрних RTK-системах супутниковий приймач використовує послідовний порт або для одночасної передачі речень NMEA та прийому бінарних поправок RTCM 10403.x, або розділяє їх між двома фізичними інтерфейсами UART.

Якщо поправки RTCM надходять у той самий фізичний потік, що й NMEA, бінарні пакети починаються з преамбули `0xD3 0x00` (байтовий маркер RTCM v3). Оскільки значення `0xD3` ніколи не збігається з символами `$` (`0x24`) або `!` (`0x21`), автомат FSM парсера NMEA перебуває в стані `WAIT_START` і безперешкодно ігнорує бінарні байти RTCM, не порушуючи роботу паралельного декодера диференційних поправок.

---

### Аналіз часової складності та обчислювального бюджету

Оцінімо обчислювальні витрати потокового парсера для типового 32-бітного мікроконтролера ARM Cortex-M4 з тактовою частотою 64 МГц:

1. **Час обробки одного байта в FSM**: кожен виклик функції `feed()` виконує порівняння станів, одну операцію `XOR`, інкремент покажчика буфера та перевірку межі. На асемблері це займає від 12 до 25 процесорних тактів (близько 0.2–0.4 мікросекунди).
2. **Пропускна здатність на швидкості 115200 бод**: при швидкості 115200 бод інтервал між надходженням байтів становить `10 / 115200 ≈ 86.8` мікросекунди. Отже, робота автомата FSM забирає менше ніж **0.5% сумарного процесорного часу ядра**, що дозволяє викликати `nmea_parser_feed()` безпосередньо всередині обробника переривання UART або в задачі FreeRTOS.
3. **Обробка повного повідомлення (семантичний парсинг)**: розбиття рядка на токени та перетворення чисел у формат `double` виконується лише один раз наприкінці речення (наприклад, 10–20 разів на секунду при частоті навігаційного оновлення 10 Гц). Загальний час розбору речення GGA становить менше 4.5 мікросекунд.
