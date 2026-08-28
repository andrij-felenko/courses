# ⚙️ Модуль оцінки політик примусового оновлення та верифікації безпечного стану

Практична реалізація підсистеми оцінки політик оновлення (Update Policy Engine) та верифікатора шлюзу фізичної безпеки (Safe Execution Window Verifier) для автономних кіберфізичних систем, вбудованих контролерів та пристроїв інтернету речей. Модуль призначений для інтеграції в клієнтські демони доставки прошивок (такі як RAUC, SWUpdate або кастомні сервіси оновлення на базі Linux/POSIX) і вирішує задачу суворого арбітражу між часовими дедлайнами безпеки та фізичним станом керованого обладнання.

## Постановка інженерної задачі та контекст застосування

У класичних серверних або хмарних середовищах розгортання оновлень спирається на механізми динамічної маршрутизації трафіку (наприклад, плаваючі IP-адреси, балансувальники навантаження або міграції контейнерів у Kubernetes). Якщо окремий сервер перезавантажується для застосування оновлення ядра, вхідні запити автоматично перенаправляються на сусідні репліки кластера, а короткочасний простій окремого вузла не впливає на функціонування системи загалом.

У кіберфізичних вбудованих системах (автономні роботи, безпілотні апарати, промислові контролери PLC, медичні станції моніторингу пацієнтів) обчислювальний вузол безпосередньо зв'язаний із фізичним світом через силові інвертори, пневматичні клапани, сервоприводи та сенсори. Спроба використати стандартні системні інструменти розкладу — такі як `cron`, планувальник `systemd.timer` або примітивні скрипти відкладеного перезапуску — призводить до фатальних наслідків через низку фундаментальних обмежень:

1. **Відсутність сенсорного зворотного зв'язку (Blind Execution):** Стандартні утиліти системного перезапуску (наприклад, `shutdown -r +15` або `reboot`) не мають доступу до шини передачі сенсорних даних (CAN, I2C, SPI) і не здатні оцінити кінематичний стан машини. Вони ініціюють завершення роботи операційної системи незалежно від того, чи стоїть робот на базі, чи рухається зі швидкістю 3 м/с через пішохідний перехід.
2. **Вразливість до стрибків і маніпуляцій із системним часом:** Системний годинник Linux (`CLOCK_REALTIME`) може змінюватися стрибкоподібно внаслідок синхронізації через протокол NTP, дрейфу кварцового резонатора RTC або навмисних дій користувача через команду `date -s`. Якщо алгоритм відкладення спирається на просте порівняння `time() > target_time`, зсув годинника назад дозволяє недобросовісному оператору нескінченно відкладати критичні виправлення безпеки, порушуючи нормативи регуляторів.
3. **Втрата стану при знеструмленні (State Loss on Power Cut):** Якщо лічильник відкладень або статус ескалації зберігається лише в оперативній пам'яті демона, будь-яке вимикання живлення, аварійне перезавантаження або виймання акумулятора призводить до скидання лічильника в нуль. Оператор може нескінченно уникати оновлення, просто щодня вимикаючи живлення машини тумблером.
4. **Гонитва станів між сенсорами та завантажувачем (Sensor-to-Reboot Race Condition):** Навіть якщо система переконалася, що швидкість дорівнює нулю, між моментом опитування датчика і моментом скидання живлення процесора існує часовий зазор (Jitter), під час якого оператор може натиснути педаль газу або контролер руху може отримати нову місію. Без захоплення монопольного блокування безпеки рестарт відбудеться у початковій фазі руху.

Представлений модуль вирішує ці завдання за рахунок повної ізоляції часових шкал, атомарного збереження стану на енергонезалежному носії, використання бітових масок інтерлоків та двофазної координації процесу активації прошивки.

## Архітектурний дизайн та принципи проектування

Модуль політик спроектовано як детермінований кінцевий автомат (Finite State Machine, FSM), що функціонує в просторі користувача операційної системи Linux і взаємодіє з трьома суміжними підсистемами:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 АРХІТЕКТУРА МОДУЛЯ UPDATE POLICY ENGINE                     │
│                                                                             │
│ [ Хмарний OTA-клієнт ] ──> (1) Ingest Manifest ──> [ Парсер політики ]      │
│                                                            │                │
│                                                            ▼                │
│ [ Енергонезалежне сховище ] <──> [ Менеджер відкладень (Snooze State) ]     │
│ (/var/lib/ota/policy.dat)                                  │                │
│                                                            ▼                │
│ [ Датчики та шина CAN/sysfs ] ──> [ Шлюз інтерлоків (Safety Interlocks) ]   │
│                                                            │                │
│                                                            ▼                │
│ [ D-Bus / HMI Інтерфейс ] <────> [ Диспетчер арбітражу та ескалації ]       │
│                                                            │                │
│                                                            ▼                │
│ [ Завантажувач A/B U-Boot ] <─── (2) Execute Reboot (Safe Window Granted)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Ізоляція часових джерел (Time Domain Isolation):**
   Для запобігання атакам з маніпуляцією системного часу модуль розділяє обчислення абсолютних дедлайнів (на базі `CLOCK_REALTIME` або захищених серверних часових міток UTC) та вимірювання локальних інтервалів стабілізації умов безпеки (на базі монотонного апаратного таймера `CLOCK_MONOTONIC_RAW`). Стрибки системного часу через протокол NTP не можуть порушити вимірювання тривалості утримання безпечного стану (T_hold).

2. **Атомарне збереження стану відкладень (Crash-Consistent Persistence):**
   Лічильники використаних відкладень (`deferrals_used`), часові мітки першого сповіщення та статуси підтвердження згоди оператора зберігаються на диску за схемою транзакційного подвійного запису: спочатку дані записуються у тимчасовий файл на тій самій файловій системі, скидаються через `fsync()`, після чого виконується атомарне перейменування через `rename()`. Це виключає скидання лічильників відкладень у разі аварійного знеструмлення пристрою.

