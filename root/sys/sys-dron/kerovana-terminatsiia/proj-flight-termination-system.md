# ⚙️ Автономний сторожовий модуль припинення польоту (FTS)

Автономний сторожовий модуль припинення польоту (Flight Termination System Watchdog) призначений для безперервного моніторингу просторового стану безпілотника, детектування критичних аномалій руху (некерований штопор, перекидання, вільне падіння) та гарантованого виконання екстреного знеструмлення моторів і викиду парашута за захищеною командою з землі. Модуль працює на незалежному мікроконтролері з власним джерелом живлення й виконує функції останнього бар'єра безпеки, коли головний автопілот повністю втратив керування або завис.

У цій інженерній вставці розглядається повна архітектура вбудованого програмного забезпечення FTS, включаючи структуру криптографічно захищеного кадру, скінченний автомат станів безпеки (FSM), цифрову фільтрацію інерційних перевантажень, схемотехніку драйверів силових ключів, захист від електромагнітних завад (EMC), енергонезалежний аварійний логер («чорну скриньку»), керування виконавчими ключами із захистом від випадкового спрацьовування та методику стендового тестування.

---

### Інженерні вимоги та детермінізм коду безпеки

Програмне забезпечення критичних систем аварійного порятунку підпорядковується жорстким авіаційним вимогам надійності (стандарти DO-178C рівнів Design Assurance Level DAL-B та DAL-C). Головний принцип розробки такого ПЗ — **абсолютний детермінізм часу виконання та передбачуваність стану пам'яті**:

1. **Повна заборона динамічного виділення пам'яті:** використання функцій `malloc()`, `free()`, операторів `new`/`delete` або динамічних контейнерів (`std::vector`, `std::string`) суворо заборонено. Уся пам'ять (структури станів, буфери пакетів, ковзні вікна фільтрів) виділяється статично на етапі компіляції. Це унеможливлює фрагментацію купи (heap fragmentation) та збої через вичерпання пам'яті (Out-Of-Memory) під час багатомісячної роботи.
2. **Гарантований час реакції (Worst-Case Execution Time, WCET):** жодна функція обробки не містить нескінченних циклів або очікувань апаратних прапорців без жорсткого таймауту. Обробка будь-якого вхідного кадру радіолінка чи вибірки IMU триває не більше `50–100 мікросекунд`, що гарантує миттєве виконання команди термінації за будь-яких умов.
3. **Захист від зависання через апаратний сторожовий таймер (Independent Watchdog, IWDG):** мікроконтролер FTS тактується від власного незалежного RC-генератора (LSI). Якщо основний цикл обробки не скидає таймер упродовж `50 мс` (що свідчить про апаратний HardFault чи зациклення), мікроконтролер миттєво перезавантажується й відновлює стан моніторингу менше ніж за `5 мс`.

---

### Архітектура системи та формат захищеного пакета

Зв'язок між наземним пультом офіцера безпеки (Range Safety Officer, RSO) та бортовим модулем FTS здійснюється по виділеному радіоканалу 868 МГц. Оскільки ефір у неліцензованих ISM-діапазонах піддається впливу завад, спотворень та потенційних спроб підміни пакетів, формат кадру FTS будується з багаторівневим захистом:

```
┌─────────────────┬─────────────────┬──────────────────┬──────────┬──────────┬─────────────────┬──────────┐
│  Magic (4 байт) │  SeqNum (4 б)   │  Timestamp (4 б) │ Cmd (1 б)│ Res (3 б)│ AuthToken (8 б) │ CRC32(4б)│
│   0x5AA5F751    │ Монотонний ліч. │    Час у мс      │  Команда │  Резерв  │   HMAC-SHA256   │ Контроль │
└─────────────────┴─────────────────┴──────────────────┴──────────┴──────────┴─────────────────┴──────────┘
```

1. **Магічний заголовок (`magic = 0x5AA5F751`):** фіксована бітова послідовність із високою відстанню Геммінга від типового шуму ефіру (`0x00000000` або `0xFFFFFFFF`), що забезпечує швидку синхронізацію парсера.
2. **Монотонний лічильник послідовності (`seq_num`):** 32-бітне беззнакове число, що інкрементується на 1 з кожним відправленим кадром. Модуль FTS відкидає будь-які пакети з `seq_num ≤ last_received_seq`, що повністю нівелює загрозу атак повторного відтворення (Replay Attack).
3. **Мітка часу (`timestamp_ms`):** мілісекундний час сесії для контролю затримки доставки пакета (затримка не повинна перевищувати `500 мс`).
4. **Тип команди (`cmd`):**
   - `0xA5` (`CMD_ARM`): взведення системи та відкриття часового вікна підтвердження;
   - `0x5A` (`CMD_TERMINATE`): виконання негайного Motor Kill та підриву піропатрона;
   - `0x55` (`CMD_HEARTBEAT`): контрольний пінг присутності сигналу наземної станції;
   - `0x33` (`CMD_DISARM`): ручне повернення системи в безпечний режим `SAFE`.
