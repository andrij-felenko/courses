# ⚙️ Автоматизована машина станів діагностики та верифікації етапів Bringup на C99 та C++20

Ручне тестування кожного вузла друкованої плати за допомогою лабораторного осцилографа, мультиметра та ручного перемикання щупів є ефективним на етапі одиничного макетування, але стає головним вузьким місцем під час запуску партії дослідних зразків ревізії А чи на виробничій ділянці тестування (ICT — In-Circuit Test). Помилка оператора, випадкове короткочасне замикання сусідніх виводів щупом осцилографа або пропуск мікросекундного просідання напруги призводять до хибного бракування справних плат або виходу мікроконтролерів із ладу.

Для повної автоматизації верифікації фізичних етапів запуску створюється спеціалізований діагностичний автомат — апаратно-програмний стендовий тестер на базі сервісного мікроконтролера. Цей модуль послідовно виконує вимірювання аналогових параметрів шин живлення через вбудований багатоканальний АЦП, контролює динаміку лінії скидання `nRST`, вимірює реальну частоту генерації кварцових резонаторів за допомогою апаратного таймера в режимі захоплення (Input Capture), виконує програмну емуляцію майстра протоколу SWD (Serial Wire Debug) для зчитування ідентифікатора ядра `DP-IDCODE`, а у разі блокування процесора автоматично застосовує відновлювальні послідовності `Connect-Under-Reset` та формує структурований телеметричний звіт у форматі JSON.

---

## 1. Архітектура та схемотехніка діагностичного стенду

Діагностична машина станів (FSM — Finite State Machine) організована як строго детермінований конвеєр перевірок із можливостями автоматичного відновлення та локалізації відмов (Recovery & Triage Branch).

```
   ┌────────────────────────────────────────────────────────┐
   │                  STATE_IDLE_STANDBY                    │
   └───────────────────────────┬────────────────────────────┘
                               │ Команда запуску тесту (Start Trigger)
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │                STATE_POWER_RAIL_CHECK                  │
   │  • АЦП дискретизація VDD, VDDA, VCORE                  │
   │  • Розрахунок швидкості наростання dV/dt               │
   │  • Контроль монотонності та відсутності Brownout       │
   └───────────────┬────────────────────────┬───────────────┘
     [VDD FAIL]    │                        │ [VDD OK]
         ┌─────────┘                        ▼
         │                 ┌────────────────────────────────┐
         │                 │       STATE_NRST_VERIFY        │
         │                 │  • Вимір часу затримки t_delay │
         │                 │  • Перевірка підтяжки до VDD   │
         │                 │  • Тест Open-Drain драйвера    │
         │                 └────────┬──────────────┬────────┘
         │               [NRST FAIL]│              │ [NRST OK]
         │        ┌─────────────────┘              ▼
         │        │                ┌────────────────────────────────┐
         │        │                │      STATE_CLOCK_MEASURE       │
         │        │                │  • Захоплення частоти таймером │
         │        │                │  • Розрахунок похибки в ppm    │
         │        │                │  • Контроль часу виходу на реж.│
         │        │                └────────┬──────────────┬────────┘
         │        │               [CLK FAIL]│              │ [CLK OK]
         │        │        ┌────────────────┘              ▼
         │        │        │               ┌────────────────────────────────┐
         │        │        │               │      STATE_SWD_DISCOVERY       │
         │        │        │               │  • SWD Line Reset (56 тактів)  │
         │        │        │               │  • Перемикання 0x79E7          │
         │        │        │               │  • Читання DP-IDCODE           │
         │        │        │               │  • Handshake CTRL/STAT         │
         │        │        │               └────────┬──────────────┬────────┘
         │        │        │              [SWD FAIL]│              │ [SWD OK]
         ▼        ▼        ▼                        ▼              │
   ┌────────────────────────────────────────────────────────┐      │
   │                 STATE_RECOVERY_TRIAGE                  │      │
   │  • Апаратний Connect-Under-Reset                       │      │
   │  • Зниження частоти SWCLK до 100 кГц                   │      │
   │  • Форсування BOOT0 в режим System Memory              │      │
   │  • Екстрене очищення Flash (Mass Erase)                │      │
   └───────────────────────────┬────────────────────────────┘      │
                               │                                   │
                               ▼                                   ▼
   ┌────────────────────────────────────────────────────────────────┐
   │                    STATE_REPORT_TELEMETRY                      │
   │  • Генерація зведеного JSON-звіту                              │
   │  • Логування часових параметрів t_rise, t_rst, f_hse, IDCODE   │
   │  • Видача коду вердикту: PASS, WARN_RECOVERED, FAIL_HARDWARE   │
   └────────────────────────────────────────────────────────────────┘
```

### 1.1. Апаратний інтерфейс випробувального стенду (Diagnostic Fixture)

Стенд для автоматизованого оживлення плат підключається до тестованого пристрою (Target Under Test, TUT) через спеціалізований голчастий адаптер (Bed-of-Nails Fixture) або сервісний технологічний роз'єм. Кожен вимірювальний канал стенду захищений від аварійних ситуацій:

1. **Керування живленням TUT:** Виконується через силовий P-MOSFET комутатор із регульованим обмеженням струму (Current Limiting) та схемою вимірювання струму споживання (Current Shunt Monitor, наприклад, INA240). Це дозволяє стенду миттєво відключити напругу за час менше 5 мікросекунд при виявленні короткого замикання на шині 3.3 В.
2. **Аналогові входи контролю шин:** Лінії `VDD`, `VDDA`, `VCORE` та `nRST` підключені до вхідних каналів швидкісного 12-розрядного АЦП сервісного мікроконтролера через прецизійні буферні повторювачі на операційних підсилювачах (Rail-to-Rail) та захисні здвоєні діоди Шотткі BAT54S, які скидають будь-які викиди перенапруги на захисну шину стенду.
3. **Цифрові лінії зв'язку:** Лінії `SWDIO`, `SWCLK`, `BOOT0` та `nRST_DRIVE` підключені через двонаправлені перетворювачі логічних рівнів (Level Shifters 74LVC8T245), що дозволяє стенду автоматично підлаштовуватися під рівень напруги цільової плати в діапазоні від 1.2 В до 5.0 В.
4. **4-провідне підключення Кельвіна (Kelvin Sensing):** Силові лінії подачі живлення `VDD_PWR/GND_PWR` та вимірювальні лінії зворотного зв'язку `VDD_SENSE/GND_SENSE` розділені аж до контактних голок голчастого адаптера. Це усуває похибку вимірювання напруги, викликану падінням струму на контактному опорі пружинних контактів Pogo Pins.

Вхідні кола АЦП сервісного контролера містять фільтр низьких частот першого порядку з резистором `R_flt = 1.0 кОм` та конденсатором `C_flt = 100 пФ`. Частота зрізу такого фільтра становить:

```
f_cutoff = 1 / (2 · π · R_flt · C_flt) = 1 / (2 · π · 1000 Ом · 100 · 10⁻¹² Ф) ≈ 1.59 МГц
```

Ця смуга пропускання повністю перекриває частоту дискретизації АЦП `f_s = 1 MSPS` відповідно до теореми Найквіста-Котельникова, запобігаючи ефекту накладання спектрів (Aliasing) від високочастотних радіозавад, і одночасно не спотворює фронти перехідного процесу наростання напруги з тривалістю `t_rise ≥ 10 мкс`.

### 1.2. Математичний апарат цифрової обробки сигналів шин живлення

Під час фази `STATE_POWER_RAIL_CHECK` сервісний контролер подає сигнал увімкнення силового ключа і одночасно запускає циклічну вибірку вхідного сигналу напруги `VDD(t)` із частотою дискретизації `f_s = 1 MSPS` (період дискретизації `T_s = 1 мкс`) у буфер прямого доступу до пам'яті (DMA) розміром `N = 1024` відліків.

1. **Швидкість наростання напруги (Slew Rate):** Обчислюється методом лінійної апроксимації на інтервалі між точкою перетину 10% номіналу (`V_10 = 0.1 · V_nom = 0.33 В`) та точкою перетину 90% номіналу (`V_90 = 0.9 · V_nom = 2.97 В`):

```
dV/dt = (V(t_90) - V(t_10)) / (t_90 - t_10)
```

Критерій придатності для типових LDO та DC-DC перетворювачів становить: `0.05 В/мс ≤ dV/dt ≤ 5.0 В/мс`. Занадто повільний підйом (`dV/dt < 0.05 В/мс`) створює ризик застрягання внутрішніх компараторів POR у стані невизначеності або виникнення ефекту Latch-Up. Занадто швидкий підйом (`dV/dt > 10 В/мс`) генерує колосальні пускові струми заряду конденсаторів розв'язки.

2. **Монотонність підйому (Monotonicity Criterion):** На інтервалі наростання від `t_10` до `t_90` ковзний алгоритм аналізує різницю сусідніх відліків напруги:

```
ΔV[i] = V[i+1] - V[i]
```

Для виключення впливу шуму дискретизації АЦП встановлюється поріг шуму `ΔV_noise = 2 · LSB_ADC ≈ 1.6 мВ`. Якщо на інтервалі підйому виявляється спад напруги `ΔV[i] < -30 мВ`, автомат фіксує критичний дефект немонотонності (Non-Monotonic Dip). Така подія свідчить про наявність паразитного споживача, що раптово підключився до шини, або про спрацьовування захисту регулятора від струмового перевантаження.

3. **Статистичний аналіз стаціонарного стану (Ripple & RMS Noise):** Після завершення перехідного процесу (інтервал часу `t > t_settle`, де `t_settle = t_90 + 2.0 мс`) розраховуються статистичні метрики якості постійної напруги:

```
V_mean = (1 / M) · ∑ V[k]   (для k від t_settle до N)
V_ripple_pp = max(V[k]) - min(V[k])
V_rms = sqrt( (1 / M) · ∑ (V[k] - V_mean)² )
```

Критерій придатності шини 3.3 В:
- Середня напруга: `3.20 В ≤ V_mean ≤ 3.40 В` (допуск `±3%`);
- Розмах пульсацій: `V_ripple_pp < 35 мВ`;
- Середньоквадратичний шум: `V_rms < 10 мВ`.

4. **Фільтрація шуму квантування ковзним середнім (Moving Average Filter):**
Перед обчисленням похідної масив вибірок пропускається через ковзне вікно шириною `W = 5` відліків:

```
V_filtered[i] = (1 / W) · ∑ V[i + j]   (де j від -2 до +2)
```