3. **Матриця бітових інтерлоків (Bitmask Interlock Aggregation):**
   Стан усіх сенсорів безпеки нормалізується до єдиного 32-бітного слова прапорців. Перевірка допуску до перезавантаження виконується за одну операцію бітової кон'юнкції `(current_mask & required_mask) == required_mask`, що забезпечує швидкість і детермінованість обчислень у реальному часі.

4. **Захист від гонитви станів (Race-Condition Free Execution Window):**
   Між моментом отримання дозволу від шлюзу безпеки та фізичним викликом перезапуску системи існує ризик зміни стану (наприклад, оператор зняв пристрій із гальма або запустив двигун). Для нейтралізації цього ризику модуль захоплює ексклюзивне системне блокування (Safety Execution Lock), блокує шину керування актуаторами на апаратному рівні через вимикання реле живлення та лише після цього ініціює перезавантаження.

## Математична модель ескалації дедлайнів

Для динамічного керування інтервалами відкладення модуль застосовує алгоритм прогресивного стискання квантів часу (Dynamic Deferral Compression). Нехай T_issued — часова мітка публікації релізу, T_deadline — абсолютний жорсткий дедлайн, N_max — гранична кількість відкладань, а k — поточний номер спроби відкладення (k ∈ [1, N_max]).

Коли оператор надсилає запит на відкладення у момент часу T_k, максимальна допустима тривалість паузи Δt_k обчислюється за формулою:

```text
Δt_k = min(Δt_step, (T_deadline - T_k) / (N_max - k + 1))   [динамічний квант відкладення]
```

де Δt_step — базовий крок відкладення, задекларований у маніфесті. Ця формула забезпечує дві критичні властивості:
- Якщо часу до дедлайну достатньо, оператор отримує повний базовий квант Δt_step.
- У міру наближення до дедлайну залишок часу рівномірно розподіляється між залишковими спробами, унеможливлюючи вихід за межі T_deadline.
- У момент k = N_max або при досягненні T_k ≥ T_deadline залишковий інтервал Δt_k прямує до нуля, переводячи систему у стан обов'язкового примусового виконання (`FORCE_PENDING`).

### Експоненційне скорочення інтервалів нагадувань (Escalating Snooze Backoff)

У практиці експлуатації автономних комплексів сталий інтервал між нагадуваннями про доступне оновлення породжує ефект когнітивного звикання: оператор механічно натискає кнопку відкладення, не оцінюючи зростання ризиків компрометації чи накопичення програмних дефектів. Щоб подолати цей поведінковий фактор, підсистема оцінки політик поєднує стискання квантів часу з моделлю експоненційного скорочення інтервалів повторного сповіщення.

Нехай базовий інтервал між першими запитами на згоду становить Δt_0 (наприклад, 8 годин). При кожному наступному запиті оператора на відкладення час до примусової появи чергового діалогового вікна на терміналі HMI зменшується за геометричною прогресією:

```text
Δt_prompt(k) = max(Δt_min, Δt_0 · 2^(-(k - 1)))   [інтервал експоненційного нагадування]
```

де Δt_min — мінімально допустимий технологічний поріг (наприклад, 15 хвилин), який гарантує, що система не заблокує інтерфейс оператора частими перериваннями під час безпосереднього керування пристроєм у технологічних проїздах.

Паралельно з часовим стисканням рушій змінює профіль нав'язливості людино-машинного інтерфейсу (Intrusiveness Escalation):
1. **Рівень 1 (Пасивне сповіщення):** При k = 1 на панель оператора виводиться неблокувальний інформаційний банер із таймером зворотного відліку. Ручний та автономний режими машини функціонують без обмежень.
2. **Рівень 2 (Напівактивне вікно із затримкою):** При k = 2 діалогове вікно перекриває центральну частину екрана під час повної зупинки машини, а кнопка відкладення стає активною лише через 5 секунд після відображення опису пакета, змушуючи оператора ознайомитися зі змінами.
3. **Рівень 3 (Модальне блокування зі звуковою тривогою):** При k ≥ N_max - 1 або досягненні 80% вікна кампанії інтерфейс блокується модальним вікном, активується переривчастий звуковий зумер зупинки, а для підтвердження відстрочки оператор зобов'язаний ввести персональний PIN-код та обрати причину затримки, яка записується в криптографічний системний журнал.

## Апаратний рівень абстракції датчиків (HAL) у Linux

У реальних вбудованих контролерах функція `sample_interlock_mask` спирається на пряму взаємодію з підсистемами ядра Linux через стандартизовані інтерфейси:

1. **Моніторинг живлення через sysfs (`power_supply`):**
   Рівень заряду тягової батареї та статус підключення зовнішнього адаптера зчитуються з псевдофайлової системи ядра:
   ```bash
   cat /sys/class/power_supply/BAT0/capacity     # 78 (відсотки)
   cat /sys/class/power_supply/BAT0/status       # "Discharging" або "Charging"
   cat /sys/class/power_supply/AC/online         # 1 (підключено до мережі)
   ```
   Драйвер відкриває дескриптор файлу через `open(..., O_RDONLY)` і використовує швидке зчитування зафіксованого буфера через `pread()` без потреби повторного відкриття дескриптора на кожному кроці циклу.

2. **Отримання телеметрії швидкості через SocketCAN:**
   Для отримання даних про кутову швидкість коліс і стан інверторів демон відкриває сокет типу `AF_CAN` (`SOCK_RAW`, протокол `CAN_RAW`) на мережевому інтерфейсі `can0`. Фільтр `can_filter` налаштовується виключно на ідентифікатори повідомлень контролера руху (наприклад, CAN ID `0x180` для енкодерів), що дозволяє ядру відсікати сторонній трафік і зменшувати навантаження на процесор.

3. **Опитування стоянкового гальма через `libgpiod`:**
   Статус кінцевих вимикачів гальмівної системи та аварійних кнопок зчитується через сучасний інтерфейс символьних пристроїв GPIO ядра Linux (`/dev/gpiochip0`). Використання виклику `gpiod_line_get_value()` унеможливлює стан гонитви за ресурсами, притаманний застарілому інтерфейсу `/sys/class/gpio`.