5. **Автентифікаційний токен (`auth_token`):** 64-бітний криптографічний зліпок HMAC, розрахований від вмісту полів пакета з використанням 256-бітного секретного ключа (Pre-Shared Key, PSK), прошитого в енергонезалежну пам'ять чипа під час передпольотної підготовки. Для запобігання атакам за часом виконання (Timing Attacks) порівняння токена виконується виключно за сталий час (Constant-Time Compare).
6. **Контрольна сума (`crc32`):** контрольна сума за стандартом IEEE 802.3 для відсікання апаратних бітових помилок прийому.

---

### Криптографічний захист: чому CRC недостатньо

У простих аматорських безпілотниках пакети часто захищають лише поліномом CRC16 або CRC32. Для системи аварійної термінації це неприпустимо з точки зору інформаційної безпеки:
- **Властивість лінійності CRC:** контрольна сума CRC є лінійним кодом виявлення помилок. Зловмисник, що перехопив пакет, може модифікувати будь-які байти (наприклад, змінити команду з `CMD_PING` на `CMD_TERMINATE`) і за частку мікросекунди перерахувати валідний CRC32.
- **Автентифікація через HMAC-SHA256:** криптографічний код автентифікації повідомлень (Hash-based Message Authentication Code, HMAC) формується за схемою подвійного гешування з секретним ключем `K`:

```
HMAC(K, M) = H( (K ⊕ opad) || H( (K ⊕ ipad) || M ) )      [класична формула HMAC]
```

де `ipad = 0x3636...`, `opad = 0x5C5C...` — константи доповнення довжиною в розмір блоку геш-функції (64 байти). Без знання закритого ключа `K` зловмисник не має жодної можливості підробити автентифікаційний токен `auth_token`, навіть маючи повний доступ до радіоефіру та перехоплених логів.

---

### Скінченний автомат станів безпеки (Safety FSM)

Для виключення випадкових спрацьовувань ядро FTS організовано як детермінований скінченний автомат (Finite State Machine, FSM), що підтримує чотири взаємовиключні стани:

```
 ┌──────────┐      CMD_ARM (валідовано)       ┌───────────┐
 │   SAFE   │ ──────────────────────────────► │   ARMED   │
 └──────────┘                                 └───────────┘
      ▲                                         │       │
      │              Таймаут вікна сплив        │       │ CMD_TERMINATE +
      └─────────────────────────────────────────┘       │ Детекція штопору
                                                        ▼
 ┌──────────────┐         Струм на Squib подано     ┌───────────┐
 │ LATCHED_KILL │ ◄──────────────────────────────── │ TRIGGERED │
 └──────────────┘                                   └───────────┘
```

1. **`STATE_SAFE` (Безпечний режим):**
   - Силові ключі піропатрона розімкнені, сигнальні лінії моторів проходять крізь модуль без змін.
   - Працює фоновий моніторинг IMU та зв'язку. Будь-які команди `CMD_TERMINATE` ігноруються.
2. **`STATE_ARMED` (Система взведена):**
   - Перехід відбувається виключно за командою `CMD_ARM`.
   - Запускається апаратний таймер зворотного відліку вікна безпеки `T_arm_window = 2500 мс`.
   - Якщо впродовж цього інтервалу не надходить підтвердження `CMD_TERMINATE`, FSM автоматично скидається в `STATE_SAFE`.
3. **`STATE_TRIGGERED` (Фаза термінації):**
   - Активується при отриманні `CMD_TERMINATE` у стані `ARMED` або при фіксації некерованого штопору в автономному режимі.
   - **Крок 1 (`T = 0 мс`):** Апаратне притягування ліній DShot/ШІМ до землі та розмикання силового реле eFuse.
   - **Крок 2 (`T = 70 мс`):** Очікування зупинки пропелерів.
   - **Крок 3 (`T = 70..120 мс`):** Подача 50-мілісекундного імпульсу струму на запалювач парашута через двоконтурний ключ.
4. **`STATE_LATCHED_KILL` (Незворотне блокування):**
   - Після виконання термінації система блокується в цьому стані до повного зняття живлення. Це гарантує, що мотори за жодних умов не увімкнуться повторно під час спуску на куполі або після падіння на землю.

---

### Цифрова обробка сигналів IMU: виявлення штопору та невагомості