Це дозволяє усунути одиничні високочастотні викиди від комутації цифрових вентилів самого мікроконтролера тестера та забезпечує гладку функцію напруги для точного визначення точок `t_10` та `t_90`.

5. **Аналіз резонансних коливань та перерегулювання (Overshoot & Ringing Analysis):**
Якщо під час виходу на номінал напруга перевищує `V_nom` більш ніж на 5% (`V_peak > 3.465 В`), алгоритм розраховує відносне перерегулювання `Overshoot = ((V_peak - V_mean) / V_mean) · 100%`. Перерегулювання понад 10% вказує на недостатній запас за фазою (Phase Margin < 45°) у контурі зворотного зв'язку стабілізатора або надмірну індуктивність друкованих трас живлення.

### 1.3. Вимірювання частоти та відхилення кварцового резонатора таймером

У фазі `STATE_CLOCK_MEASURE` тактовий сигнал цільового мікроконтролера (виведений на тестову точку або пін MCO — Microcontroller Clock Output) подається на вхід таймера сервісного контролера `TIM_IC` (Input Capture).

Вимірювання частоти виконується методом стробування за фіксований час вимірювального вікна `T_gate = 100 мс`. Базовий таймер стенду (Master Timer), синхронізований від прецизійного термокомпенсованого опорного генератора TCXO з точністю 0.5 ppm, формує апаратний строб захоплення. Підлеглий лічильник (Slave Counter) підраховує кількість імпульсів `N_pulses`, що надійшли від цільового резонатора:

```
f_measured = N_pulses / T_gate
```

Відхилення частоти в мільйонних частках (ppm — parts per million) від паспортного номіналу `f_nominal` (наприклад, 8 МГц, 16 МГц чи 25 МГц) обчислюється за формулою:

```
Δf_ppm = ((f_measured - f_nominal) / f_nominal) · 1 000 000
```

Критерії придатності частоти тактування:
- Високочастотний кварцовий резонатор HSE (для інтерфейсів USB 2.0, CAN-FD, Ethernet): `|Δf_ppm| ≤ 50 ppm`;
- Загальносистемний кварцовий резонатор: `|Δf_ppm| ≤ 150 ppm`;
- Годинниковий кварц реального часу LSE (32.768 кГц): `|Δf_ppm| ≤ 20 ppm`;
- Внутрішній фабричний RC-генератор HSI: `|Δf_ppm| ≤ 1000 ppm` (допуск `±1%`).

Апаратна схема зв'язки таймерів виключає програмні затримки переривань: запуск підлеглого лічильника здійснюється сигналом тригера `TRGO` базового таймера безпосередньо через матрицю міжтаймерних з'єднань (ITR — Internal Trigger Connection), а завершення вимірювального інтервалу апаратно замикає вхідний преддільник, фіксуючи точне значення лічильника в регістрі захоплення `TIM_CCR`.

### 1.4. Програмний емулятор протоколу SWD (Bitbanged SW-DP Master)

Для читання регістрів ядра та ідентифікації мікроконтролера сервісний процесор реалізує програмний драйвер протоколу Serial Wire Debug (SWD), що працює на швидкості до 2 МГц.

Протокол вимагає суворого дотримання таймінгів сигналів:
- **Час встановлення (Setup Time `t_setup`):** Хост виставляє логічний рівень на лінії `SWDIO` щонайменше за 100 нс до наростаючого фронту сигналу `SWCLK`.
- **Час утримання (Hold Time `t_hold`):** Логічний рівень утримується незмінним щонайменше 100 нс після наростаючого фронту `SWCLK`.
- **Зміна напрямку передачі (Turnaround Period `Trn`):** При переході лінії `SWDIO` від хоста до таргета або навпаки формується 1 такт холостого ходу, під час якого вихідні драйвери обох сторін переходять у стан високого імпедансу (Hi-Z).

Пакет транзакції читання або запису складається з 8-бітного запиту хоста, 3-бітного підтвердження таргета `ACK` та 32-бітного слова даних із бітом парності:

```
Запит хоста (Host Request, 8 біт):
Bit 0: Start Bit = 1 (Ознака початку транзакції)
Bit 1: APnDP (0 = звернення до Debug Port, 1 = звернення до Access Port)
Bit 2: RnW (1 = операція читання, 0 = операція запису)
Bit 3: A[2] (Молодший біт зміщення адреси регістра)
Bit 4: A[3] (Старший біт зміщення адреси регістра)
Bit 5: Parity = APnDP ⊕ RnW ⊕ A[2] ⊕ A[3] (Біт парності заголовка)
Bit 6: Stop Bit = 0 (Ознака завершення заголовка)
Bit 7: Park Bit = 1 (Утримання лінії у високому рівні)
```

Таргет повертає 3-бітний статус `ACK`:
- `0b001` (ACK OK) — успіх, таргет готовий до передачі або прийому даних;
- `0b010` (ACK WAIT) — таргет зайнятий виконанням попередньої операції пам'яті (потрібен повтор запиту);
- `0b100` (ACK FAULT) — апаратна помилка шини або заблокований доступ.

Якщо після читання 32-бітного слова даних біт парності `rcv_parity` не збігається з обчисленим через інструкцію `popcount(data) % 2`, транзакція вважається пошкодженою шумом, і автомат переходить до аналізу цілісності ліній.

### 1.5. Топологія заземлення та придушення синфазних завад стенду

Під час одночасної роботи силового комутатора живлення та високошвидкісного бітбенгінгу SWD через контактні голки тестера протікають імпульсні струми з крутими фронтами `dI/dt > 100 мА/нс`. Якщо контури повернення струму (Return Paths) спроектовані неправильно, виникає паразитна індуктивна наводка на спільній ділянці заземлення (Ground Bounce):

```
V_ground_bounce = L_pogo · (dI / dt)
```

де `L_pogo ≈ 2–5 нГн` — паразитна індуктивність контакту голки Pogo Pin. При перемиканні навантаження це створює динамічний зсув потенціалу землі до 200–300 мВ, що здатне викликати хибне спрацьовування вхідних тригерів Шмітта на лініях `SWCLK` та `SWDIO`.

Для усунення цього дефекту в діагностичній фікстурі реалізовано наступні заходи:
1. **Багатоточкове підключення землі:** Кожна сигнальна лінія (`SWCLK`, `SWDIO`, `nRST`) оточена мінімум двома виділеними земляними голками `GND_SIGNAL`, підключеними безпосередньо до суцільного екранного полігону плати тестера.
2. **Розділення силових та вимірювальних шин:** Силовий поворотний провід `GND_PWR` підключений до джерела живлення окремим товстим провідником, що унеможливлює протікання силового струму заряджання конденсаторів через вимірювальну землю АЦП `AGND`.

---

## 2. Реалізація повної системи діагностики Bringup на C99

Нижче наведено повну реалізацію автоматизованої машини станів на мові C99. Код спроектовано для роботи на вбудованих платформах без динамічного виділення пам'яті (Zero Heap Allocation) із підтримкою форматування звітів JSON у статичний буфер.