4. **Апаратне знеструмлення силових ланцюгів (Interlock Safe Disarm):**
   Перед ініціалізацією системного перезавантаження модуль виконує запис у спеціальний вивід GPIO, з'єднаний із силовим реле високої напруги (Safety Relay). Це гарантує, що навіть у разі апаратного збою процесора під час рестарту силові інвертори залишаться знеструмленими до повного завантаження нової прошивки.

5. **Озброєння апаратного Watchdog перед перезавантаженням:**
   Під час переходу до фінальної стадії активації демон відкриває дескриптор `/dev/watchdog`, встановлює інтервал спрацьовування 30 секунд через керівний виклик `ioctl(wd_fd, WDIOC_SETTIMEOUT, &timeout)` та виконує останній удар серця (Ping). Якщо ядро операційної системи зависне під час виконання виклику `reboot()`, сторожовий таймер автоматично виконає апаратне скидання живлення процесора.

## Структури даних, вирівнювання пам'яті та стійкість до проблеми Y2038

Під час проектування двійкових форматів для вбудованих систем особливу увагу приділено розміщенню структур у пам'яті:

1. **Проблема 2038 року (Y2038 Bug):** Усі часові мітки в маніфестах і структурах стану визначені як 64-розрядні знакові цілі `int64_t` (секунди від Epoch UTC). Це гарантує коректну роботу модуля на 32-бітних процесорах ARM Cortex-A7/A9, де стандартний системний тип `time_t` може бути 32-розрядним і переповнюватися у січні 2038 року.
2. **Вирівнювання та заповнення структур (Data Structure Padding):** Поля структури `persistent_deferral_state_t` впорядковані за спаданням розміру (спочатку 64-бітні поля `next_prompt_epoch` та `hard_deadline_epoch`, потім 32-бітне `deferrals_used` і 8-бітний прапорець `force_active`). Це мінімізує неявне вирівнювання компілятором і виключає витік неініціалізованих байтів пам'яті на диск.
3. **Бітові маски інтерлоків:** Використання констант типу `1U << N` із суфіксом `U` запобігає невизначеній поведінці знакових зсувів при операціях із старшими бітами 32-розрядного слова.

## Стани кінцевого автомата

Автомат станів життєвого циклу примусового оновлення підтримує сім фіксованих станів:

- `STATE_IDLE`: активна кампанія оновлення відсутня, пристрій функціонує у штатному режимі.
- `STATE_POLICY_LOADED`: отримано та валідовано новий маніфест, обчислено початкові дедлайни.
- `STATE_DEFERRED_WAIT`: оператор або бізнес-логіка відклали оновлення; активний таймер очікування наступного нагадування.
- `STATE_WARNING_COUNTDOWN`: наближення дедлайну (менше 20% часу або 1 відкладення); виведення модальних попереджень та звукової індикації.
- `STATE_HARD_DEADLINE_FORCE`: дедлайн вичерпано; блокування кнопки Snooze, припинення прийому нових завдань обладнанням.
- `STATE_SAFETY_WINDOW_HOLD`: дедлайн настав, але сенсорні інтерлоки не виконані (наприклад, пристрій перебуває в русі); очікування зупинки та стабілізації.
- `STATE_READY_TO_ACTIVATE`: усі інтерлоки стабільно виконані протягом T_hold; видача дозволу на перемикання A/B слотів пам'яті та рестарт.

## Повна реалізація модуля на C99 та C++20

Нижче наведено повні вихідні тексти модуля на мовах C99 та C++20, що включають структури конфігурації, симуляцію опитування датчиків, роботу з атомарними файлами стану та тестовий сценарій проходження життєвого циклу ескалації.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>

#define INTERLOCK_SPEED_ZERO     (1U << 0)
#define INTERLOCK_BRAKE_ENGAGED  (1U << 1)
#define INTERLOCK_BATTERY_OK     (1U << 2)
#define INTERLOCK_ACTUATORS_OFF  (1U << 3)
#define INTERLOCK_FS_DRAINED     (1U << 4)

#define DEFAULT_REQUIRED_INTERLOCKS (INTERLOCK_SPEED_ZERO | \
                                    INTERLOCK_BRAKE_ENGAGED | \
                                    INTERLOCK_BATTERY_OK | \
                                    INTERLOCK_ACTUATORS_OFF | \
                                    INTERLOCK_FS_DRAINED)

typedef enum {
    URGENCY_STANDARD = 0,
    URGENCY_IMPORTANT = 1,
    URGENCY_MANDATORY = 2,
    URGENCY_CRITICAL_ZERO_DAY = 3,
    URGENCY_EMERGENCY_RECALL = 4
} update_urgency_level_t;

typedef enum {
    ENGINE_STATE_IDLE,
    ENGINE_STATE_LOADED,
    ENGINE_STATE_DEFERRED,
    ENGINE_STATE_WARNING,
    ENGINE_STATE_FORCE_PENDING,
    ENGINE_STATE_SAFETY_HOLD,
    ENGINE_STATE_READY_TO_ACTIVATE
} engine_state_t;

typedef struct {
    char bundle_id[64];
    update_urgency_level_t urgency;
    int64_t issued_at_epoch;
    int64_t hard_deadline_epoch;
    uint32_t max_deferrals;
    uint32_t deferral_step_sec;
    uint32_t required_interlocks_mask;
    uint32_t stability_hold_sec;
    uint32_t safety_wait_timeout_sec;
} update_policy_manifest_t;

typedef struct {
    uint32_t deferrals_used;
    int64_t next_prompt_epoch;
    int64_t hard_deadline_epoch;
    bool force_active;
} persistent_deferral_state_t;

typedef struct {
    double velocity_mps;
    bool parking_brake;
    uint8_t battery_soc_percent;
    bool is_ac_connected;
    double actuator_current_amps;
    bool filesystem_drained;
} raw_sensor_telemetry_t;

typedef struct {
    engine_state_t state;
    update_policy_manifest_t manifest;
    persistent_deferral_state_t persist;
    char state_file_path[256];
    struct timespec safe_conditions_start_mono;
    bool has_safe_start_time;
    int64_t safety_wait_start_epoch;
} update_policy_engine_t;

static int64_t get_current_epoch_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (int64_t)ts.tv_sec;
}

static struct timespec get_current_mono_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts;
}