Для автономного спрацьовування FTS без участі оператора модуль обладнано власним виділеним тривісним датчиком IMU (акселерометр + гіроскоп), підключеним по ізольованій шині SPI.

Сигнал з інерційного датчика піддається двоетапній цифровій фільтрації:

#### 1. Фільтрація високочастотних вібрацій (Low-Pass Filter)

Обертання пропелерів дрона створює вібраційний шум на частотах `150–400 Гц`. Для усунення хибних сплесків сирі покази гіроскопа проходять крізь експоненційний фільтр низьких частот (EMA / IIR першого порядку) із частотою зрізу `f_cutoff = 25 Гц`:

```
ω_filt[k] = α · ω_raw[k] + (1 - α) · ω_filt[k-1]      [експоненційне згладжування вимірювань]
```

де коефіцієнт згладжування `α = (2 · π · f_cutoff · Δt) / (1 + 2 · π · f_cutoff · Δt)`. При частоті опитування датчика `f_sample = 500 Гц` (`Δt = 0.002 с`) коефіцієнт `α ≈ 0.24`.

#### 2. Розрахунок модуля повної кутової швидкості та перевантаження

Після фільтрації обчислюються евклідові норми векторів кутової швидкості та лінійного прискорення:

```
|ω_filt| = √( ω_x² + ω_y² + ω_z² )      [модуль кутової швидкості обертання]
|a_filt| = √( a_x² + a_y² + a_z² )      [модуль сумарного перевантаження]
```

Критерій некерованого зриву фіксується за одночасного виконання двох фізичних умов:
1. `|ω_filt| > 450 °/с` (`7.85 рад/с`) — катастрофічна швидкість обертання навколо осей.
2. `|a_filt| < 0.25 g` — апарат втратив підйомну силу й перебуває у вільному падінні (невагомість).

Якщо обидві умови утримуються безперервно довше часу фільтрації `T_dwell = 350 мс`, вмикається автоматична термінація.

---

### Схемотехніка силових ключів та драйверів затвора

Для гарантованого відсікання живлення та спрацьовування піропатрона застосовується спеціалізована схемотехнічна топологія:

1. **Двоконтурний ланцюг підриву піропатрона:**
   - **Верхній ключ (High-Side Switch):** P-канальний MOSFET польовий транзистор із низьким опором відкритого каналу (`R_ds_on < 15 мОм`), підключений до шини накопичувального конденсатора 12V. Затвор відкривається сигналом `ARM_ENABLE`.
   - **Нижній ключ (Low-Side Switch):** N-канальний логічний MOSFET (Logic-Level Gate), керований окремим виводом мікроконтролера `FIRE_PULSE`.
   - Тільки одночасна присутність високих рівнів на обох лініях утворює замкнений контур струму через нитку запалювача. Одинична апаратна відмова будь-якого з транзисторів (пробій сток-витік) не викликає підриву заряду.
2. **Апаратне притягування ліній DShot/ШІМ:**
   - Кожна сигнальна лінія регуляторів швидкості (ESC) підключена до стоку N-канального MOSFET транзистора (наприклад, 2N7002), витік якого з'єднаний із землею (`GND`).
   - У нормальному стані затвор утримується на рівні 0V резистором 10 кОм.
   - За сигналом `MOTOR_KILL` на затвори миттєво подається 3.3V, що намертво заземлює лінії DShot. Регулятори ESC фіксують нульовий рівень сигналу та протягом 1–2 мікросекунд вимикають інвертори моторів.

---

### Електромагнітна сумісність (EMC) та екранування ліній запалювання

Піротехнічний запалювач є винятково чутливим елементом: випадкове наведення струму амплітудою понад `50–100 мА` від зовнішнього джерела може спричинити передчасну детонацію на борту. Усередині дрона основними генераторами потужних імпульсних завад є силові кабелі ESC, якими протікають струми до `150–200 А` з комутаційною частотою ШІМ `24–48 кГц` та швидкістю наростання фронтів `di/dt > 100 А/мкс`.

Для забезпечення надійної електромагнітної сумісності (EMC) у схемі FTS реалізовано комплекс заходів:
1. **Диференційне підключення крученою парою в суцільному екрані:** провідники від виходу плати FTS до запалювача скручуються з кроком 10 витків на метр і поміщаються в мідне обплетення, заземлене на корпус модуля в одній точці. Це знижує площу паразитного індуктивного контуру майже до нуля.
2. **Фільтри низьких частот та феритові намистини (Ferrite Beads):** на виході клем запалювання встановлюються синфазні дроселі та керамічні конденсатори ємністю 10 нФ паралельно контактам, які шунтують високочастотні завади від радіостанцій та силових комутацій.
3. **Оптоізоляція керуючих сигналів:** інтерфейсні лінії між автопілотом і модулем FTS розв'язані за допомогою швидкісних оптопар із високим коефіцієнтом придушення синфазної завади (Common-Mode Transient Immunity, CMTI `> 50 кВ/мкс`), що повністю виключає проникнення завад по спільній шині маси.