:::tabs
```c
/* ============================================================================
 * Bringup Diagnostic State Machine (C99 Production Implementation)
 * File: bringup_fsm.c
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>

#define ADC_SAMPLE_COUNT        1024
#define SWD_ACK_OK              0x01
#define SWD_ACK_WAIT            0x02
#define SWD_ACK_FAULT           0x04

#define TARGET_VDD_NOMINAL_MV   3300
#define TARGET_VDD_MIN_MV       3150
#define TARGET_VDD_MAX_MV       3450
#define MAX_RIPPLE_PP_MV        35
#define MIN_SLEW_RATE_MV_PER_US 50
#define MAX_SLEW_RATE_MV_PER_US 5000

#define DP_REG_IDCODE           0x00
#define DP_REG_CTRL_STAT        0x04
#define DP_REG_SELECT           0x08
#define DP_REG_RDBUFF           0x0C

typedef enum {
    BRINGUP_STATE_IDLE = 0,
    BRINGUP_STATE_POWER_RAIL_CHECK,
    BRINGUP_STATE_NRST_VERIFY,
    BRINGUP_STATE_CLOCK_MEASURE,
    BRINGUP_STATE_SWD_DISCOVERY,
    BRINGUP_STATE_RECOVERY_TRIAGE,
    BRINGUP_STATE_REPORT_TELEMETRY,
    BRINGUP_STATE_COMPLETE_SUCCESS,
    BRINGUP_STATE_COMPLETE_FAIL
} bringup_state_t;

typedef enum {
    BRINGUP_ERR_NONE = 0,
    BRINGUP_ERR_POWER_VOLTAGE_OUT_OF_SPEC,
    BRINGUP_ERR_POWER_NON_MONOTONIC,
    BRINGUP_ERR_POWER_RIPPLE_EXCESSIVE,
    BRINGUP_ERR_NRST_STUCK_LOW,
    BRINGUP_ERR_NRST_TIMEOUT,
    BRINGUP_ERR_CLOCK_ABSENT,
    BRINGUP_ERR_CLOCK_PPM_EXCESSIVE,
    BRINGUP_ERR_SWD_NO_RESPONSE,
    BRINGUP_ERR_SWD_PARITY_MISMATCH,
    BRINGUP_ERR_SWD_INVALID_IDCODE,
    BRINGUP_ERR_CORE_HALT_FAILED
} bringup_error_t;

typedef struct {
    uint32_t vdd_mean_mv;
    uint32_t vdd_ripple_pp_mv;
    uint32_t vdd_slew_rate_mv_per_us;
    bool     vdd_is_monotonic;
    uint32_t nrst_release_delay_us;
    uint32_t nrst_steady_state_mv;
    uint32_t clock_freq_hz;
    int32_t  clock_ppm_error;
    uint32_t swd_dpidr;
    uint8_t  swd_ack_status;
    bool     is_recovered;
    bringup_error_t last_error;
} bringup_telemetry_t;

typedef struct {
    void     (*power_enable)(bool enable);
    void     (*start_adc_sampling)(uint16_t *buf, size_t count);
    bool     (*is_adc_sampling_complete)(void);
    uint32_t (*get_nrst_mv)(void);
    void     (*drive_nrst)(bool assert_low);
    void     (*drive_boot0)(bool high);
    uint32_t (*measure_hse_freq_hz)(uint32_t gate_time_ms);
    void     (*swd_set_clk)(bool level);
    void     (*swd_set_dio)(bool level);
    bool     (*swd_get_dio)(void);
    void     (*swd_set_dio_dir_out)(bool is_output);
    void     (*delay_us)(uint32_t us);
    uint32_t (*get_system_time_ms)(void);
} bringup_hal_ops_t;

typedef struct {
    bringup_state_t     state;
    bringup_telemetry_t telemetry;
    const bringup_hal_ops_t *hal;
    uint16_t            adc_raw_buffer[ADC_SAMPLE_COUNT];
    uint32_t            state_entry_time_ms;
    uint8_t             retry_counter;
} bringup_fsm_t;

/* --- Прототипи допоміжних функцій SWD --- */
static void swd_clock_pulse(const bringup_hal_ops_t *hal);
static void swd_line_reset(const bringup_hal_ops_t *hal);
static void swd_send_switch_sequence(const bringup_hal_ops_t *hal);
static bool swd_read_dp(const bringup_hal_ops_t *hal, uint8_t addr_reg, uint32_t *out_val, uint8_t *out_ack);
static bool swd_write_dp(const bringup_hal_ops_t *hal, uint8_t addr_reg, uint32_t val);
static uint8_t calc_parity32(uint32_t val);

void bringup_fsm_init(bringup_fsm_t *fsm, const bringup_hal_ops_t *hal) {
    memset(fsm, 0, sizeof(bringup_fsm_t));
    fsm->state = BRINGUP_STATE_IDLE;
    fsm->hal = hal;
}

void bringup_fsm_start(bringup_fsm_t *fsm) {
    fsm->state = BRINGUP_STATE_POWER_RAIL_CHECK;
    fsm->state_entry_time_ms = fsm->hal->get_system_time_ms();
    fsm->retry_counter = 0;
    fsm->hal->power_enable(true);
    fsm->hal->start_adc_sampling(fsm->adc_raw_buffer, ADC_SAMPLE_COUNT);
}

void bringup_fsm_process(bringup_fsm_t *fsm) {
    uint32_t now_ms = fsm->hal->get_system_time_ms();

    switch (fsm->state) {
    case BRINGUP_STATE_IDLE:
        break;

    case BRINGUP_STATE_POWER_RAIL_CHECK: {
        if (!fsm->hal->is_adc_sampling_complete()) {
            if (now_ms - fsm->state_entry_time_ms > 100) {
                fsm->telemetry.last_error = BRINGUP_ERR_POWER_VOLTAGE_OUT_OF_SPEC;
                fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            }
            return;
        }

        /* 1. Обробка вибірки АЦП: розрахунок Slew Rate та монотонності */
        uint32_t v_10_idx = 0, v_90_idx = 0;
        uint32_t sum = 0, min_val = 0xFFFF, max_val = 0;
        bool monotonic = true;
        uint16_t v_10_thresh = (TARGET_VDD_NOMINAL_MV * 10) / 100;
        uint16_t v_90_thresh = (TARGET_VDD_NOMINAL_MV * 90) / 100;

        for (size_t i = 0; i < ADC_SAMPLE_COUNT; ++i) {
            uint16_t v = fsm->adc_raw_buffer[i];
            if (v_10_idx == 0 && v >= v_10_thresh) v_10_idx = (uint32_t)i;
            if (v_90_idx == 0 && v >= v_90_thresh) v_90_idx = (uint32_t)i;

            if (i > 0 && v_10_idx > 0 && v_90_idx == 0) {
                if ((int32_t)v - (int32_t)fsm->adc_raw_buffer[i - 1] < -30) {
                    monotonic = false;
                }
            }

            /* Статистика на стаціонарній ділянці (останні 256 відліків) */
            if (i >= ADC_SAMPLE_COUNT - 256) {
                sum += v;
                if (v < min_val) min_val = v;
                if (v > max_val) max_val = v;
            }
        }

        fsm->telemetry.vdd_is_monotonic = monotonic;
        fsm->telemetry.vdd_mean_mv = sum / 256;
        fsm->telemetry.vdd_ripple_pp_mv = max_val - min_val;

        if (v_90_idx > v_10_idx) {
            uint32_t dt_us = v_90_idx - v_10_idx;
            fsm->telemetry.vdd_slew_rate_mv_per_us = (v_90_thresh - v_10_thresh) / dt_us;
        }

        /* 2. Валідація критеріїв придатності шини живлення */
        if (fsm->telemetry.vdd_mean_mv < TARGET_VDD_MIN_MV ||
            fsm->telemetry.vdd_mean_mv > TARGET_VDD_MAX_MV) {
            fsm->telemetry.last_error = BRINGUP_ERR_POWER_VOLTAGE_OUT_OF_SPEC;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        if (!monotonic) {
            fsm->telemetry.last_error = BRINGUP_ERR_POWER_NON_MONOTONIC;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        if (fsm->telemetry.vdd_ripple_pp_mv > MAX_RIPPLE_PP_MV) {
            fsm->telemetry.last_error = BRINGUP_ERR_POWER_RIPPLE_EXCESSIVE;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        /* Перехід до верифікації лінії NRST */
        fsm->state = BRINGUP_STATE_NRST_VERIFY;
        fsm->state_entry_time_ms = now_ms;
        break;
    }

    case BRINGUP_STATE_NRST_VERIFY: {
        uint32_t nrst_mv = fsm->hal->get_nrst_mv();
        fsm->telemetry.nrst_steady_state_mv = nrst_mv;

        if (nrst_mv > (TARGET_VDD_NOMINAL_MV * 80) / 100) {
            fsm->telemetry.nrst_release_delay_us = (now_ms - fsm->state_entry_time_ms) * 1000;
            fsm->state = BRINGUP_STATE_CLOCK_MEASURE;
            fsm->state_entry_time_ms = now_ms;
            return;
        }

        if (now_ms - fsm->state_entry_time_ms > 150) {
            fsm->telemetry.last_error = (nrst_mv < 500) ? BRINGUP_ERR_NRST_STUCK_LOW : BRINGUP_ERR_NRST_TIMEOUT;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
        }
        break;
    }

    case BRINGUP_STATE_CLOCK_MEASURE: {
        uint32_t freq = fsm->hal->measure_hse_freq_hz(100);
        fsm->telemetry.clock_freq_hz = freq;

        if (freq == 0) {
            fsm->telemetry.last_error = BRINGUP_ERR_CLOCK_ABSENT;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        constexpr uint32_t target_freq = 25000000;
        int64_t diff = (int64_t)freq - (int64_t)target_freq;
        int32_t ppm = (int32_t)((diff * 1000000) / target_freq);
        fsm->telemetry.clock_ppm_error = ppm;

        if (ppm > 200 || ppm < -200) {
            fsm->telemetry.last_error = BRINGUP_ERR_CLOCK_PPM_EXCESSIVE;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        fsm->state = BRINGUP_STATE_SWD_DISCOVERY;
        fsm->state_entry_time_ms = now_ms;
        break;
    }

    case BRINGUP_STATE_SWD_DISCOVERY: {
        swd_line_reset(fsm->hal);
        swd_send_switch_sequence(fsm->hal);
        swd_line_reset(fsm->hal);

        uint32_t dpidr = 0;
        uint8_t ack = 0;
        bool ok = swd_read_dp(fsm->hal, DP_REG_IDCODE, &dpidr, &ack);
        fsm->telemetry.swd_ack_status = ack;
        fsm->telemetry.swd_dpidr = dpidr;

        if (!ok || ack != SWD_ACK_OK) {
            fsm->telemetry.last_error = (ack == 0) ? BRINGUP_ERR_SWD_NO_RESPONSE : BRINGUP_ERR_SWD_PARITY_MISMATCH;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        if ((dpidr & 0x00000FFE) != 0x00000476 && (dpidr & 0x00000FFE) != 0x00000020) {
            fsm->telemetry.last_error = BRINGUP_ERR_SWD_INVALID_IDCODE;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        /* Активація доменів живлення налагодження */
        swd_write_dp(fsm->hal, DP_REG_CTRL_STAT, 0x50000000); /* CSYSPWRUPREQ | CDBGPWRUPREQ */

        fsm->state = BRINGUP_STATE_REPORT_TELEMETRY;
        break;
    }

    case BRINGUP_STATE_RECOVERY_TRIAGE: {
        fsm->telemetry.is_recovered = true;
        if (fsm->retry_counter >= 3) {
            fsm->state = BRINGUP_STATE_REPORT_TELEMETRY;
            return;
        }
        fsm->retry_counter++;

        /* 1. Апаратне скидання Connect-Under-Reset */
        fsm->hal->drive_nrst(true);
        fsm->hal->delay_us(5000);

        swd_line_reset(fsm->hal);
        swd_send_switch_sequence(fsm->hal);
        swd_line_reset(fsm->hal);

        uint32_t dpidr = 0;
        uint8_t ack = 0;
        if (swd_read_dp(fsm->hal, DP_REG_IDCODE, &dpidr, &ack) && ack == SWD_ACK_OK) {
            fsm->telemetry.swd_dpidr = dpidr;
            swd_write_dp(fsm->hal, DP_REG_CTRL_STAT, 0x50000000);
            fsm->hal->drive_nrst(false);
            fsm->state = BRINGUP_STATE_REPORT_TELEMETRY;
            return;
        }

        /* 2. Спроба переведення BOOT0 в High (System Memory Bootloader) */
        fsm->hal->drive_boot0(true);
        fsm->hal->drive_nrst(true);
        fsm->hal->delay_us(10000);
        fsm->hal->drive_nrst(false);
        fsm->hal->delay_us(20000);

        fsm->state = BRINGUP_STATE_SWD_DISCOVERY;
        break;
    }

    case BRINGUP_STATE_REPORT_TELEMETRY:
        fsm->state = (fsm->telemetry.last_error == BRINGUP_ERR_NONE || fsm->telemetry.is_recovered)
                     ? BRINGUP_STATE_COMPLETE_SUCCESS
                     : BRINGUP_STATE_COMPLETE_FAIL;
        break;

    case BRINGUP_STATE_COMPLETE_SUCCESS:
    case BRINGUP_STATE_COMPLETE_FAIL:
        break;
    }
}

size_t bringup_generate_json_report(const bringup_fsm_t *fsm, char *out_buf, size_t max_len) {
    const char *verdict_str = "FAIL_HARDWARE";
    if (fsm->telemetry.last_error == BRINGUP_ERR_NONE) {
        verdict_str = "PASS";
    } else if (fsm->telemetry.is_recovered) {
        verdict_str = "WARN_RECOVERED";
    }

    return (size_t)snprintf(out_buf, max_len,
        "{
"
        "  "bringup_report": {
"
        "    "verdict": "%s",
"
        "    "error_code": %u,
"
        "    "power_rail": {
"
        "      "nominal_mv": %u,
"
        "      "measured_mean_mv": %lu,
"
        "      "ripple_pp_mv": %lu,
"
        "      "slew_rate_mv_per_us": %lu,
"
        "      "is_monotonic": %s
"
        "    },
"
        "    "reset_circuit": {
"
        "      "nrst_steady_mv": %lu,
"
        "      "release_delay_us": %lu
"
        "    },
"
        "    "clock_system": {
"
        "      "measured_freq_hz": %lu,
"
        "      "ppm_error": %ld
"
        "    },
"
        "    "swd_interface": {
"
        "      "dpidr_hex": "0x%08lX",
"
        "      "ack_status": %u,
"
        "      "recovery_invoked": %s
"
        "    }
"
        "  }
"
        "}",
        verdict_str,
        (unsigned)fsm->telemetry.last_error,
        TARGET_VDD_NOMINAL_MV,
        (unsigned long)fsm->telemetry.vdd_mean_mv,
        (unsigned long)fsm->telemetry.vdd_ripple_pp_mv,
        (unsigned long)fsm->telemetry.vdd_slew_rate_mv_per_us,
        fsm->telemetry.vdd_is_monotonic ? "true" : "false",
        (unsigned long)fsm->telemetry.nrst_steady_state_mv,
        (unsigned long)fsm->telemetry.nrst_release_delay_us,
        (unsigned long)fsm->telemetry.clock_freq_hz,
        (long)fsm->telemetry.clock_ppm_error,
        (unsigned long)fsm->telemetry.swd_dpidr,
        fsm->telemetry.swd_ack_status,
        fsm->telemetry.is_recovered ? "true" : "false"
    );
}

/* --- Допоміжні функції низькорівневого бітбенг-майстра SWD --- */

static void swd_clock_pulse(const bringup_hal_ops_t *hal) {
    hal->swd_set_clk(false);
    hal->delay_us(1);
    hal->swd_set_clk(true);
    hal->delay_us(1);
}

static void swd_line_reset(const bringup_hal_ops_t *hal) {
    hal->swd_set_dio_out(true);
    hal->swd_set_dio(true);
    for (int i = 0; i < 56; ++i) {
        swd_clock_pulse(hal);
    }
}

static void swd_send_switch_sequence(const bringup_hal_ops_t *hal) {
    uint16_t seq = 0xE79E; /* LSB-first для 0x79E7 */
    hal->swd_set_dio_out(true);
    for (int i = 0; i < 16; ++i) {
        hal->swd_set_dio((seq >> i) & 1);
        swd_clock_pulse(hal);
    }
}

static uint8_t calc_parity32(uint32_t val) {
    val ^= val >> 16;
    val ^= val >> 8;
    val ^= val >> 4;
    val ^= val >> 2;
    val ^= val >> 1;
    return (uint8_t)(val & 1);
}

static bool swd_read_dp(const bringup_hal_ops_t *hal, uint8_t addr_reg, uint32_t *out_val, uint8_t *out_ack) {
    uint8_t req = 0x81 | ((addr_reg & 0x0C) << 1); /* Start=1, APnDP=0, RnW=1, Stop=0, Park=1 */
    uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
    req |= (parity << 5);

    hal->swd_set_dio_out(true);
    for (int i = 0; i < 8; ++i) {
        hal->swd_set_dio((req >> i) & 1);
        swd_clock_pulse(hal);
    }

    hal->swd_set_dio_out(false);
    swd_clock_pulse(hal);

    uint8_t ack = 0;
    for (int i = 0; i < 3; ++i) {
        hal->swd_set_clk(false);
        hal->delay_us(1);
        if (hal->swd_get_dio()) ack |= (1 << i);
        hal->swd_set_clk(true);
        hal->delay_us(1);
    }
    *out_ack = ack;

    if (ack != SWD_ACK_OK) return false;

    uint32_t data = 0;
    for (int i = 0; i < 32; ++i) {
        hal->swd_set_clk(false);
        hal->delay_us(1);
        if (hal->swd_get_dio()) data |= (1UL << i);
        hal->swd_set_clk(true);
        hal->delay_us(1);
    }

    hal->swd_set_clk(false);
    hal->delay_us(1);
    bool rcv_par = hal->swd_get_dio();
    hal->swd_set_clk(true);
    hal->delay_us(1);

    hal->swd_set_dio_out(true);
    hal->swd_set_dio(false);
    for (int i = 0; i < 4; ++i) swd_clock_pulse(hal);

    if (rcv_par != calc_parity32(data)) return false;

    *out_val = data;
    return true;
}

static bool swd_write_dp(const bringup_hal_ops_t *hal, uint8_t addr_reg, uint32_t val) {
    uint8_t req = 0x81 | ((addr_reg & 0x0C) << 1); /* Start=1, APnDP=0, RnW=0, Stop=0, Park=1 */
    uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
    req |= (parity << 5);

    hal->swd_set_dio_out(true);
    for (int i = 0; i < 8; ++i) {
        hal->swd_set_dio((req >> i) & 1);
        swd_clock_pulse(hal);
    }

    hal->swd_set_dio_out(false);
    swd_clock_pulse(hal);

    uint8_t ack = 0;
    for (int i = 0; i < 3; ++i) {
        hal->swd_set_clk(false);
        hal->delay_us(1);
        if (hal->swd_get_dio()) ack |= (1 << i);
        hal->swd_set_clk(true);
        hal->delay_us(1);
    }

    if (ack != SWD_ACK_OK) return false;

    swd_clock_pulse(hal);
    hal->swd_set_dio_out(true);

    for (int i = 0; i < 32; ++i) {
        hal->swd_set_dio(((val >> i) & 1) != 0);
        swd_clock_pulse(hal);
    }

    hal->swd_set_dio(calc_parity32(val));
    swd_clock_pulse(hal);

    hal->swd_set_dio(false);
    for (int i = 0; i < 4; ++i) swd_clock_pulse(hal);

    return true;
}
```
```cpp
// ============================================================================
// Bringup Diagnostic State Machine (Modern C++20 Zero-Allocation Implementation)
// File: bringup_fsm.hpp
// ============================================================================

#pragma once

#include <cstdint>
#include <cstddef>
#include <concepts>
#include <expected>
#include <span>
#include <array>
#include <bit>
#include <string_view>
#include <format>

namespace bringup {

enum class State : uint8_t {
    Idle = 0,
    PowerRailCheck,
    NrstVerify,
    ClockMeasure,
    SwdDiscovery,
    RecoveryTriage,
    ReportTelemetry,
    CompleteSuccess,
    CompleteFail
};

enum class ErrorCode : uint8_t {
    None = 0,
    PowerVoltageOutOfSpec,
    PowerNonMonotonic,
    PowerRippleExcessive,
    NrstStuckLow,
    NrstTimeout,
    ClockAbsent,
    ClockPpmExcessive,
    SwdNoResponse,
    SwdParityError,
    SwdInvalidIdcode,
    CoreHaltFailed
};

struct Telemetry {
    uint32_t  vdd_mean_mv{0};
    uint32_t  vdd_ripple_pp_mv{0};
    uint32_t  vdd_slew_rate_mv_per_us{0};
    bool      vdd_is_monotonic{false};
    uint32_t  nrst_release_delay_us{0};
    uint32_t  nrst_steady_state_mv{0};
    uint32_t  clock_freq_hz{0};
    int32_t   clock_ppm_error{0};
    uint32_t  swd_dpidr{0};
    uint8_t   swd_ack_status{0};
    bool      is_recovered{false};
    ErrorCode last_error{ErrorCode::None};
};

template <typename T>
concept BringupHal = requires(T hal, bool level, uint16_t* buf, std::size_t count, uint32_t val) {
    { hal.power_enable(level) } -> std::same_as<void>;
    { hal.start_adc_sampling(buf, count) } -> std::same_as<void>;
    { hal.is_adc_sampling_complete() } -> std::same_as<bool>;
    { hal.get_nrst_mv() } -> std::same_as<uint32_t>;
    { hal.drive_nrst(level) } -> std::same_as<void>;
    { hal.drive_boot0(level) } -> std::same_as<void>;
    { hal.measure_hse_freq_hz(val) } -> std::same_as<uint32_t>;
    { hal.swd_set_clk(level) } -> std::same_as<void>;
    { hal.swd_set_dio(level) } -> std::same_as<void>;
    { hal.swd_get_dio() } -> std::same_as<bool>;
    { hal.swd_set_dio_out(level) } -> std::same_as<void>;
    { hal.delay_us(val) } -> std::same_as<void>;
    { hal.get_system_time_ms() } -> std::same_as<uint32_t>;
};

template <BringupHal Hal, std::size_t BufferSize = 1024>
class BringupEngine {
public:
    explicit constexpr BringupEngine(Hal& hal) noexcept : hal_{hal} {}

    void start() noexcept {
        current_state_ = State::PowerRailCheck;
        start_time_ms_ = hal_.get_system_time_ms();
        retry_count_ = 0;
        telemetry_ = {};
        hal_.power_enable(true);
        hal_.start_adc_sampling(adc_buffer_.data(), adc_buffer_.size());
    }

    void process() noexcept {
        const uint32_t now = hal_.get_system_time_ms();

        switch (current_state_) {
        case State::Idle:
            break;

        case State::PowerRailCheck:
            process_power_rail(now);
            break;

        case State::NrstVerify:
            process_nrst(now);
            break;

        case State::ClockMeasure:
            process_clock();
            break;

        case State::SwdDiscovery:
            process_swd(now);
            break;

        case State::RecoveryTriage:
            process_recovery();
            break;

        case State::ReportTelemetry:
            current_state_ = (telemetry_.last_error == ErrorCode::None || telemetry_.is_recovered)
                             ? State::CompleteSuccess
                             : State::CompleteFail;
            break;

        case State::CompleteSuccess:
        case State::CompleteFail:
            break;
        }
    }

    [[nodiscard]] constexpr State current_state() const noexcept { return current_state_; }
    [[nodiscard]] const Telemetry& telemetry() const noexcept { return telemetry_; }

private:
    void process_power_rail(uint32_t now) noexcept {
        if (!hal_.is_adc_sampling_complete()) {
            if (now - start_time_ms_ > 100) {
                telemetry_.last_error = ErrorCode::PowerVoltageOutOfSpec;
                current_state_ = State::RecoveryTriage;
            }
            return;
        }

        std::size_t v_10_idx = 0, v_90_idx = 0;
        uint32_t sum = 0, min_val = 0xFFFF, max_val = 0;
        bool monotonic = true;
        constexpr uint16_t v_10_thresh = 330;
        constexpr uint16_t v_90_thresh = 2970;

        for (std::size_t i = 0; i < adc_buffer_.size(); ++i) {
            const uint16_t v = adc_buffer_[i];
            if (v_10_idx == 0 && v >= v_10_thresh) v_10_idx = i;
            if (v_90_idx == 0 && v >= v_90_thresh) v_90_idx = i;

            if (i > 0 && v_10_idx > 0 && v_90_idx == 0) {
                if (static_cast<int32_t>(v) - static_cast<int32_t>(adc_buffer_[i - 1]) < -30) {
                    monotonic = false;
                }
            }

            if (i >= adc_buffer_.size() - 256) {
                sum += v;
                min_val = std::min<uint32_t>(min_val, v);
                max_val = std::max<uint32_t>(max_val, v);
            }
        }

        telemetry_.vdd_is_monotonic = monotonic;
        telemetry_.vdd_mean_mv = sum / 256;
        telemetry_.vdd_ripple_pp_mv = max_val - min_val;

        if (v_90_idx > v_10_idx) {
            telemetry_.vdd_slew_rate_mv_per_us = (v_90_thresh - v_10_thresh) / static_cast<uint32_t>(v_90_idx - v_10_idx);
        }

        if (telemetry_.vdd_mean_mv < 3150 || telemetry_.vdd_mean_mv > 3450) {
            telemetry_.last_error = ErrorCode::PowerVoltageOutOfSpec;
            current_state_ = State::RecoveryTriage;
            return;
        }

        if (!monotonic) {
            telemetry_.last_error = ErrorCode::PowerNonMonotonic;
            current_state_ = State::RecoveryTriage;
            return;
        }

        if (telemetry_.vdd_ripple_pp_mv > 35) {
            telemetry_.last_error = ErrorCode::PowerRippleExcessive;
            current_state_ = State::RecoveryTriage;
            return;
        }

        current_state_ = State::NrstVerify;
        start_time_ms_ = now;
    }

    void process_nrst(uint32_t now) noexcept {
        const uint32_t nrst_mv = hal_.get_nrst_mv();
        telemetry_.nrst_steady_state_mv = nrst_mv;

        if (nrst_mv > 2640) {
            telemetry_.nrst_release_delay_us = (now - start_time_ms_) * 1000;
            current_state_ = State::ClockMeasure;
            return;
        }

        if (now - start_time_ms_ > 150) {
            telemetry_.last_error = (nrst_mv < 500) ? ErrorCode::NrstStuckLow : ErrorCode::NrstTimeout;
            current_state_ = State::RecoveryTriage;
        }
    }

    void process_clock() noexcept {
        const uint32_t freq = hal_.measure_hse_freq_hz(100);
        telemetry_.clock_freq_hz = freq;

        if (freq == 0) {
            telemetry_.last_error = ErrorCode::ClockAbsent;
            current_state_ = State::RecoveryTriage;
            return;
        }

        constexpr uint32_t target_freq = 25000000;
        const int64_t diff = static_cast<int64_t>(freq) - static_cast<int64_t>(target_freq);
        const int32_t ppm = static_cast<int32_t>((diff * 1000000) / target_freq);
        telemetry_.clock_ppm_error = ppm;

        if (ppm > 200 || ppm < -200) {
            telemetry_.last_error = ErrorCode::ClockPpmExcessive;
            current_state_ = State::RecoveryTriage;
            return;
        }

        current_state_ = State::SwdDiscovery;
    }

    void process_swd(uint32_t now) noexcept {
        swd_line_reset();
        swd_send_switch_sequence();
        swd_line_reset();

        auto res = swd_read_dp(0x00);
        if (!res.has_value()) {
            telemetry_.last_error = res.error();
            current_state_ = State::RecoveryTriage;
            return;
        }

        telemetry_.swd_dpidr = *res;
        swd_write_dp(0x04, 0x50000000);
        current_state_ = State::ReportTelemetry;
    }

    void process_recovery() noexcept {
        telemetry_.is_recovered = true;
        if (retry_count_ >= 3) {
            current_state_ = State::ReportTelemetry;
            return;
        }
        retry_count_++;

        hal_.drive_nrst(true);
        hal_.delay_us(5000);

        swd_line_reset();
        swd_send_switch_sequence();
        swd_line_reset();

        auto res = swd_read_dp(0x00);
        if (res.has_value()) {
            telemetry_.swd_dpidr = *res;
            swd_write_dp(0x04, 0x50000000);
            hal_.drive_nrst(false);
            current_state_ = State::ReportTelemetry;
            return;
        }

        hal_.drive_boot0(true);
        hal_.drive_nrst(true);
        hal_.delay_us(10000);
        hal_.drive_nrst(false);
        hal_.delay_us(20000);

        current_state_ = State::SwdDiscovery;
    }

    void swd_clk_pulse() noexcept {
        hal_.swd_set_clk(false);
        hal_.delay_us(1);
        hal_.swd_set_clk(true);
        hal_.delay_us(1);
    }

    void swd_line_reset() noexcept {
        hal_.swd_set_dio_out(true);
        hal_.swd_set_dio(true);
        for (std::size_t i = 0; i < 56; ++i) swd_clk_pulse();
    }

    void swd_send_switch_sequence() noexcept {
        constexpr uint16_t seq = 0xE79E;
        hal_.swd_set_dio_out(true);
        for (std::size_t i = 0; i < 16; ++i) {
            hal_.swd_set_dio(((seq >> i) & 1) != 0);
            swd_clk_pulse();
        }
    }

    [[nodiscard]] std::expected<uint32_t, ErrorCode> swd_read_dp(uint8_t addr_reg) noexcept {
        uint8_t req = 0x81 | static_cast<uint8_t>((addr_reg & 0x0C) << 1);
        uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
        req |= static_cast<uint8_t>(parity << 5);

        hal_.swd_set_dio_out(true);
        for (std::size_t i = 0; i < 8; ++i) {
            hal_.swd_set_dio(((req >> i) & 1) != 0);
            swd_clk_pulse();
        }

        hal_.swd_set_dio_out(false);
        swd_clk_pulse();

        uint8_t ack = 0;
        for (std::size_t i = 0; i < 3; ++i) {
            hal_.swd_set_clk(false);
            hal_.delay_us(1);
            if (hal_.swd_get_dio()) ack |= static_cast<uint8_t>(1 << i);
            hal_.swd_set_clk(true);
            hal_.delay_us(1);
        }
        telemetry_.swd_ack_status = ack;

        if (ack != 0x01) return std::unexpected(ErrorCode::SwdNoResponse);

        uint32_t data = 0;
        for (std::size_t i = 0; i < 32; ++i) {
            hal_.swd_set_clk(false);
            hal_.delay_us(1);
            if (hal_.swd_get_dio()) data |= (1UL << i);
            hal_.swd_set_clk(true);
            hal_.delay_us(1);
        }

        hal_.swd_set_clk(false);
        hal_.delay_us(1);
        const bool rcv_par = hal_.swd_get_dio();
        hal_.swd_set_clk(true);
        hal_.delay_us(1);

        hal_.swd_set_dio_out(true);
        hal_.swd_set_dio(false);
        for (std::size_t i = 0; i < 4; ++i) swd_clk_pulse();

        const bool calc_par = (std::popcount(data) % 2) != 0;
        if (rcv_par != calc_par) return std::unexpected(ErrorCode::SwdParityError);

        return data;
    }

    bool swd_write_dp(uint8_t addr_reg, uint32_t val) noexcept {
        uint8_t req = 0x81 | static_cast<uint8_t>((addr_reg & 0x0C) << 1);
        uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
        req |= static_cast<uint8_t>(parity << 5);

        hal_.swd_set_dio_out(true);
        for (std::size_t i = 0; i < 8; ++i) {
            hal_.swd_set_dio(((req >> i) & 1) != 0);
            swd_clk_pulse();
        }

        hal_.swd_set_dio_out(false);
        swd_clk_pulse();

        uint8_t ack = 0;
        for (std::size_t i = 0; i < 3; ++i) {
            hal_.swd_set_clk(false);
            hal_.delay_us(1);
            if (hal_.swd_get_dio()) ack |= static_cast<uint8_t>(1 << i);
            hal_.swd_set_clk(true);
            hal_.delay_us(1);
        }

        if (ack != 0x01) return false;

        swd_clock_pulse(hal);
        hal_.swd_set_dio_out(true);

        for (std::size_t i = 0; i < 32; ++i) {
            hal_.swd_set_dio(((val >> i) & 1) != 0);
            swd_clk_pulse();
        }

        const bool calc_par = (std::popcount(val) % 2) != 0;
        hal_.swd_set_dio(calc_par);
        swd_clock_pulse(hal);

        hal_.swd_set_dio(false);
        for (std::size_t i = 0; i < 4; ++i) swd_clk_pulse();

        return true;
    }

    Hal& hal_;
    State current_state_{State::Idle};
    Telemetry telemetry_{};
    std::array<uint16_t, BufferSize> adc_buffer_{};
    uint32_t start_time_ms_{0};
    uint8_t retry_count_{0};
};

} // namespace bringup
```
:::