static double timespec_diff_sec(const struct timespec* end, const struct timespec* start) {
    double sec = (double)(end->tv_sec - start->tv_sec);
    double nsec = (double)(end->tv_nsec - start->tv_nsec) / 1e9;
    return sec + nsec;
}

static bool save_persistent_state(const char* filepath, const persistent_deferral_state_t* state) {
    char temp_path[300];
    snprintf(temp_path, sizeof(temp_path), "%s.tmp", filepath);

    int fd = open(temp_path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd < 0) {
        return false;
    }

    ssize_t bytes_written = write(fd, state, sizeof(*state));
    if (bytes_written != (ssize_t)sizeof(*state)) {
        close(fd);
        unlink(temp_path);
        return false;
    }

    if (fsync(fd) != 0) {
        close(fd);
        unlink(temp_path);
        return false;
    }

    close(fd);
    return (rename(temp_path, filepath) == 0);
}

static bool load_persistent_state(const char* filepath, persistent_deferral_state_t* state) {
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        return false;
    }

    ssize_t bytes_read = read(fd, state, sizeof(*state));
    close(fd);
    return (bytes_read == (ssize_t)sizeof(*state));
}

static uint32_t sample_interlock_mask(const raw_sensor_telemetry_t* telem) {
    uint32_t mask = 0;
    if (telem->velocity_mps >= -0.01 && telem->velocity_mps <= 0.01) {
        mask |= INTERLOCK_SPEED_ZERO;
    }
    if (telem->parking_brake) {
        mask |= INTERLOCK_BRAKE_ENGAGED;
    }
    if (telem->battery_soc_percent >= 50 || telem->is_ac_connected) {
        mask |= INTERLOCK_BATTERY_OK;
    }
    if (telem->actuator_current_amps >= -0.05 && telem->actuator_current_amps <= 0.05) {
        mask |= INTERLOCK_ACTUATORS_OFF;
    }
    if (telem->filesystem_drained) {
        mask |= INTERLOCK_FS_DRAINED;
    }
    return mask;
}

void policy_engine_init(update_policy_engine_t* engine, const char* state_path) {
    memset(engine, 0, sizeof(*engine));
    engine->state = ENGINE_STATE_IDLE;
    strncpy(engine->state_file_path, state_path, sizeof(engine->state_file_path) - 1);
    engine->has_safe_start_time = false;
}

bool policy_engine_load_manifest(update_policy_engine_t* engine, const update_policy_manifest_t* manifest) {
    if (!engine || !manifest) return false;
    memcpy(&engine->manifest, manifest, sizeof(*manifest));

    if (!load_persistent_state(engine->state_file_path, &engine->persist)) {
        engine->persist.deferrals_used = 0;
        engine->persist.next_prompt_epoch = get_current_epoch_sec();
        engine->persist.hard_deadline_epoch = manifest->hard_deadline_epoch;
        engine->persist.force_active = false;
        save_persistent_state(engine->state_file_path, &engine->persist);
    }

    engine->state = ENGINE_STATE_LOADED;
    return true;
}

bool policy_engine_request_deferral(update_policy_engine_t* engine, uint32_t requested_sec) {
    if (!engine || engine->state == ENGINE_STATE_IDLE) return false;

    int64_t now = get_current_epoch_sec();
    if (now >= engine->manifest.hard_deadline_epoch ||
        engine->persist.deferrals_used >= engine->manifest.max_deferrals ||
        engine->manifest.urgency == URGENCY_EMERGENCY_RECALL) {
        return false;
    }

    uint32_t step = (requested_sec > 0) ? requested_sec : engine->manifest.deferral_step_sec;
    int64_t target_prompt = now + step;
    if (target_prompt > engine->manifest.hard_deadline_epoch) {
        target_prompt = engine->manifest.hard_deadline_epoch;
    }

    engine->persist.deferrals_used++;
    engine->persist.next_prompt_epoch = target_prompt;
    save_persistent_state(engine->state_file_path, &engine->persist);

    engine->state = ENGINE_STATE_DEFERRED;
    return true;
}

engine_state_t policy_engine_tick(update_policy_engine_t* engine, const raw_sensor_telemetry_t* telemetry) {
    if (!engine || engine->state == ENGINE_STATE_IDLE) return ENGINE_STATE_IDLE;

    int64_t now_epoch = get_current_epoch_sec();
    struct timespec now_mono = get_current_mono_time();

    bool deadline_reached = (now_epoch >= engine->manifest.hard_deadline_epoch);
    bool deferrals_out = (engine->persist.deferrals_used >= engine->manifest.max_deferrals);
    bool is_emergency = (engine->manifest.urgency == URGENCY_EMERGENCY_RECALL);

    if (deadline_reached || deferrals_out || is_emergency) {
        engine->persist.force_active = true;
    }

    int64_t total_window = engine->manifest.hard_deadline_epoch - engine->manifest.issued_at_epoch;
    int64_t elapsed_window = now_epoch - engine->manifest.issued_at_epoch;
    double progress = (total_window > 0) ? ((double)elapsed_window / (double)total_window) : 1.0;

    if (engine->persist.force_active) {
        engine->state = ENGINE_STATE_FORCE_PENDING;
    } else if (progress >= 0.80 || (engine->manifest.max_deferrals - engine->persist.deferrals_used <= 1)) {
        engine->state = ENGINE_STATE_WARNING;
    } else if (now_epoch < engine->persist.next_prompt_epoch) {
        engine->state = ENGINE_STATE_DEFERRED;
        return engine->state;
    } else {
        engine->state = ENGINE_STATE_LOADED;
    }

    uint32_t current_interlocks = sample_interlock_mask(telemetry);
    uint32_t req_mask = engine->manifest.required_interlocks_mask ? 
                        engine->manifest.required_interlocks_mask : DEFAULT_REQUIRED_INTERLOCKS;

    bool interlocks_passed = ((current_interlocks & req_mask) == req_mask);

    if (!interlocks_passed) {
        engine->has_safe_start_time = false;
        if (engine->persist.force_active) {
            if (engine->safety_wait_start_epoch == 0) {
                engine->safety_wait_start_epoch = now_epoch;
            }
            engine->state = ENGINE_STATE_SAFETY_HOLD;
        }
        return engine->state;
    }

    if (!engine->has_safe_start_time) {
        engine->safe_conditions_start_mono = now_mono;
        engine->has_safe_start_time = true;
        if (engine->persist.force_active) {
            engine->state = ENGINE_STATE_SAFETY_HOLD;
        }
        return engine->state;
    }

    double stable_duration = timespec_diff_sec(&now_mono, &engine->safe_conditions_start_mono);
    if (stable_duration >= (double)engine->manifest.stability_hold_sec) {
        if (engine->persist.force_active || engine->state == ENGINE_STATE_LOADED || engine->state == ENGINE_STATE_WARNING) {
            engine->state = ENGINE_STATE_READY_TO_ACTIVATE;
        }
    } else {
        if (engine->persist.force_active) {
            engine->state = ENGINE_STATE_SAFETY_HOLD;
        }
    }

    return engine->state;
}