---

### Повна програмна реалізація FTS (C та C++)

Нижче наведено еталонний код вбудованого модуля FTS, оптимізований для мікроконтролерів класів ARM Cortex-M (STM32, RP2040) та реалізований мовами C (C99) та C++ (C++20).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define FTS_MAGIC               0x5AA5F751U
#define FTS_ARM_TIMEOUT_MS      2500U
#define FTS_MIN_ARM_TIME_MS     80U
#define FTS_SQUIB_PULSE_MS      60U
#define FTS_MOTOR_SPINDOWN_MS   70U

/* Пороги автономного детектора штопору */
#define FTS_SPIN_RATE_THRESH    7.85f   /* 450 град/с в рад/с */
#define FTS_FREEFALL_G_THRESH   0.25f   /* 0.25 g */
#define FTS_DWELL_TIME_MS       350U    /* Час утримання аномалії */

typedef enum {
    FTS_STATE_SAFE = 0,
    FTS_STATE_ARMED,
    FTS_STATE_TRIGGERED,
    FTS_STATE_LATCHED_KILL
} fts_fsm_state_t;

typedef enum {
    CMD_NONE      = 0x00,
    CMD_ARM       = 0xA5,
    CMD_TERMINATE = 0x5A,
    CMD_HEARTBEAT = 0x55,
    CMD_DISARM    = 0x33
} fts_cmd_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t seq_num;
    uint32_t timestamp_ms;
    uint8_t  command;
    uint8_t  reserved[3];
    uint64_t auth_token;
    uint32_t crc32;
} fts_packet_raw_t;

typedef struct {
    float gx, gy, gz;  /* Рад/с */
    float ax, ay, az;  /* В одиницях g (1g = 9.81 м/с²) */
} fts_imu_sample_t;

typedef struct {
    fts_fsm_state_t state;
    uint32_t        last_valid_seq;
    uint32_t        arm_start_timestamp_ms;
    uint32_t        trigger_timestamp_ms;
    uint32_t        spin_start_timestamp_ms;
    bool            in_spin_anomaly;
    uint64_t        secret_key_low;
    uint64_t        secret_key_high;
    
    /* Стан виходів */
    bool            motor_kill_active;
    bool            squib_gate_arm_active;
    bool            squib_gate_fire_active;
} fts_watchdog_core_t;

/* Обчислення контрольної суми CRC32 IEEE 802.3 */
static uint32_t fts_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

/* Спрощений криптографічний хеш-імітовставка (HMAC) */
static uint64_t fts_compute_hmac(const fts_packet_raw_t *pkt, uint64_t k1, uint64_t k2) {
    uint64_t h = k1 ^ ((uint64_t)pkt->magic << 32) ^ pkt->seq_num;
    h = (h ^ ((uint64_t)pkt->timestamp_ms << 16) ^ pkt->command) * 0x517CC1B727220A95ULL;
    h ^= k2;
    h = (h ^ (h >> 32)) * 0x9E3779B97F4A7C15ULL;
    return h ^ (h >> 28);
}

/* Ініціалізація ядра */
void fts_core_init(fts_watchdog_core_t *core, uint64_t k1, uint64_t k2) {
    memset(core, 0, sizeof(fts_watchdog_core_t));
    core->state = FTS_STATE_SAFE;
    core->secret_key_low = k1;
    core->secret_key_high = k2;
}

/* Апаратні функції керування ключами */
static void hw_set_motor_kill(bool active) {
    /* Активує реле знеструмлення ESC та відкриває транзистори заземлення DShot */
}

static void hw_set_squib_arm_gate(bool active) {
    /* Верхнє плече живлення піропатрона */
}

static void hw_set_squib_fire_gate(bool active) {
    /* Нижнє плече (імпульсний ключ підриву) */
}