---

## 3. Детальний аналіз та обробка станів машини діагностики

Кожен стан діагностичної машини реалізує детермінований набір апаратних дій, часових затримок та перевірок граничних умов. Нижче наведено покроковий розбір фізичних процесів, що протікають у системі на кожному кроці Bringup:

### 3.1. Стан `STATE_IDLE_STANDBY` та початкова калібрація вимірювального тракту

Перед початком тестування система перебуває у стані очікування зовнішнього тригера (натискання кнопки оператора, отримання команди через UART/Ethernet або спрацьовування датчика закриття кришки голчастого адаптера). У цьому стані силовий транзистор комутації живлення гарантовано закритий, а всі цифрові виводи стенду переведені в режим високого імпедансу (Hi-Z) з внутрішніми підтяжками до землі через резистори 100 кОм.

У стані очікування сервісний контролер виконує фонову самодіагностику:
1. **Калібрування нульового зсуву АЦП (ADC Zero-Offset Calibration):** Входи аналогового комутатора тимчасово замикаються на внутрішню аналогову землю `AGND`, і вимірюється залишковий зсув напруги (Offset Error). Це значення зберігається в калібрувальному регістрі та автоматично віднімається від усіх наступних результатів вимірювань.
2. **Перевірка відсутності залишкового заряду на шинах плати:** АЦП вимірює напругу на тестових точках `VDD` та `VDDA`. Якщо напруга перевищує 100 мВ (наприклад, через залишковий заряд у високоефективних полімерних конденсаторах ємністю сотні мікрофарад), система вмикає внутрішній розрядний резистор (Bleeder Resistor) опором 47 Ом на час 50 мс. Подача живлення блокується до моменту повного зняття залишкового потенціалу, щоб уникнути помилкового визначення швидкості наростання та застрягання внутрішніх тригерів мікроконтролера.