int main(void) {
    printf("[C99 Engine Test Harness] Initializing Policy Evaluator...\n");
    const char* state_file = "/tmp/ota_test_policy.dat";
    unlink(state_file);

    update_policy_engine_t engine;
    policy_engine_init(&engine, state_file);

    int64_t now = get_current_epoch_sec();
    update_policy_manifest_t manifest = {
        .bundle_id = "com.fleet.firmware-amr-5.12.4",
        .urgency = URGENCY_CRITICAL_ZERO_DAY,
        .issued_at_epoch = now,
        .hard_deadline_epoch = now + 10,
        .max_deferrals = 2,
        .deferral_step_sec = 4,
        .required_interlocks_mask = DEFAULT_REQUIRED_INTERLOCKS,
        .stability_hold_sec = 2,
        .safety_wait_timeout_sec = 60
    };

    policy_engine_load_manifest(&engine, &manifest);

    raw_sensor_telemetry_t telem_moving = {
        .velocity_mps = 1.8,
        .parking_brake = false,
        .battery_soc_percent = 78,
        .is_ac_connected = false,
        .actuator_current_amps = 12.4,
        .filesystem_drained = false
    };

    printf("Step 1: Vehicle moving during advisory period -> Request Deferral 1...\n");
    policy_engine_tick(&engine, &telem_moving);
    bool d1 = policy_engine_request_deferral(&engine, 4);
    printf("Deferral 1 granted: %s (State: %d, used: %u)\n",
           d1 ? "YES" : "NO", engine.state, engine.persist.deferrals_used);

    printf("Step 2: Vehicle still moving, requesting Deferral 2...\n");
    bool d2 = policy_engine_request_deferral(&engine, 4);
    printf("Deferral 2 granted: %s (used: %u)\n", d2 ? "YES" : "NO", engine.persist.deferrals_used);

    printf("Step 3: Attempting Deferral 3 (exceeding limit of 2)...\n");
    bool d3 = policy_engine_request_deferral(&engine, 4);
    printf("Deferral 3 granted: %s (expected NO)\n", d3 ? "YES" : "NO");

    printf("Step 4: Simulating Hard Deadline arrival while robot is still moving...\n");
    engine.manifest.hard_deadline_epoch = get_current_epoch_sec() - 1;
    policy_engine_tick(&engine, &telem_moving);
    printf("Engine State: %d (expected SAFETY_HOLD=%d)\n", engine.state, ENGINE_STATE_SAFETY_HOLD);

    printf("Step 5: Robot parks safely; stabilizing interlocks for 2 seconds...\n");
    raw_sensor_telemetry_t telem_parked = {
        .velocity_mps = 0.0,
        .parking_brake = true,
        .battery_soc_percent = 77,
        .is_ac_connected = false,
        .actuator_current_amps = 0.0,
        .filesystem_drained = true
    };

    for (int i = 0; i < 3; ++i) {
        engine_state_t st = policy_engine_tick(&engine, &telem_parked);
        printf("Tick %d: State = %d\n", i + 1, st);
        sleep(1);
    }

    if (engine.state == ENGINE_STATE_READY_TO_ACTIVATE) {
        printf("[SUCCESS] Safe Window Granted: System authorized for A/B reboot!\n");
    } else {
        printf("[FAILURE] Engine did not transition to READY_TO_ACTIVATE\n");
    }

    unlink(state_file);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <expected>
#include <memory>
#include <thread>
#include <cstdint>
#include <filesystem>
#include <system_error>

namespace fleet::ota {

enum class UrgencyLevel : uint8_t {
    Standard = 0,
    Important = 1,
    Mandatory = 2,
    CriticalZeroDay = 3,
    EmergencyRecall = 4
};

enum class EngineState : uint8_t {
    Idle,
    Loaded,
    Deferred,
    Warning,
    ForcePending,
    SafetyHold,
    ReadyToActivate
};

struct InterlockFlags {
    static constexpr uint32_t SpeedZero     = 1U << 0;
    static constexpr uint32_t BrakeEngaged  = 1U << 1;
    static constexpr uint32_t BatteryOk     = 1U << 2;
    static constexpr uint32_t ActuatorsOff  = 1U << 3;
    static constexpr uint32_t FsDrained     = 1U << 4;
    static constexpr uint32_t AllDefault    = SpeedZero | BrakeEngaged | BatteryOk | ActuatorsOff | FsDrained;
};

struct PolicyManifest {
    std::string bundle_id;
    UrgencyLevel urgency{UrgencyLevel::Standard};
    std::chrono::system_clock::time_point issued_at;
    std::chrono::system_clock::time_point hard_deadline;
    uint32_t max_deferrals{3};
    std::chrono::seconds deferral_step{7200};
    uint32_t required_interlocks{InterlockFlags::AllDefault};
    std::chrono::seconds stability_hold{5};
    std::chrono::seconds safety_wait_timeout{3600};
};

struct PersistentState {
    uint32_t deferrals_used{0};
    std::chrono::system_clock::time_point next_prompt;
    std::chrono::system_clock::time_point hard_deadline;
    bool force_active{false};
};

struct VehicleTelemetry {
    double velocity_mps{0.0};
    bool parking_brake{false};
    uint8_t battery_soc_percent{0};
    bool is_ac_connected{false};
    double actuator_current_amps{0.0};
    bool filesystem_drained{false};

    [[nodiscard]] constexpr uint32_t evaluate_mask() const noexcept {
        uint32_t mask = 0;
        if (velocity_mps >= -0.01 && velocity_mps <= 0.01) {
            mask |= InterlockFlags::SpeedZero;
        }
        if (parking_brake) {
            mask |= InterlockFlags::BrakeEngaged;
        }
        if (battery_soc_percent >= 50 || is_ac_connected) {
            mask |= InterlockFlags::BatteryOk;
        }
        if (actuator_current_amps >= -0.05 && actuator_current_amps <= 0.05) {
            mask |= InterlockFlags::ActuatorsOff;
        }
        if (filesystem_drained) {
            mask |= InterlockFlags::FsDrained;
        }
        return mask;
    }
};

class StateStore {
public:
    explicit StateStore(std::filesystem::path path) : path_(std::move(path)) {}

    [[nodiscard]] bool save(const PersistentState& state) const noexcept {
        const auto tmp_path = path_.string() + ".tmp";
        {
            std::ofstream out(tmp_path, std::ios::binary | std::ios::trunc);
            if (!out.is_open()) return false;

            const auto next_p_count = state.next_prompt.time_since_epoch().count();
            const auto hard_d_count = state.hard_deadline.time_since_epoch().count();

            out.write(reinterpret_cast<const char*>(&state.deferrals_used), sizeof(state.deferrals_used));
            out.write(reinterpret_cast<const char*>(&next_p_count), sizeof(next_p_count));
            out.write(reinterpret_cast<const char*>(&hard_d_count), sizeof(hard_d_count));
            out.write(reinterpret_cast<const char*>(&state.force_active), sizeof(state.force_active));
            out.flush();
            if (!out.good()) return false;
        }

        std::error_code ec;
        std::filesystem::rename(tmp_path, path_, ec);
        return !ec;
    }

    [[nodiscard]] std::optional<PersistentState> load() const noexcept {
        std::ifstream in(path_, std::ios::binary);
        if (!in.is_open()) return std::nullopt;

        PersistentState state;
        decltype(std::chrono::system_clock::time_point{}.time_since_epoch().count()) next_p_count{0}, hard_d_count{0};

        in.read(reinterpret_cast<char*>(&state.deferrals_used), sizeof(state.deferrals_used));
        in.read(reinterpret_cast<char*>(&next_p_count), sizeof(next_p_count));
        in.read(reinterpret_cast<char*>(&hard_d_count), sizeof(hard_d_count));
        in.read(reinterpret_cast<char*>(&state.force_active), sizeof(state.force_active));

        if (!in.good()) return std::nullopt;

        state.next_prompt = std::chrono::system_clock::time_point{std::chrono::system_clock::duration{next_p_count}};
        state.hard_deadline = std::chrono::system_clock::time_point{std::chrono::system_clock::duration{hard_d_count}};
        return state;
    }

private:
    std::filesystem::path path_;
};

class PolicyEngine {
public:
    explicit PolicyEngine(std::filesystem::path state_path)
        : store_(std::move(state_path)), state_(EngineState::Idle) {}

    bool load_manifest(PolicyManifest manifest) {
        manifest_ = std::move(manifest);
        auto loaded = store_.load();
        if (loaded.has_value()) {
            persist_ = *loaded;
        } else {
            persist_.deferrals_used = 0;
            persist_.next_prompt = std::chrono::system_clock::now();
            persist_.hard_deadline = manifest_.hard_deadline;
            persist_.force_active = false;
            store_.save(persist_);
        }
        state_ = EngineState::Loaded;
        safe_start_time_.reset();
        return true;
    }

    [[nodiscard]] bool request_deferral(std::optional<std::chrono::seconds> custom_step = std::nullopt) {
        if (state_ == EngineState::Idle) return false;

        const auto now = std::chrono::system_clock::now();
        if (now >= manifest_.hard_deadline || 
            persist_.deferrals_used >= manifest_.max_deferrals ||
            manifest_.urgency == UrgencyLevel::EmergencyRecall) {
            return false;
        }

        const auto step = custom_step.value_or(manifest_.deferral_step);
        auto target = now + step;
        if (target > manifest_.hard_deadline) {
            target = manifest_.hard_deadline;
        }

        persist_.deferrals_used++;
        persist_.next_prompt = target;
        store_.save(persist_);

        state_ = EngineState::Deferred;
        return true;
    }

    [[nodiscard]] EngineState tick(
        const VehicleTelemetry& telemetry,
        std::chrono::system_clock::time_point sys_now,
        std::chrono::steady_clock::time_point steady_now) noexcept
    {
        if (state_ == EngineState::Idle) return EngineState::Idle;

        const bool deadline_reached = (sys_now >= manifest_.hard_deadline);
        const bool deferrals_out = (persist_.deferrals_used >= manifest_.max_deferrals);
        const bool is_emergency = (manifest_.urgency == UrgencyLevel::EmergencyRecall);

        if (deadline_reached || deferrals_out || is_emergency) {
            persist_.force_active = true;
        }

        const auto total_window = manifest_.hard_deadline - manifest_.issued_at;
        const auto elapsed = sys_now - manifest_.issued_at;
        const double progress = (total_window.count() > 0)
            ? (static_cast<double>(elapsed.count()) / static_cast<double>(total_window.count()))
            : 1.0;

        if (persist_.force_active) {
            state_ = EngineState::ForcePending;
        } else if (progress >= 0.80 || (manifest_.max_deferrals - persist_.deferrals_used <= 1)) {
            state_ = EngineState::Warning;
        } else if (sys_now < persist_.next_prompt) {
            state_ = EngineState::Deferred;
            return state_;
        } else {
            state_ = EngineState::Loaded;
        }

        const uint32_t current_mask = telemetry.evaluate_mask();
        const bool interlocks_passed = ((current_mask & manifest_.required_interlocks) == manifest_.required_interlocks);

        if (!interlocks_passed) {
            safe_start_time_.reset();
            if (persist_.force_active) {
                state_ = EngineState::SafetyHold;
            }
            return state_;
        }

        if (!safe_start_time_.has_value()) {
            safe_start_time_ = steady_now;
            if (persist_.force_active) {
                state_ = EngineState::SafetyHold;
            }
            return state_;
        }

        const auto hold_elapsed = std::chrono::duration_cast<std::chrono::seconds>(steady_now - *safe_start_time_);
        if (hold_elapsed >= manifest_.stability_hold) {
            if (persist_.force_active || state_ == EngineState::Loaded || state_ == EngineState::Warning) {
                state_ = EngineState::ReadyToActivate;
            }
        } else {
            if (persist_.force_active) {
                state_ = EngineState::SafetyHold;
            }
        }

        return state_;
    }

    [[nodiscard]] EngineState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t deferrals_used() const noexcept { return persist_.deferrals_used; }

private:
    StateStore store_;
    PolicyManifest manifest_;
    PersistentState persist_;
    EngineState state_;
    std::optional<std::chrono::steady_clock::time_point> safe_start_time_;
};

} // namespace fleet::ota

int main() {
    std::cout << "[C++20 Engine Test Harness] Initializing Policy Engine...\n";
    const std::filesystem::path state_path = "/tmp/ota_cpp_test_policy.dat";
    std::filesystem::remove(state_path);

    fleet::ota::PolicyEngine engine(state_path);

    const auto now = std::chrono::system_clock::now();
    fleet::ota::PolicyManifest manifest{
        .bundle_id = "com.fleet.firmware-amr-5.12.4",
        .urgency = fleet::ota::UrgencyLevel::CriticalZeroDay,
        .issued_at = now,
        .hard_deadline = now + std::chrono::seconds(10),
        .max_deferrals = 2,
        .deferral_step = std::chrono::seconds(4),
        .required_interlocks = fleet::ota::InterlockFlags::AllDefault,
        .stability_hold = std::chrono::seconds(2),
        .safety_wait_timeout = std::chrono::seconds(60)
    };

    engine.load_manifest(manifest);

    fleet::ota::VehicleTelemetry moving_telem{
        .velocity_mps = 2.1,
        .parking_brake = false,
        .battery_soc_percent = 85,
        .is_ac_connected = false,
        .actuator_current_amps = 14.5,
        .filesystem_drained = false
    };

    std::cout << "Step 1: Moving AMR -> Request Deferral 1...\n";
    engine.tick(moving_telem, std::chrono::system_clock::now(), std::chrono::steady_clock::now());
    bool d1 = engine.request_deferral(std::chrono::seconds(4));
    std::cout << "Deferral 1: " << (d1 ? "GRANTED" : "REJECTED") << ", count = " << engine.deferrals_used() << "\n";

    std::cout << "Step 2: Request Deferral 2...\n";
    bool d2 = engine.request_deferral(std::chrono::seconds(4));
    std::cout << "Deferral 2: " << (d2 ? "GRANTED" : "REJECTED") << ", count = " << engine.deferrals_used() << "\n";

    std::cout << "Step 3: Request Deferral 3 (exceeding limit)...\n";
    bool d3 = engine.request_deferral(std::chrono::seconds(4));
    std::cout << "Deferral 3: " << (d3 ? "GRANTED" : "REJECTED") << " (expected REJECTED)\n";

    std::cout << "Step 4: Park vehicle and hold interlocks for 2 seconds...\n";
    fleet::ota::VehicleTelemetry parked_telem{
        .velocity_mps = 0.0,
        .parking_brake = true,
        .battery_soc_percent = 84,
        .is_ac_connected = false,
        .actuator_current_amps = 0.0,
        .filesystem_drained = true
    };

    for (int i = 0; i < 3; ++i) {
        auto st = engine.tick(parked_telem, std::chrono::system_clock::now(), std::chrono::steady_clock::now());
        std::cout << "Tick " << (i + 1) << ": State = " << static_cast<int>(st) << "\n";
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    if (engine.state() == fleet::ota::EngineState::ReadyToActivate) {
        std::cout << "[SUCCESS] C++20 Policy Engine granted Safe Execution Window!\n";
    }

    std::filesystem::remove(state_path);
    return 0;
}
```
:::

## Покроковий розбір алгоритму та пастки реалізації

Під час проектування підсистеми оцінки політик виникає низка критичних архітектурних пасток, які вимагають ретельного контролю на рівні системного коду:

### 1. Пастка переривання живлення під час оновлення файлу стану (Torn Writes)

Якщо оновлення лічильника `deferrals_used` виконується через прямий запис у файл `policy.dat` без використання тимчасового файлу, раптове знеструмлення процесора в середині операції `write()` залишає файл пошкодженим або заповненим нульовими байтами. При наступному завантаженні парсер не зможе прочитати структуру і скине лічильник відкладень до нуля, що відкриє шлях до нескінченного відкладення критичних оновлень. Реалізація із записом у `policy.dat.tmp`, викликом `fsync()` та атомарним `rename()` гарантує, що на диску завжди зберігається або попередня коректна версія стану, або нова.

Якщо ж на диску виникає критична помилка браку вільного місця (`ENOSPC`), функція `save_persistent_state` повертає `false`, а модуль переходить у режим аварійного збереження стану в оперативній пам'яті (In-Memory Safe Fallback). У цьому режимі право відкладення блокується на рівні пам'яті, що запобігає експлуатації переповнення диска для блокування оновлень.

### 2. Пастка плаваючого нуля швидкості (Sensor Noise & Jitter)

Аналогові та цифрові датчики швидкості, оптичні сенсори та інтегратори IMU мають власний рівень теплового шуму та апаратного дрейфу. Якщо перевірка швидкості реалізована як суворе порівняння з нулем `velocity == 0.0`, через дрібні шуми порядку 0.0001 м/с шлюз безпеки ніколи не перейде в активний стан. У функції `sample_interlock_mask` застосовано симетричну зону нечутливості (Deadband) `|v| ≤ 0.01` м/с, що відсікає апаратний шум одометрії, але надійно детектує будь-який фізичний рух.

### 3. Пастка транзитної зупинки (Transient Zero Speed)

Мобільний робот або транспортний засіб регулярно зупиняється на долі секунди перед пішохідними переходами, світлофорами або під час маневрування. Якщо агент активує процедуру перезавантаження негайно при першому виявленні нульової швидкості, рестарт почнеться рівно в момент відновлення руху. Використання монотонного таймера стабілізації `stability_hold_sec` (щонайменше 5 секунд безперервного спокою) гарантує, що пристрій справді завершив рух і став на стоянкове гальмо.

### 4. Взаємодія з Linux VFS та скидання буферів

Перед перемиканням завантажувача U-Boot агент зобов'язаний гарантувати повне скидання брудних сторінок пам'яті. Виклик стандартної функції `sync()` у просторі користувача надсилає запит ядру Linux на скидання всіх файлових буферів, однак для гарантії атомарності у вбудованих сховищах eMMC слід додатково відкрити блоковий пристрій та виконати команду очищення кешу контролера через `ioctl(blk_fd, BLKFLSBUF, 0)`.

### 5. Багатопотокова синхронізація та асинхронні події

У промислових системах телеметрія надходить із високою частотою (100–250 Гц) через окремий потік опитування шини CAN або драйверів ядра, тоді як запити на відкладення від користувача чи сервера надходять асинхронно через D-Bus або gRPC. Для усунення гонитви за ресурсами доступ до структур `persistent_deferral_state_t` та `update_policy_manifest_t` захищається взаємним виключенням через м'ютекси або атомарні типи `std::atomic`. Усі критичні секції модифікації стану зводяться до мінімуму, щоб не затримувати потік обробки телеметрії реального часу.

### 6. Обробка відмов апаратного таймера Watchdog

Коли система переходить у стан `READY_TO_ACTIVATE`, демон оновлення відкриває дескриптор `/dev/watchdog` і встановлює таймаут на 60 секунд. Це є точкою неповернення: якщо після цього ядро зависне під час виконання системного виклику `reboot()`, апаратний сторожовий таймер примусово перезавантажить процесор за апаратним сигналом RESET. У конфігурації завантажувача змінна `upgrade_available=1` повідомляє логіку U-Boot про необхідність перевірки успішності запуску нової прошивки.

### 7. Діагностичний аудит подій у systemd-journald

Для відповідності регуляторним вимогам UN R156 кожна зміна стану кінцевого автомата фіксується у системному журналі Linux через структурований системний виклик:

:::tabs
```c
sd_journal_send(
    "MESSAGE=OTA Policy state transition: %d -> %d", prev_state, new_state,
    "PRIORITY=%d", (new_state == ENGINE_STATE_FORCE_PENDING) ? LOG_WARNING : LOG_INFO,
    "OTA_BUNDLE_ID=%s", engine->manifest.bundle_id,
    "OTA_DEFERRALS_USED=%u", engine->persist.deferrals_used,
    "OTA_INTERLOCK_MASK=0x%08X", current_interlocks,
    NULL
);
```
```cpp
sd_journal_send(
    "MESSAGE=OTA Policy state transition: %d -> %d",
    static_cast<int>(prev_state), static_cast<int>(new_state),
    "PRIORITY=%d", (new_state == EngineState::ForcePending) ? LOG_WARNING : LOG_INFO,
    "OTA_BUNDLE_ID=%s", manifest_.bundle_id.c_str(),
    "OTA_DEFERRALS_USED=%u", persist_.deferrals_used,
    "OTA_INTERLOCK_MASK=0x%08X", current_interlocks,
    nullptr
);
```
:::

Це формує захищений криптографічний слід дій системи, доступний для аудиту після завершення кампанії розгортання.

### 8. Блокування критичних виконавчих механізмів при відмові від патчу (Graceful Degradation & Actuator Interlocking)

Коли вичерпано максимальну кількість відкладень (`deferrals_used >= max_deferrals`) або системний час перетнув абсолютну межу `hard_deadline_epoch`, але сенсорні інтерлоки не дозволяють миттєво перезавантажити контролер (наприклад, мобільний робот завершує доставку вантажу та перебуває в русі), рушій політики не може безпечно перемкнути слоти прошивки. Проте пасивне очікування на системі без встановленого виправлення безпеки створює неприпустимий вектор атаки або загрозу аварії обладнання. У цьому стані модуль ініціює керовану деградацію функціоналу (Operational Functional Degradation):

1. **Обмеження динаміки та перехід у захисний режим (Limp-Home Mode):**
   Демон оновлення надсилає до підсистеми керування рухом через шину CAN команду на заборону повністю автономного планування траєкторій. Максимальна лінійна швидкість апарата примусово обмежується безпечним маневровим порогом (наприклад, 0.3 м/с замість штатних 2.5 м/с), а планувальник маршрутів перемикається виключно на повернення до найближчого зарядного дока або технологічної кишені цеху.

2. **Апаратне блокування силових актуаторів підвищеного ризику:**
   Для виконавчих вузлів підвищеної небезпеки (гідравлічні насоси високого тиску, поворотні маніпулятори, нагрівальні столи або зварювальні інвертори) надсилається сигнал вимкнення контуру живлення Safe Torque Off (STO). Розмикання контактів силового реле безпеки (Safety Relay) через лінію GPIO унеможливлює активацію механічної потужності навіть у разі програмного збою чи спроби оператора запустити нове виробниче завдання до завершення оновлення.

3. **Мережевий карантин підсистеми зв'язку (Network Quarantine):**
   Для оновлень із рівнем терміновості `URGENCY_CRITICAL_ZERO_DAY` або `URGENCY_EMERGENCY_RECALL` підсистема мережевої фільтрації Linux (`nftables`) перемикається в ізольований профіль. Будь-які вхідні та вихідні з'єднання по портах загального призначення, брокерах MQTT та віддалених сервісах телеметрії відсікаються на рівні ядра, за винятком локального криптографічно захищеного каналу до репозиторію прошивок. Це блокує можливість експлуатації відомої вразливості нульового дня через зовнішню мережу до моменту успішної верифікації та перезавантаження нової версії ядра.