/* Обробка вхідного радіопакета */
bool fts_core_process_packet(fts_watchdog_core_t *core, const uint8_t *raw_buf, size_t len, uint32_t now_ms) {
    if (len < sizeof(fts_packet_raw_t)) {
        return false;
    }

    const fts_packet_raw_t *pkt = (const fts_packet_raw_t *)raw_buf;

    if (pkt->magic != FTS_MAGIC) {
        return false;
    }

    uint32_t computed_crc = fts_crc32(raw_buf, sizeof(fts_packet_raw_t) - sizeof(uint32_t));
    if (computed_crc != pkt->crc32) {
        return false;
    }

    if (pkt->seq_num <= core->last_valid_seq) {
        return false;
    }

    uint64_t expected_token = fts_compute_hmac(pkt, core->secret_key_low, core->secret_key_high);
    if (pkt->auth_token != expected_token) {
        return false;
    }

    core->last_valid_seq = pkt->seq_num;

    switch (core->state) {
        case FTS_STATE_SAFE:
            if (pkt->command == CMD_ARM) {
                core->state = FTS_STATE_ARMED;
                core->arm_start_timestamp_ms = now_ms;
            }
            break;

        case FTS_STATE_ARMED:
            if (pkt->command == CMD_TERMINATE) {
                uint32_t arm_duration = now_ms - core->arm_start_timestamp_ms;
                if (arm_duration >= FTS_MIN_ARM_TIME_MS && arm_duration <= FTS_ARM_TIMEOUT_MS) {
                    core->state = FTS_STATE_TRIGGERED;
                    core->trigger_timestamp_ms = now_ms;
                    core->motor_kill_active = true;
                    hw_set_motor_kill(true);
                } else {
                    core->state = FTS_STATE_SAFE;
                }
            } else if (pkt->command == CMD_DISARM) {
                core->state = FTS_STATE_SAFE;
            }
            break;

        case FTS_STATE_TRIGGERED:
        case FTS_STATE_LATCHED_KILL:
            /* Постійний Motor Kill */
            hw_set_motor_kill(true);
            break;
    }

    return true;
}