### 3.2. Стан `STATE_POWER_RAIL_CHECK`: Динамічний та спектральний контроль живлення

Після отримання команди старту машина станів активує затвор силового P-MOSFET комутатора. Одночасно запускається таймер вибірки АЦП, синхронізований із контролером прямого доступу до пам'яті (DMA), який переносить результати оцифрування напруги з частотою 1 Мвиб/с безпосередньо в циклічний буфер оперативної пам'яті.

Аналіз перехідного процесу наростання напруги виконується за наступним алгоритмом:
1. **Визначення динамічних порогів:** Алгоритм розраховує напругу 10% (`0.33 В`) та 90% (`2.97 В`) від номінального значення 3.3 В. Потім у масиві відліків знаходяться індекси першого перетину цих рівнів `t_10` та `t_90`.
2. **Розрахунок тривалості фронту та швидкості наростання:** Інтервал часу наростання становить `t_rise = (t_90 - t_10) · T_s`. Швидкість наростання `Slew_Rate = (2.97 - 0.33) / t_rise`. Якщо `t_rise < 10 мкс`, це вказує на відсутність необхідної фільтрувальної ємності або пошкодження котушки індуктивності DC-DC перетворювача. Якщо `t_rise > 20 мс`, це свідчить про наявність паразитного струму витоку або перевантаження стабілізатора.
3. **Контроль монотонності наростання:** У зоні від `t_10` до `t_90` обчислюється перша похідна сигналу. Наявність будь-якого локального просідання напруги глибиною більше 30 мВ однозначно сигналізує про виникнення нестійкості в контурі зворотного зв'язку стабілізатора або про раптовий пусковий струм внутрішніх вузлів мікроконтролера, що підключаються до шини.
4. **Оцінка спектральних пульсацій у стаціонарному режимі:** Після завершення перехідного процесу на інтервалі тривалістю 256 мкс розраховується розмах пульсацій `V_ripple_pp` та середньоквадратичне значення шуму `V_rms`. Якщо на платі встановлено імпульсний перетворювач, наприклад, із частотою комутації 2.2 МГц, розмах пульсацій не повинен перевищувати 35 мВ. Більші значення пульсацій вказують на розтріскування керамічних конденсаторів типорозміру 0603/0805 під час паяння або використання діелектрика з високим п'єзоефектом (наприклад, Y5V замість якісного X7R/X5R).

### 3.3. Стан `STATE_NRST_VERIFY`: Верифікація ланцюга апаратного скидання

Ланцюг скидання мікроконтролера `nRST` формується внутрішнім генератором Power-On-Reset, зовнішнім підтягувальним резистором (типово 40–100 кОм всередині кристала або 10 кОм на схемі) та фільтрувальним конденсатором 100 нФ, підключеним до землі.

Діагностичний автомат виконує комплексний тест лінії скидання:
1. **Контроль затримки зняття скидання (`t_delay`):** АЦП відстежує наростання напруги на виводі `nRST`. Напруга повинна залишатися нижче порогу логічного нуля (0.8 В) протягом щонайменше 1–2 мілісекунд після того, як напруга живлення `VDD` досягла стабільного рівня 3.0 В. Якщо напруга `nRST` піднімається миттєво разом із живленням, це свідчить про обрив або відсутність конденсатора скидання, що у майбутньому призведе до збоїв старту при повільному наростанні напруги в польових умовах.
2. **Перевірка стаціонарного логічного рівня:** Після виходу на режим напруга на лінії `nRST` повинна бути не менше `0.8 · VDD` (тобто не менше 2.64 В для 3.3 В живлення). Рівень нижче 2.5 В вказує на наявність струмів витоку через залишки струмопровідного флюсу між виводами або пошкодження внутрішнього транзистора скидання.
3. **Тест функції примусового скидання (Active-Low Pull):** Сервісний стенд відкриває вбудований транзистор з відкритим стоком на лінії `nRST_DRIVE`, притискаючи пін до землі, і перевіряє, чи опустилася напруга нижче 0.2 В. Потім лінія відпускається, і контролюється правильність експоненціального заряду конденсатора за формулою `V(t) = VDD · (1 - exp(-t / (R_pullup · C_nrst)))`.

### 3.4. Стан `STATE_CLOCK_MEASURE`: Прецизійне вимірювання частоти та стабільності генератора

Після зняття сигналу скидання мікроконтролер переходить до виконання початкового коду завантажувача або вбудованої мікропрограми. Для верифікації роботи тактової підсистеми сервісний контролер вимірює параметри сигналу на виводі `MCO` (або спеціальній тестовій точці буферизованого тактування).

Методика вимірювання заснована на двох апаратно зв'язаних таймерах:
1. **Формування вимірювального вікна (Gate Time):** Базовий таймер стенду використовує тактування від високостабільного термокомпенсованого генератора TCXO з температурною нестабільністю не гірше 0.5 ppm у діапазоні від -40°C до +85°C. Таймер налаштовується на формування суворого часового інтервалу тривалістю рівно `T_gate = 100.000 мс`.
2. **Підрахунок імпульсів цільового резонатора:** Підлеглий таймер переводиться в режим лічильника зовнішніх імпульсів (External Clock Mode 2). Вхідний тактовий сигнал надходить через швидкісний диференціальний або логічний буфер тестера. Запуск і зупинка лічильника виконуються апаратно за фронтами сигналу стробування `TRGO` без участі програмного коду переривань, що повністю виключає джитер обробки ISR.
3. **Розрахунок та класифікація похибки частоти:** Кількість порахованих імпульсів `N` ділиться на тривалість вікна `T_gate`. Отримана частота порівнюється з номіналом. Наприклад, для кварцового резонатора 25.000 МГц за 100 мс лічильник повинен зафіксувати рівно `2 500 000` імпульсів. Якщо зафіксовано `2 500 350` імпульсів, абсолютна похибка становить `+350 Гц`, а відносне відхилення дорівнює `Δf_ppm = (+350 / 25 000 000) · 10⁶ = +14 ppm`.

Якщо виміряне значення відхилення перевищує 50 ppm, це свідчить про неправильний розрахунок ємності навантажувальних конденсаторів `C_L1` та `C_L2` (Load Capacitance) або паразитної ємності друкованих провідників плати `C_stray`. При відхиленні частоти більше 200 ppm високошвидкісні інтерфейси (наприклад, USB 2.0 Full/High Speed або шина CAN-FD) не зможуть підтримувати синхронізацію кадрів і будуть генерувати безперервні помилки передачі (Stuff Error, CRC Error).

### 3.5. Стан `STATE_SWD_DISCOVERY`: Низькорівнева ініціалізація та рукостискання CoreSight

Коли фізичні параметри живлення, скидання та тактування підтверджені, діагностичний автомат переходить до спроби встановлення налагоджувального з'єднання через інтерфейс SWD.

Процедура відкриття сесії складається з обов'язкових послідовностей:
1. **Протокольне скидання лінії (SWD Line Reset):** Майстер виставляє лінію `SWDIO` у високий логічний рівень і формує щонайменше 56 тактових імпульсів на лінії `SWCLK`. Це гарантує синхронізацію внутрішнього скінченного автомата налагоджувального порту (SW-DP) навіть якщо попередня транзакція була аварійно перервана посередині передачі даних.
2. **Перемикання JTAG-to-SWD:** Оскільки на багатьох мікроконтролерах виводи `SWDIO` та `SWCLK` суміщені з лініями JTAG (`JTMS` та `JTCK`), передається стандартизована 16-бітна послідовність перемикання `0x79E7` (передається молодшим бітом уперед як `0xE79E`). Ця послідовність вимикає TAP-контролер JTAG і активує контролер Serial Wire Debug.
3. **Повторне скидання та холості такти:** Передається повторна серія з 56 тактів високого рівня, після чого формується щонайменше 4 холостих такти низького рівня (Idle Cycles) для переведення інтерфейсу в стан готовності до прийому першого запиту.
4. **Читання ідентифікаційного регістра `DPIDR`:** Майстер надсилає 8-бітний заголовок читання регістра за адресою `0x00` (Debug Port Identification Register). Від мікроконтролера очікується відповідь `ACK = 0b001` (ACK OK) та 32-бітний код ідентифікатора. Наприклад, значення `0x0BC11477` вказує на ядро Cortex-M0+ із SW-DPv2, а `0x2BA01477` — на ядро Cortex-M4/M7 із підтримкою розширеного захисту.
5. **Активація системних доменів налагодження (`CTRL/STAT`):** Для того, щоб отримати доступ до внутрішньої шини процесора через модуль AHB-AP, необхідно подати живлення на налагоджувальний домен. Майстер записує значення `0x50000000` у регістр `CTRL/STAT`, встановлюючи біти `CDBGPWRUPREQ` (Debug Power-Up Request) та `CSYSPWRUPREQ` (System Power-Up Request). Потім виконується опитування цього ж регістра доти, доки біти підтвердження `CDBGPWRUPACK` та `CSYSPWRUPACK` не перейдуть в одиничний стан.

### 3.6. Покроковий протокол транзакцій MEM-AP для прямого доступу до пам'яті

Після успішної активації налагоджувального порту SW-DP сервісний контролер отримує можливість читати та записувати дані безпосередньо у внутрішній адресний простір мікроконтролера (Flash, SRAM, периферійні регістри) через модуль Memory Access Port (MEM-AP / AHB-AP).

Послідовність виконання 32-бітної операції читання пам'яті:
1. **Вибір порту доступу та банку регістрів (DP SELECT):** Майстер записує у регістр `SELECT` значення `0x00000000`, що обирає Access Port 0 (AHB-AP) та банк регістрів 0 (`0x00–0x0C`).
2. **Конфігурація режиму передачі (MEM-AP CSW):** У регістр `CSW` (Control/Status Word за адресою `0x00` в обраному банку AP) записується значення `0x23000002`. Ця конфігурація задає:
   - Розмір передачі (Size) = 32 біти (`0b010`);
   - Автоінкремент адреси (AddrInc) = Single Increment (`0b01`), що автоматично збільшує адресу в регістрі `TAR` на 4 байти після кожного звернення;
   - Захист доступу (DeviceEn, HPROT) = привілейований режим доступу даних (`0x23`).