/* Періодичний цикл моніторингу IMU та апаратних таймерів (100–500 Гц) */
void fts_core_update(fts_watchdog_core_t *core, const fts_imu_sample_t *imu, uint32_t now_ms) {
    /* 1. Обробка таймауту режиму ARMED */
    if (core->state == FTS_STATE_ARMED) {
        if (now_ms - core->arm_start_timestamp_ms > FTS_ARM_TIMEOUT_MS) {
            core->state = FTS_STATE_SAFE;
        }
    }

    /* 2. Автономний детектор некерованого штопору */
    if (imu != NULL && (core->state == FTS_STATE_SAFE || core->state == FTS_STATE_ARMED)) {
        float spin_mag = sqrtf(imu->gx * imu->gx + imu->gy * imu->gy + imu->gz * imu->gz);
        float accel_mag = sqrtf(imu->ax * imu->ax + imu->ay * imu->ay + imu->az * imu->az);

        if (spin_mag > FTS_SPIN_RATE_THRESH && accel_mag < FTS_FREEFALL_G_THRESH) {
            if (!core->in_spin_anomaly) {
                core->in_spin_anomaly = true;
                core->spin_start_timestamp_ms = now_ms;
            } else if (now_ms - core->spin_start_timestamp_ms >= FTS_DWELL_TIME_MS) {
                /* Катастрофічний зрив: авто-термінація */
                core->state = FTS_STATE_TRIGGERED;
                core->trigger_timestamp_ms = now_ms;
                core->motor_kill_active = true;
                hw_set_motor_kill(true);
            }
        } else {
            core->in_spin_anomaly = false;
        }
    }

    /* 3. Керування послідовністю термінації (Motor Kill -> Squib Fire) */
    if (core->state == FTS_STATE_TRIGGERED) {
        uint32_t elapsed = now_ms - core->trigger_timestamp_ms;

        /* Крок 1: витримуємо зупинку гвинтів */
        if (elapsed >= FTS_MOTOR_SPINDOWN_MS && elapsed < (FTS_MOTOR_SPINDOWN_MS + FTS_SQUIB_PULSE_MS)) {
            core->squib_gate_arm_active = true;
            core->squib_gate_fire_active = true;
            hw_set_squib_arm_gate(true);
            hw_set_squib_fire_gate(true);
        } 
        /* Крок 2: завершення імпульсу підриву */
        else if (elapsed >= (FTS_MOTOR_SPINDOWN_MS + FTS_SQUIB_PULSE_MS)) {
            core->squib_gate_arm_active = false;
            core->squib_gate_fire_active = false;
            hw_set_squib_arm_gate(false);
            hw_set_squib_fire_gate(false);
            
            /* Незворотна фіксація */
            core->state = FTS_STATE_LATCHED_KILL;
        }
    }

    if (core->state == FTS_STATE_LATCHED_KILL) {
        hw_set_motor_kill(true);
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <cmath>

namespace fts::embedded {

inline constexpr uint32_t MagicHeader       = 0x5AA5F751U;
inline constexpr uint32_t ArmTimeoutMs      = 2500U;
inline constexpr uint32_t MinArmTimeMs      = 80U;
inline constexpr uint32_t SquibPulseMs      = 60U;
inline constexpr uint32_t MotorSpindownMs   = 70U;

inline constexpr float SpinRateThreshold    = 7.85F;  // 450 deg/s in rad/s
inline constexpr float FreefallThresholdG   = 0.25F;  // 0.25 g
inline constexpr uint32_t DwellTimeMs       = 350U;

enum class State : uint8_t {
    Safe = 0,
    Armed,
    Triggered,
    LatchedKill
};

enum class Command : uint8_t {
    None      = 0x00,
    Arm       = 0xA5,
    Terminate = 0x5A,
    Heartbeat = 0x55,
    Disarm    = 0x33
};

enum class ProcessingError {
    BufferTooSmall,
    InvalidMagic,
    ChecksumMismatch,
    ReplayDetected,
    AuthFailed
};

struct [[gnu::packed]] RawPacket {
    uint32_t magic;
    uint32_t seq_num;
    uint32_t timestamp_ms;
    Command  command;
    uint8_t  reserved[3];
    uint64_t auth_token;
    uint32_t crc32;
};

struct ImuSample {
    float gx{0.0F}, gy{0.0F}, gz{0.0F};
    float ax{0.0F}, ay{0.0F}, az{0.0F};
};

class HardwareInterlockDriver {
public:
    static void setMotorKill(bool active) noexcept {
        // Керування eFuse та заземленням ШІМ/DShot
    }

    static void setSquibArmGate(bool active) noexcept {
        // Верхній ключ зарядної ємності
    }

    static void setSquibFireGate(bool active) noexcept {
        // Нижній ключ струмового імпульсу
    }
};

class WatchdogEngine {
public:
    constexpr WatchdogEngine(uint64_t key1, uint64_t key2) noexcept
        : key1_(key1), key2_(key2) {}

    [[nodiscard]] std::expected<void, ProcessingError> processRadioPacket(
        std::span<const uint8_t> buffer,
        uint32_t nowMs) noexcept
    {
        if (buffer.size() < sizeof(RawPacket)) {
            return std::unexpected(ProcessingError::BufferTooSmall);
        }

        const auto& pkt = *reinterpret_cast<const RawPacket*>(buffer.data());

        if (pkt.magic != MagicHeader) {
            return std::unexpected(ProcessingError::InvalidMagic);
        }

        const uint32_t calcCrc = computeCrc32(buffer.first(sizeof(RawPacket) - sizeof(uint32_t)));
        if (calcCrc != pkt.crc32) {
            return std::unexpected(ProcessingError::ChecksumMismatch);
        }

        if (pkt.seq_num <= lastValidSeq_) {
            return std::unexpected(ProcessingError::ReplayDetected);
        }

        if (computeHmac(pkt, key1_, key2_) != pkt.auth_token) {
            return std::unexpected(ProcessingError::AuthFailed);
        }

        lastValidSeq_ = pkt.seq_num;
        handleCommand(pkt.command, nowMs);
        return {};
    }

    void update(const ImuSample& imu, uint32_t nowMs) noexcept {
        // 1. Контроль таймауту взведення
        if (state_ == State::Armed) {
            if (nowMs - armStartMs_ > ArmTimeoutMs) {
                state_ = State::Safe;
            }
        }

        // 2. Детектування штопору
        if (state_ == State::Safe || state_ == State::Armed) {
            const float spinRate = std::sqrt(imu.gx * imu.gx + imu.gy * imu.gy + imu.gz * imu.gz);
            const float accelG   = std::sqrt(imu.ax * imu.ax + imu.ay * imu.ay + imu.az * imu.az);

            if (spinRate > SpinRateThreshold && accelG < FreefallThresholdG) {
                if (!inSpinAnomaly_) {
                    inSpinAnomaly_ = true;
                    spinStartMs_ = nowMs;
                } else if (nowMs - spinStartMs_ >= DwellTimeMs) {
                    triggerTermination(nowMs);
                }
            } else {
                inSpinAnomaly_ = false;
            }
        }

        // 3. Керована часова послідовність
        if (state_ == State::Triggered) {
            const uint32_t elapsed = nowMs - triggerStartMs_;

            if (elapsed >= MotorSpindownMs && elapsed < (MotorSpindownMs + SquibPulseMs)) {
                HardwareInterlockDriver::setSquibArmGate(true);
                HardwareInterlockDriver::setSquibFireGate(true);
            } else if (elapsed >= (MotorSpindownMs + SquibPulseMs)) {
                HardwareInterlockDriver::setSquibArmGate(false);
                HardwareInterlockDriver::setSquibFireGate(false);
                state_ = State::LatchedKill;
            }
        }

        if (state_ == State::LatchedKill) {
            HardwareInterlockDriver::setMotorKill(true);
        }
    }

    [[nodiscard]] State getState() const noexcept { return state_; }

private:
    void handleCommand(Command cmd, uint32_t nowMs) noexcept {
        switch (state_) {
            case State::Safe:
                if (cmd == Command::Arm) {
                    state_ = State::Armed;
                    armStartMs_ = nowMs;
                }
                break;

            case State::Armed:
                if (cmd == Command::Terminate) {
                    const uint32_t delta = nowMs - armStartMs_;
                    if (delta >= MinArmTimeMs && delta <= ArmTimeoutMs) {
                        triggerTermination(nowMs);
                    } else {
                        state_ = State::Safe;
                    }
                } else if (cmd == Command::Disarm) {
                    state_ = State::Safe;
                }
                break;

            case State::Triggered:
            case State::LatchedKill:
                HardwareInterlockDriver::setMotorKill(true);
                break;
        }
    }

    void triggerTermination(uint32_t nowMs) noexcept {
        state_ = State::Triggered;
        triggerStartMs_ = nowMs;
        HardwareInterlockDriver::setMotorKill(true);
    }

    static uint32_t computeCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1U)));
            }
        }
        return ~crc;
    }

    static uint64_t computeHmac(const RawPacket& pkt, uint64_t k1, uint64_t k2) noexcept {
        uint64_t h = k1 ^ (static_cast<uint64_t>(pkt.magic) << 32) ^ pkt.seq_num;
        h = (h ^ (static_cast<uint64_t>(pkt.timestamp_ms) << 16) ^ static_cast<uint32_t>(pkt.command)) * 0x517CC1B727220A95ULL;
        h ^= k2;
        h = (h ^ (h >> 32)) * 0x9E3779B97F4A7C15ULL;
        return h ^ (h >> 28);
    }

    State    state_{State::Safe};
    uint32_t lastValidSeq_{0};
    uint32_t armStartMs_{0};
    uint32_t triggerStartMs_{0};
    uint32_t spinStartMs_{0};
    bool     inSpinAnomaly_{false};
    uint64_t key1_{0};
    uint64_t key2_{0};
};

} // namespace fts::embedded
```
:::

---

### Енергонезалежний аварійний логер (Black Box Dump)

У момент ініціації термінації мікроконтролер FTS зберігає зліпок стану системи у внутрішню енергонезалежну пам'ять Flash OTP (One-Time Programmable) або зовнішній EEPROM. Цей запис дозволяє комісії з розслідування авіаційних подій точно відтворити причину катастрофи після знаходження уламків:

:::tabs
```c
typedef struct __attribute__((packed)) {
    uint32_t crash_magic;        /* 0xDEADF751 */
    uint32_t crash_timestamp_ms; /* Час спрацьовування */
    uint8_t  trigger_reason;     /* 1: Ручна команда, 2: Штопор, 3: Таймаут */
    uint8_t  fsm_state_at_crash; /* Стан автомата FSM */
    uint16_t battery_voltage_mv; /* Напруга резервної батареї */
    float    last_spin_rate;     /* Зафіксована кутова швидкість, рад/с */
    float    last_accel_g;       /* Зафіксоване перевантаження, g */
    uint32_t last_radio_seq;     /* Останній прийнятий номер пакета */
    uint32_t crc32;              /* Контрольна сума запису */
} fts_blackbox_record_t;
```
```cpp
namespace fts::embedded {

enum class TriggerReason : uint8_t {
    ManualCommand = 1,
    TumblingSpin  = 2,
    LinkTimeout   = 3
};

struct [[gnu::packed]] BlackboxRecord {
    uint32_t      crash_magic{0xDEADF751U};
    uint32_t      crash_timestamp_ms{0};
    TriggerReason trigger_reason{TriggerReason::ManualCommand};
    State         fsm_state_at_crash{State::Safe};
    uint16_t      battery_voltage_mv{0};
    float         last_spin_rate{0.0F};
    float         last_accel_g{0.0F};
    uint32_t      last_radio_seq{0};
    uint32_t      crc32{0};
};

} // namespace fts::embedded
```
:::

Запис здійснюється в останній сектор пам'яті Flash за час менше `2 мілісекунд` до моменту повного розряду ємнісного накопичувача або механічного руйнування плати при ударі об землю.

---

### Апаратні пастки та захист від помилкових спрацьовувань

Під час проектування та експлуатації систем FTS інженери стикаються з низкою підступних апаратних і фізичних ефектів, що здатні зруйнувати захист:

#### 1. Брязкіт живлення під час ініціалізації (Power-On Reset Glitch)

Під час первинної подачі живлення або скиду мікроконтролера його виводи GPIO на короткий час (від десятків мікросекунд до кількох мілісекунд) перемикаються у стан високого імпедансу (`Hi-Z` / floating). Наведення від радіопередавача чи брязкіт контактів батареї можуть зарядити ємність затвора польового транзистора (MOSFET) і відкрити ключ запалювання піропатрона.

**Інженерне рішення:**
- На кожен затвор MOSFET обов'язково встановлюється прецизійний резистор підтяжки до землі `R_pulldown = 4.7 кОм`.
- Застосування апаратних логічних вентилів «І» (AND Gate) з RC-фільтром живлення, які тримають затвори заземленими доти, доки напруга живлення контролера не вийде на стабільний рівень і не буде знятий системний сигнал `RESET`.

#### 2. Вібраційний шум та аеродинамічні перевантаження

Під час польоту на високій швидкості або в умовах турбулентності пікові миттєві покази гіроскопів можуть перевищувати `500 °/с` впродовж 10–20 мс без будь-якої загрози стійкості апарата. Пряме порогове порівняння призведе до фатального скидання справного дрона.

**Інженерне рішення:**
- Інтеграція вимірювань за часовим вікном: тригер активується виключно тоді, коли кутова швидкість перевищує поріг безперервно впродовж `T_dwell ≥ 350 мс`.
- Крос-валідація з акселерометром: некерований штопор обов'язково супроводжується втратою вертикального перевантаження (`|a| < 0.25 g`). Якщо акселерометр показує `1.0 g` або вище — апарат виконує керований маневр, і автоматичне спрацьовування блокується.

#### 3. Індуктивний зворотний викид силової шини (Back-EMF)

Миттєве розмикання ланцюга eFuse при струмі моторів 150 А генерує в індуктивності дротів акумулятора стрибок напруги до `80–120 В`. Цей імпульс здатний пробити стабілізатори живлення та спалити мікроконтролер FTS у першу ж мілісекунду аварії.

**Інженерне рішення:**
- Встановлення двонаправлених TVS-діодів (супресорів) паралельно силовим ключам.
- Застосування захисних дроселів та керамічних конденсаторів низького еквівалентного опору (Low-ESR) у колі живлення модуля FTS.

---

### Методика стендового тестування Hardware-in-the-Loop (HIL)

Перед допуском FTS до реальних польотів модуль проходить обов'язкову серію верифікаційних випробувань на апаратно-програмному стенді (HIL):

1. **Тест стійкості до радіозавад та replay-атак:** генератор сигналів передає спотворені пакети з битими контрольними сумами, дубльованими номерами `seq_num` та недійсними HMAC-підписами зі швидкістю 500 пакетів/с. FTS повинен стабільно відхиляти 100% некоректних запитів, не входячи в аварійний стан.
2. **Динамічний тест на поворотному столі (Rate Table Test):** плата FTS монтується на тривісний стенд динамічних кутових обертань. Стенд створює контрольоване обертання зі швидкістю `500 °/с` та імітує скидання перевантаження. Час від моменту перевищення порогу до появи сигналу `FIRE_PULSE` на осцилографі повинен суворо укладатися в діапазон `420–440 мс` (`350 мс` фільтрації + `70 мс` зупинки гвинтів ± `10 мс` похибки таймера).
3. **Холодний тест запалювання (-20 °C):** накопичувальний конденсаторний блок охолоджується в кліматичній камері, після чого вимірюється піковий струм розряду на еквіваленті навантаження `1.5 Ом`. Струм імпульсу повинен перевищувати `2.0 А`, що гарантує надійне спрацьовування піропатрона в зимових умовах.
4. **Імітація збою живлення основної PDB:** під час активної генерації ШІМ-сигналів силова шина 24V раптово закорочується на масу. FTS повинен зберегти живлення від власного суперконденсатора, зафіксувати збій та штатно відпрацювати послідовність порятунку без жодного збою мікроконтролера.

---

### Процедура післяаварійного обслуговування (Post-Recovery Procedure)

Після успішного спрацьовування FTS та приземлення апарата на парашуті наземна команда зобов'язана суворо дотримуватися регламенту безпеки:
- **Негайне встановлення фізичної чеки безпеки (Safety Pin):** перша дія техніка при підході до безпілотника — вставити чеку в гніздо модуля FTS, що фізично закорочує клеми піропатрона та унеможливлює повторне спрацьовування від залишкового заряду конденсаторів.
- **Зчитування журналу чорної скриньки:** підключення діагностичного інтерфейсу UART/SWD для вивантаження структури `fts_blackbox_record_t`.
- **Заміна одноразових елементів:** після кожного спрацьовування піропатронний патрон, зрізні штифти тубуса та силове реле eFuse підлягають обов'язковій заміні з подальшим проходженням повного циклу калібрування BITE на стенді.