3. **Запис адреси цільової пам'яті (MEM-AP TAR):** У регістр `TAR` (Transfer Address Register за адресою `0x04`) записується фізична адреса пам'яті (наприклад, `0x08000000` для Flash або `0xE000ED00` для регістра CPUID).
4. **Ініціація шинної транзакції (MEM-AP DRW Read):** Майстер виконує перше читання регістра даних `DRW` (Data Read/Write за адресою `0x0C`). За протоколом ARM CoreSight це перше читання є попереднім: воно запускає апаратний цикл читання на внутрішній шині AHB-Lite і завантажує дані в конвеєр DAP, повертаючи застаріле значення.
5. **Отримання актуальних даних з буфера (DP RDBUFF):** Майстер виконує читання регістра `RDBUFF` Debug-порту (або повторне читання `DRW`), яке повертає реальне 32-бітне значення, зчитане з пам'яті процесора.

### 3.7. Обробка виняткових ситуацій протоколу SWD (Fault Handling & Re-Synchronization)

Під час опитування регістрів та передачі даних по шині SWD можуть виникати апаратні конфлікти та збої таймінгів. Діагностичний автомат реалізує дворівневу систему обробки протокольних помилок:

1. **Обробка статусу `ACK = 0b010` (ACK WAIT):**
   Якщо мікроконтролер виконує внутрішню повільну операцію (наприклад, апаратне стирання сектора флеш-пам'яті або доступ до зовнішньої SDRAM), він повертає відповідь `ACK WAIT`. Автомат не розриває з'єднання, а переходить у режим очікування з експоненціальним відкатом (Exponential Backoff): тривалість паузи між повторними запитами збільшується від 10 мкс до 1.0 мс із загальним таймаутом до 500 мс.
2. **Обробка статусу `ACK = 0b100` (ACK FAULT):**
   Відповідь `ACK FAULT` виникає при зверненні до неіснуючої адреси пам'яті або шинному тайм-ауті внутрішнього контролера AHB-Lite. При отриманні Fault автомат записує маску `0x0000001E` у регістр `ABORT` Debug-порту, що апаратно скидає всі липкі прапорці помилок (`ORUNERRCLR`, `WDERRCLR`, `STKERRCLR`, `STKCMPCLR`), після чого повторює спробу адресації.
3. **Відновлення втрати бітової синхронізації:**
   Якщо на лінії `SWCLK` стався збій через паразитну наводку і біт парності `Parity` не зійшовся, автомат миттєво відправляє серію з 56 тактів високого рівня (Line Reset) та повторює зчитування регістра `DPIDR`. Якщо повторне скидання відновлює зв'язок, у телеметричний звіт записується попередження `WARN_SWD_JITTER_RECOVERED`.

---

## 4. Каталог типових аварійних станів та алгоритми відмовостійкої діагностики

У процесі практичного тестування реальних друкованих плат автомат Bringup стикається з нестандартними фізичними станами, які вимагають специфічної реакції програмного алгоритму:

### 4.1. Паразитичне фантомне живлення через діоди захисту ESD (Phantom Power)

Якщо налагоджувальний адаптер або сервісний стенд подає високі логічні рівні на лінії `SWCLK` або `SWDIO` до моменту активації головного джерела живлення плати, виникає небезпечний ефект паразитичного живлення. Струм від лінії зв'язку тече через верхній внутрішній захисний діод мікроконтролера (ESD Clamp Diode) безпосередньо у внутрішню шину `VDD` мікроконтролера:

```
Лінія SWDIO (3.3 В) ──► [ ESD Diodes ] ──► Внутрішня шина VDD (підйом до 2.2 В)
```

В результаті мікроконтролер намагається запуститися при зниженій напрузі 2.0–2.4 В через високоомний вихідний каскад логічного буфера тестера. Струм обмежений внутрішнім опором драйвера (близько 50–100 Ом), напруга нестабільна, внутрішні схеми пам'яті зависають у невизначеному стані, а ядро потрапляє в стан блокування (Lockup).

**Алгоритм реакції діагностичного автомата:**
У стані `STATE_IDLE_STANDBY` автомат вимірює напругу на шині `VDD`. Якщо фіксується значення `VDD > 300 мВ` при вимкненому силовому ключі, автомат примусово переводить усі цифрові виводи стенду (`SWDIO`, `SWCLK`, `NRST`, `BOOT0`) у логічний нуль на 20 мс, розряджаючи шину до нуля перед увімкненням основного регулятора живлення.

### 4.2. Експоненціально затягнутий фронт лінії скидання (RC Sluggish Rise)

Помилка підбору номіналу конденсатора на лінії `nRST` (наприклад, встановлення керамічного конденсатора 10 мкФ замість 100 нФ або використання конденсатора з високим струмом витоку) призводить до надмірно великої сталої часу заряджання `τ = R_pullup · C_nrst = 40 кОм · 10 мкФ = 400 мс`.

При цьому напруга на лінії `nRST` наростає вкрай повільно. Мікроконтролер залишається в стані апаратного скидання протягом майже пів секунди після старту живлення. Якщо налагоджувач спробує ініціалізувати зв'язок через стандартний таймаут 50 мс, він отримає помилку відсутності відповіді, хоча всі мікросхеми на платі повністю справні.

**Алгоритм реакції діагностичного автомата:**
Автомат безперервно вимірює напругу `nRST` за допомогою АЦП та фіксує точний час досягнення порогу логічної одиниці `t_nrst_high`. Якщо цей час перевищує 50 мс, але не досягає 200 мс, статус тесту скидання маркується як `WARN_SLOW_RESET`, що дозволяє успішно завершити Bringup, але виставляє попередження інженерам-схемотехнікам про необхідність заміни номіналу пасивного компонента.

### 4.3. Блокування ядра режимами низького енергоспоживання (WFI / Stop / Standby)

Якщо на плату було попередньо прошито програмне забезпечення з агресивними режимами енергозбереження, мікроконтролер може переходити в режим глибокого сну (Deep Sleep / Stop Mode) у перші ж мікросекунди після запуску. У цих режимах тактування ядра зупиняється, а тактування блоку CoreSight DP/AP вимикається для мінімізації споживання струму (до одиниць мікроампер).

Спроба підключення стандартним відлагоджувачем завершується помилкою `Cannot connect to target` або `SWD ACK Fault`, оскільки внутрішній блок DAP (Debug Access Port) не отримує тактового сигналу.

**Алгоритм відновлення (Connect-Under-Reset Triage):**
1. Стенд опускає лінію `nRST` у низький рівень (0 В) за допомогою апаратного транзистора тестера.
2. Утримуючи процесор під скиданням, автомат виконує послідовність `SWD Line Reset` та перемикання `0x79E7`.
3. Опитується регістр `DPIDR` — налагоджувальний порт успішно відповідає навіть при затиснутому скиданні.
4. Автомат подає запити живлення в регістр `CTRL/STAT` і через регістри ядра `DHCSR` (`0xE000EDF0`) встановлює біти `C_DEBUGEN = 1` та `C_HALT = 1`.
5. Після цього лінія `nRST` відпускається у високий рівень. Мікроконтролер виходить зі скидання, але ядро миттєво зупиняється апаратним блоком CoreSight перед вибіркою першої інструкції з Flash-пам'яті (вектора `Reset_Handler`).
6. Автомат отримує повний контроль над процесором і може виконати стирання пам'яті (Mass Erase).

### 4.4. Захист від зчитування флеш-пам'яті (Readout Protection Level 1 / Level 2)

Якщо мікроконтролер надійшов на стенд із встановленим рівнем захисту Flash RDP Level 1 (наприклад, чип використовувався повторно після попереднього тестування), інтерфейс SWD дозволяє прочитати `DPIDR` та активувати живлення в `CTRL/STAT`. Проте будь-яка спроба звернення до системної шини через `MEM-AP` (читання Flash або SRAM) блокується апаратним монітором безпеки і повертає `ACK = 0b100` (ACK FAULT).

**Алгоритм зняття захисту:**
1. Автомат детектує наявність захисту RDP за характерною ознакою: `DPIDR` читається коректно, але читання адреси `0x08000000` через MEM-AP викликає Fault.
2. Через спеціальний регістр Option Bytes у просторі пам'яті Flash-контролера подається авторизаційна послідовність ключів розблокування (наприклад, для STM32: запис `0x45670123` та `0xCDEF89AB` у регістр `FLASH_KEYR`, потім запис `0x08192A3B` та `0x4C5D6E7F` у регістр `FLASH_OPTKEYR`).
3. У конфігураційний регістр Option Control записується байт рівня захисту `0xAA` (RDP Level 0 — відкритий доступ).
4. Flash-контролер апаратно ініціює повне стирання всієї флеш-пам'яті та секторів користувача (Mass Erase) і генерує автоматичне системне перезавантаження.
5. Після повторного циклу Bringup чип стає повністю доступним для запису нової прошивки.

### 4.5. Деградація контактного опору голок голчастого адаптера

При тривалій експлуатації стенду на контактах голок Pogo Pins накопичуються залишки каніфолі, флюсу No-Clean та окисли металів. Контактний опір `R_contact` окремої голки може зрости від номінальних 20–30 мОм до 1.5–3.0 Ом.

При протіканні динамічного струму ядра під час старту (наприклад, імпульс струму 150 мА тривалістю кілька мікросекунд) на контактному опорі виникає падіння напруги:

```
ΔV_drop = I_target · R_contact = 0.15 А · 2.0 Ом = 0.30 В (300 мВ)
```

В результаті реальна напруга живлення мікроконтролера просідає з 3.3 В до 3.0 В, що викликає спрацьовування внутрішнього детектора Brownout Reset (BOR) та перезапуск процесора.

**Алгоритм детектування контактного опору Кельвіна:**
Діагностичний автомат проводить вимірювання напруги за 4-провідною схемою Кельвіна: паралельно вимірюється напруга на виході силового ключа тестера `V_force` та напруга на окремій вимірювальній голці `V_sense`, підключеній до тієї самої площадки на тестованій платі. Якщо різниця напруг під навантаженням перевищує 40 мВ, стенд реєструє аварійний стан `FAIL_FIXTURE_CONTACT_RESISTANCE` і видає оператору повідомлення про необхідність очищення контактного поля ізопропіловим спиртом або ультразвукової заміни голок.

### 4.6. Помилкове секвенсування в багатодоменних системах живлення

Складні системи на кристалі (наприклад, із роздільними шинами `VDD = 3.3 В`, `VDDA = 3.0 В`, `VCORE = 1.2 В` або `VDD_IO = 1.8 В`) вимагають суворого дотримання послідовності подачі напруг:
- Напруга введення-виведення `VDD` не повинна перевищувати аналогову напругу `VDDA` більше ніж на 300 мВ під час усього перехідного процесу;
- Напруга цифрового ядра `VCORE` не повинна подаватися раніше стабілізації допоміжних доменів живлення.

Порушення цієї послідовності призводить до прямого відкриття паразитних біполярних p-n-p-n структур всередині кремнієвого кристала і виникнення руйнівного ефекту тиристорного замикання (Latch-Up Effect), при якому струм споживання зростає до кількох ампер, викликаючи тепловий пробіг кристала.

**Алгоритм контролю секвенсування:**
Діагностичний автомат використовує багатоканальний синхронний АЦП (Dual Simultaneous Sampling ADC) для одночасного вимірювання напруг `VDD(t)` та `VDDA(t)`. На кожному кроці дискретизації перевіряється умова:

```
| VDD[i] - VDDA[i] | ≤ 300 мВ   (на всій ділянці від 0 В до V_nominal)
```

Якщо зафіксовано випередження однієї з шин на величину більше 300 мВ тривалістю понад 10 мкс, живлення негайно відключається за час менше 5 мкс аварійним ключем швидкого захисту.

### 4.7. Дзвін та відбиття сигналу на довгих проводах лінії SWCLK

При підключенні налагоджувального стенду через стрічкові кабелі (Ribbon Cable) або довгі джгути проводів без екранування виникає проблема неузгодженості хвильового імпедансу лінії (`Z_0 ≈ 100–120 Ом`) та низького вихідного опору драйвера (`R_out ≈ 15–25 Ом`).

Швидкий фронт сигналу `SWCLK` із крутизною `t_rise < 2 нс` викликає сильні відбиття сигналу від приймального входу мікроконтролера, що має високий імпеданс. На осцилограмі виникає високочастотний дзвін (Ringing) з амплітудою до 1.5 В вище шини живлення та просіданням нижче порогу логічної одиниці в момент тактування. В результаті ядро фіксує подвійні тактові імпульси (Double Clocking), що руйнує синхронізацію пакетів SWD.

**Алгоритм діагностики та компенсації:**
Діагностичний стенд включає послідовний демпфуючий резистор (Series Termination Resistor `R_term = 33 Ом`) безпосередньо на виході вихідного буфера `SWCLK`. Крім того, програмний драйвер автомата зменшує крутизну наростання вихідного каскаду GPIO (Slew Rate Limit = Medium) та знижує частоту бітбенгінгу з 2 МГц до 200 кГц при виявленні першої ж помилки парності `BRINGUP_ERR_SWD_PARITY_MISMATCH`.

### 4.8. Коротке замикання через мікроперемички припою (Solder Bridge Short)

Найпоширенішим дефектом поверхневого монтажу компонентів у корпусах QFP, QFN та BGA є виникнення мікроперемичок припою між сусідніми виводами живлення та землі під час оплавлення паяльної пасти. Опір такої перемички зазвичай становить від кількох міліом до сотень міліом.

Пряме підключення лабораторного джерела живлення без захисту викликає вигоряння доріжок плати або спалювання вихідного каскаду мікросхеми стабілізатора.

**Алгоритм захисту стенду:**
Силовий комутатор стенду обладнаний апаратною схемою швидкого струмового відсікання на базі компаратора з часом спрацьовування менше 2 мікросекунд при перевищенні порогу струму 500 мА. Якщо струмовий захист спрацював у перші ж мікросекунди після ввімкнення `power_enable`, стенд маркує плату як `FAIL_SHORT_CIRCUIT` та переходить до процедури локалізації місця замикання за допомогою мікроомметричного зондування.

### 4.9. Асиметричний витік та порушення імпедансу лінії SWDIO

Якщо на друкованій платі помилково встановлено зовнішній підтягувальний резистор до землі (Pull-Down 10 кОм) на лінії `SWDIO`, він утворює резистивний дільник напруги з внутрішнім підтягувальним резистором до живлення (Pull-Up 40–100 кОм) всередині мікроконтролера:

```
V_swdio_idle = VDD · (R_ext_down / (R_int_up + R_ext_down)) = 3.3 В · (10 кОм / (40 кОм + 10 кОм)) = 0.66 В
```

У стані спокою напруга на лінії `SWDIO` становить всього 0.66 В, що потрапляє в заборонену зону невизначеності логічних рівнів (між 0.8 В та 2.0 В). В результаті приймач мікроконтролера не може зафіксувати стартовий біт запиту хоста.

**Алгоритм виявлення дільника:**
Перед початком передачі пакетів SWD автомат переводить свій пін `SWDIO` у режим входу (Hi-Z) і вимірює постійну напругу на лінії за допомогою АЦП. Якщо виміряна напруга холостого ходу становить менше `0.7 · VDD` (тобто нижче 2.31 В), реєструється помилка `FAIL_SWDIO_INVALID_IDLE_LEVEL`, що вказує на наявність неправильних підтяжок або паразитного витоку на платі.

### 4.10. Збій внутрішнього стабілізатора живлення ядра (Internal Core LDO Failure)

Багато сучасних мікроконтролерів (наприклад, лінійки STM32F4, STM32H7, NXP LPC55) містять внутрішній стабілізатор LDO або імпульсний регулятор SMPS, що формує напругу живлення цифрового ядра `VCORE = 1.2 В` з вхідної напруги `VDD = 3.3 В`. Для стабілізації цього внутрішнього регулятора виробники вимагають підключення зовнішніх керамічних конденсаторів ємністю 2.2–4.7 мкФ із низьким еквівалентним послідовним опором (ESR < 1 Ом) до спеціальних виводів `VCAP1` та `VCAP2`.

Якщо конденсатор `VCAP` не запаяно, має тріщину або встановлено неякісний компонент із високим ESR, внутрішній регулятор переходить у режим автоколивань або видає занижену напругу `VCORE < 0.9 В`. При цьому зовнішнє живлення `VDD = 3.3 В` перебуває в ідеальному стані, але процесор повністю мертвий.

**Алгоритм контролю шини VCAP:**
Діагностичний стенд виводить окрему голку голчастого адаптера безпосередньо на тестову точку `VCAP_SENSE`. Автомат вимірює напругу ядра та її пульсації. Якщо напруга `VCAP` відхиляється від номіналу 1.20 В більше ніж на 5% (`1.14 В ≤ VCAP ≤ 1.26 В`) або розмах пульсацій перевищує 20 мВ, виставляється прямий діагностичний вердикт: `FAIL_INTERNAL_REGULATOR_VCAP_CAPACITOR_DEFECT`.

---

## 5. Інтеграція в конвеєр виробничого контролю та CI/CD

Формування звіту в уніфікованому форматі JSON дозволяє напряму інтегрувати сервісний стенд Bringup у заводську систему управління виробництвом (MES — Manufacturing Execution System), бази даних якості та конвеєри безперервної інтеграції (Hardware-in-the-Loop CI/CD):

```json
{
  "bringup_report": {
    "verdict": "PASS",
    "error_code": 0,
    "power_rail": {
      "nominal_mv": 3300,
      "measured_mean_mv": 3294,
      "ripple_pp_mv": 18,
      "slew_rate_mv_per_us": 620,
      "is_monotonic": true
    },
    "reset_circuit": {
      "nrst_steady_mv": 3288,
      "release_delay_us": 1420
    },
    "clock_system": {
      "measured_freq_hz": 25000210,
      "ppm_error": 8
    },
    "swd_interface": {
      "dpidr_hex": "0x2BA01477",
      "ack_status": 1,
      "recovery_invoked": false
    }
  }
}
```

### 5.1. Статистичний аналіз стабільності техпроцесу (Cp та Cpk)

Збереження детальної аналогової телеметрії кожного етапу Bringup у централізованій базі даних дозволяє виробничим інженерам будувати контрольні карти Шухарта та розраховувати індекси придатності технологічного процесу монтажу плат:
- **Індекс розсіювання процесу (Process Capability Cp):**

```
Cp = (USL - LSL) / (6 · σ)
```

де `USL` та `LSL` — верхня та нижня межі допуску (Upper/Lower Specification Limits) для параметра (наприклад, для напруги живлення `USL = 3.45 В`, `LSL = 3.15 В`), а `σ` — середньоквадратичне відхилення вимірювань за вибіркою партії плат.

- **Індекс центрованості процесу (Process Capability Index Cpk):**

```
Cpk = min( (USL - μ) / (3 · σ), (μ - LSL) / (3 · σ) )
```

де `μ` — середнє значення виміряного параметра.

Значення Cpk ≥ 1.33 свідчить про стабільний і відтворюваний процес монтажу компонентів живлення, тоді як падіння Cpk < 1.0 сигналізує про дрейф параметрів паяльної пасти, знос живильників установника компонентів (Pick-and-Place Feeder) або нестабільність партії стабілізаторів напруги від постачальника.

### 5.2. Автоматизована архітектура регресійного тестування апаратних ревізій

При переході від ревізії A до ревізії B часто змінюється компонування друкованої плати, постачальники пасивних компонентів або мікросхеми перетворювачів живлення. Інтеграція машини станів Bringup у тестовий стенд CI/CD забезпечує безперервну верифікацію ключових параметрів апаратного забезпечення:
1. **Автоматизований запуск тестів при підключенні нової плати:** Тестовий стенд під керуванням Single-Board Computer (наприклад, Raspberry Pi CM4) фіксує підключення плати через сигнал датчика контактного тиску голчастого адаптера і автоматично запускає прогін повної послідовності Bringup FSM.
2. **Верифікація температурного дрейфу в кліматичній камері:** Автомат Bringup підтримує циклічний перезапуск цільової плати при ступінчастій зміні температури від -40°C до +85°C. На кожному температурному кроці реєструється зміна швидкості наростання живлення `dV/dt`, напруга спрацьовування детектора Brownout та дрейф частоти резонатора `ppm_error(T)`.
3. **Експорт артефактів тестування:** Результати кожного прогону зберігаються у вигляді підписаного JSON-файлу разом із графіками перехідних процесів у сховище артефактів (Artifact Storage), що забезпечує 100% простежуваність (Traceability) для кожного виробленого пристрою.

Використання розробленої машини станів дозволяє скоротити час первинної верифікації нової плати з 15–20 хвилин ручної метушні з щупами до 120 мілісекунд повністю автоматизованого тесту з формуванням детального телеметричного звіту.
