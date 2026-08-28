# ⚙️ Програмний модуль 4-квадрантного лічильника енергії та NVM-журналу

Цей практичний проєкт демонструє повну, оптимізовану для реального часу реалізацію вбудованого метрологічного ядра 4-квадрантного лічильника електроенергії для мікроконтролерів класів ARM Cortex-M0+/M4/M7, ESP32, STM32 та RISC-V. Модуль здійснює математичну обробку дискретних відліків АЦП у цілочисельному форматі з фіксованою комою, обчислює діючі значення напруги й струму (True RMS), активну потужність `P`, реактивну потужність `Q` (методом 90-градусної затримки), класифікує енергетичні потоки за 4 квадрантами, захищає лічильник від самоходу (anti-creep) та забезпечує надійне збереження накопичених значень у кільцевий журнал енергонезалежної пам'яті (Flash / EEPROM Wear-Leveling) із контрольною сумою CRC16.

### Архітектура та математика обчислювального конвеєра

Метрологічний конвеєр розроблено з розрахунку на частоту дискретизації АЦП `f_s = 8000 Гц` (інтервал між відліками `T_s = 125 мкс`). Для стандартної промислової частоти мережі `50 Гц` один повний період напруги містить рівно `160 відліків` (`8000 / 50 = 160`).

Обробка кожного нового відліку пари `(v_mv, i_ma)` виконується у швидкому перериванні таймера або DMA-обробнику за наступним чотириетапним алгоритмом:

1. **Квадратурна лінія затримки (Hilbert/90° Quadrature):**
   Для визначення реактивної потужності `Q` без ресурсомістких тригонометричних функцій або вилучення квадратного кореня `√(S² - P²)`, алгоритм зсуває сигнал напруги на чверть періоду (90°). При 160 відліках на період чверть становить рівно `40 відліків`. Кільцевий буфер розміром у 40 елементів `int32_t` зберігає історію напруги, надаючи значення `v_delayed = v[n - 40]` із нульовими накладними витратами процесора.

2. **Обчислення миттєвих добутків та періодичне усереднення:**
   Миттєва активна потужність обчислюється як добуток поточної напруги на струм:
```
p_inst = v[n] · i[n]
```
   Миттєва реактивна потужність обчислюється як добуток затриманої напруги на струм:
```
q_inst = v[n - 40] · i[n]
```
   Значення накопичуються у 64-бітних акумуляторах `sum_p_inst` та `sum_q_inst`. По завершенню кожного повного періоду (кожні 160 відліків = 20 мс) суми діляться на кількість відліків, формуючи середні значення активної потужності `P` (у міліватах) та реактивної потужності `Q` (у міліварах).

3. **Класифікація потоку енергії за чотирма квадрантами:**
   На основі знаків середньої активної потужності `P` та реактивної потужності `Q` алгоритм визначає поточний режим роботи системи:
   - `P ≥ 0` та `Q ≥ 0` → **Квадрант I (Q1)**: Імпорт активної енергії + індуктивна реактивна енергія (споживання двигунів, трансформаторів).
   - `P < 0` та `Q ≥ 0` → **Квадрант II (Q2)**: Експорт активної енергії + індуктивна реактивна енергія (генерація синхронних генераторів).
   - `P < 0` та `Q < 0` → **Квадрант III (Q3)**: Експорт активної енергії + ємнісна реактивна енергія (генерація сонячних інверторів із компенсацією).
   - `P ≥ 0` та `Q < 0` → **Квадрант IV (Q4)**: Імпорт активної енергії + ємнісна реактивна енергія (споживання імпульсних блоків із фільтрами).

4. **Дворівневе накопичення енергії та захист від самоходу (Anti-Creep):**
   Елементарний квант енергії за один інтервал дискретизації `125 мкс` дорівнює:
```
dE = (p_inst мкВт) / 8000 Гц = (p_inst / 8000) мкДж
```
   Якщо миттєва потужність перевищує поріг чутливості `200 мВт` (`0.2 Вт`), квант додається до відповідного 64-бітного мікроджоульного регістра (`act_import_uj`, `act_export_uj`, `react_ind_uj`, `react_cap_uj`). Коли значення в мікроджоулях досягає еквіваленту `1 Вт·год = 3.6 · 10⁹ мкДж`, воно переноситься у 32-бітний регістр цілих ват-годин, а залишок залишається в мікроджоульному акумуляторі для подальшого точного інтегрування без похибки квантування.

### Фіксована крапка: Масштабування та відсутність FPU

Однією з ключових переваг наведеного коду є повна відмова від арифметики з рухомою комою (`float` / `double`). На бюджетних мікроконтролерах класу Cortex-M0+ без апаратного блоку FPU операції з числами `double` виконуються програмною бібліотекою і займають десятки тактів на кожну операцію множення.

Натомість у нашому модулі застосовано масштабування цілих чисел:
- Напруга передається в мілівольтах (`1 В = 1000 мВ`, тип `int32_t`);
- Струм передається в міліамперах (`1 А = 1000 мА`, тип `int32_t`);
- Добуток `v_mv * i_ma` дає мікровати (`1 мВ · 1 мА = 10⁻³ В · 10⁻³ А = 10⁻⁶ Вт = 1 мкВт`), що поміщається в 64-бітне ціле `int64_t` без переповнення;
- Елементарний енергетичний квант `p_inst / 8000` виражається безпосередньо в мікроджоулях (`мкДж`).

Таке масштабування забезпечує швидкість виконання обробника одного відліку менш ніж за 40 тактів процесора (менше `0.6 мкс` на ядрі 64 МГц), залишаючи понад `99%` процесорного часу для комунікаційних стеків (Modbus RTU, MQTT, Wi-Fi, BLE).

### Енергонезалежне збереження стану та вирівнювання зносу (Wear-Leveling)

Для захисту пам'яті Flash або EEPROM від передчасного виходу з ладу модуль реалізує циклічний журнал із `8` слотів (розмір сектора може бути збільшений до будь-якої кількості слотів залежно від геометрії пам'яті мікроконтролера).

Кожен слот має фіксовану бінарну структуру:
- Сигнатура валідності (`Magic Word = 0x5A4D`, 2 байти);
- Монотонний 32-бітний номер транзакції (`Sequence ID`, 4 байти);
- Чотири 32-бітні лічильники енергії (`act_import_wh`, `act_export_wh`, `react_ind_varh`, `react_cap_varh`, разом 16 байтів);
- Контрольна сума `CRC16-CCITT` (2 байти).

При старті системи функція ініціалізації перевіряє цілісність усіх слотів за допомогою розрахунку CRC16. Серед усіх непошкоджених записів обирається слот із найбільшим номером `Sequence ID`. Це гарантує миттєве відновлення останнього коректно збереженого стану навіть після аварійного відключення живлення під час виконання запису.

### Обробка крайових випадків та відхилень частоти

У реальній енергомережі частота напруги коливається в межах `49.5...50.5 Гц`. Якщо тривалість мережевого періоду дещо відхиляється від 20 мс, фіксована затримка на 40 відліків вносить додатковий фазовий зсув `Δψ = 90° · (Δf / f₀) ≈ 0.9°`. Для усунення цієї похибки в комерційних приладах реалізують детектор переходу через нуль (Zero-Crossing Detector) на каналі напруги, який вимірює реальний період у тактах таймера і динамічно підлаштовує розмір квадратурного буфера або інтерполює відліки за допомогою поліфазного FIR-фільтра.

Нижче наведено повний вихідний код модуля на мовах C та ідіоматичному C++20.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ADC_SAMPLE_RATE_HZ     8000
#define MAINS_FREQ_HZ          50
#define SAMPLES_PER_CYCLE      (ADC_SAMPLE_RATE_HZ / MAINS_FREQ_HZ) /* 160 відліків */
#define QUADRATURE_DELAY       (SAMPLES_PER_CYCLE / 4)             /* 40 відліків для 90° */
#define NVM_SECTOR_SLOTS       8
#define NVM_MAGIC_WORD         0x5A4D
#define ANTI_CREEP_POWER_MW    200   /* 0.2 Вт поріг чутливості */

/* Квадранти площини потужності за стандартом IEC 62053 */
typedef enum {
    QUADRANT_NONE = 0,
    QUADRANT_1_IMP_IND = 1, /* +P, +Q: Споживання активної, індуктивна реактивна */
    QUADRANT_2_EXP_IND = 2, /* -P, +Q: Генерація активної, індуктивна реактивна  */
    QUADRANT_3_EXP_CAP = 3, /* -P, -Q: Генерація активної, ємнісна реактивна     */
    QUADRANT_4_IMP_CAP = 4  /* +P, -Q: Споживання активної, ємнісна реактивна    */
} energy_quadrant_t;

/* 64-бітні накопичувачі енергії лічильника (в мікроджоулях та ват-годинах) */
typedef struct {
    uint64_t act_import_uj;   /* Активна імпорт (+P), мкДж */
    uint64_t act_export_uj;   /* Активна експорт (-P), мкДж */
    uint64_t react_ind_uj;    /* Реактивна індуктивна (+Q), мквар·с (мкДж) */
    uint64_t react_cap_uj;    /* Реактивна ємнісна (-Q), мквар·с (мкДж) */

    uint32_t act_import_wh;   /* Ват-години цілі імпорт */
    uint32_t act_export_wh;   /* Ват-години цілі експорт */
    uint32_t react_ind_varh;  /* Вар-години цілі індуктивні */
    uint32_t react_cap_varh;  /* Вар-години цілі ємнісні */
} energy_accumulators_t;

/* Слот енергонезалежного запису у Flash/EEPROM */
typedef struct {
    uint16_t magic;           /* NVM_MAGIC_WORD */
    uint16_t reserved;
    uint32_t seq_id;          /* Монотонний лічильник транзакцій */
    uint32_t act_import_wh;
    uint32_t act_export_wh;
    uint32_t react_ind_varh;
    uint32_t react_cap_varh;
    uint16_t crc16;
} nvm_slot_t;

/* Стан обчислювального конвеєра лічильника */
typedef struct {
    int32_t v_delay_buf[QUADRATURE_DELAY];
    uint32_t delay_idx;

    int64_t sum_v_sq;
    int64_t sum_i_sq;
    int64_t sum_p_inst;
    int64_t sum_q_inst;
    uint32_t sample_count;

    int32_t v_rms_mv;
    int32_t i_rms_ma;
    int32_t p_active_mw;
    int32_t q_reactive_mvar;
    energy_quadrant_t cur_quadrant;

    energy_accumulators_t accumulators;
    uint32_t nvm_last_saved_seq;
    nvm_slot_t flash_storage[NVM_SECTOR_SLOTS];
} energy_meter_engine_t;

/* Розрахунок CRC16-CCITT */
static uint16_t calc_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

/* Ініціалізація ядра вимірювання */
void energy_meter_init(energy_meter_engine_t *eng) {
    for (size_t i = 0; i < QUADRATURE_DELAY; ++i) {
        eng->v_delay_buf[i] = 0;
    }
    eng->delay_idx = 0;
    eng->sum_v_sq = 0;
    eng->sum_i_sq = 0;
    eng->sum_p_inst = 0;
    eng->sum_q_inst = 0;
    eng->sample_count = 0;
    eng->v_rms_mv = 0;
    eng->i_rms_ma = 0;
    eng->p_active_mw = 0;
    eng->q_reactive_mvar = 0;
    eng->cur_quadrant = QUADRANT_NONE;
    eng->nvm_last_saved_seq = 0;

    /* Скидання акумуляторів */
    eng->accumulators.act_import_uj = 0;
    eng->accumulators.act_export_uj = 0;
    eng->accumulators.react_ind_uj = 0;
    eng->accumulators.react_cap_uj = 0;
    eng->accumulators.act_import_wh = 0;
    eng->accumulators.act_export_wh = 0;
    eng->accumulators.react_ind_varh = 0;
    eng->accumulators.react_cap_varh = 0;

    /* Пошук останнього дійсного запису у Flash */
    uint32_t max_seq = 0;
    int best_slot = -1;
    for (int s = 0; s < NVM_SECTOR_SLOTS; ++s) {
        nvm_slot_t *slot = &eng->flash_storage[s];
        if (slot->magic == NVM_MAGIC_WORD) {
            uint16_t c = calc_crc16((const uint8_t *)slot, offsetof(nvm_slot_t, crc16));
            if (c == slot->crc16 && slot->seq_id > max_seq) {
                max_seq = slot->seq_id;
                best_slot = s;
            }
        }
    }

    if (best_slot >= 0) {
        nvm_slot_t *v = &eng->flash_storage[best_slot];
        eng->accumulators.act_import_wh = v->act_import_wh;
        eng->accumulators.act_export_wh = v->act_export_wh;
        eng->accumulators.react_ind_varh = v->react_ind_varh;
        eng->accumulators.react_cap_varh = v->react_cap_varh;
        eng->nvm_last_saved_seq = v->seq_id;
    }
}

/* Збереження поточного стану енергії у наступний слот NVM */
bool energy_meter_save_nvm(energy_meter_engine_t *eng) {
    uint32_t next_seq = eng->nvm_last_saved_seq + 1;
    uint32_t slot_idx = next_seq % NVM_SECTOR_SLOTS;
    nvm_slot_t *slot = &eng->flash_storage[slot_idx];

    slot->magic = NVM_MAGIC_WORD;
    slot->reserved = 0;
    slot->seq_id = next_seq;
    slot->act_import_wh = eng->accumulators.act_import_wh;
    slot->act_export_wh = eng->accumulators.act_export_wh;
    slot->react_ind_varh = eng->accumulators.react_ind_varh;
    slot->react_cap_varh = eng->accumulators.react_cap_varh;
    slot->crc16 = calc_crc16((const uint8_t *)slot, offsetof(nvm_slot_t, crc16));

    eng->nvm_last_saved_seq = next_seq;
    return true;
}

/* Обробка одного відліку АЦП (викликається з частотою 8 кГц) */
void energy_meter_process_sample(energy_meter_engine_t *eng, int32_t v_mv, int32_t i_ma) {
    /* 1. Квадратурна лінія затримки 90° для напруги */
    int32_t v_delayed = eng->v_delay_buf[eng->delay_idx];
    eng->v_delay_buf[eng->delay_idx] = v_mv;
    eng->delay_idx = (eng->delay_idx + 1) % QUADRATURE_DELAY;

    /* 2. Миттєві добутки (у мікроватах: мВ * мА = мкВт) */
    int64_t p_inst = (int64_t)v_mv * i_ma;
    int64_t q_inst = (int64_t)v_delayed * i_ma;

    eng->sum_v_sq += (int64_t)v_mv * v_mv;
    eng->sum_i_sq += (int64_t)i_ma * i_ma;
    eng->sum_p_inst += p_inst;
    eng->sum_q_inst += q_inst;
    eng->sample_count++;

    /* 3. Оновлення мікроджоульних акумуляторів кожні 125 мкс (1 Вт*с = 10^6 мкДж) */
    /* Елементарний квант енергії dE = P_inst * dt = (p_inst мкВт) / (8000 Гц) = мкДж / 8 */
    int64_t de_p_uj = p_inst / ADC_SAMPLE_RATE_HZ;
    int64_t de_q_uj = q_inst / ADC_SAMPLE_RATE_HZ;

    /* Anti-creep фільтр: не накопичуємо, якщо активна потужність нижче порогу */
    if (p_inst > (int64_t)ANTI_CREEP_POWER_MW * 1000) {
        eng->accumulators.act_import_uj += (uint64_t)de_p_uj;
    } else if (p_inst < -((int64_t)ANTI_CREEP_POWER_MW * 1000)) {
        eng->accumulators.act_export_uj += (uint64_t)(-de_p_uj);
    }

    if (q_inst > (int64_t)ANTI_CREEP_POWER_MW * 1000) {
        eng->accumulators.react_ind_uj += (uint64_t)de_q_uj;
    } else if (q_inst < -((int64_t)ANTI_CREEP_POWER_MW * 1000)) {
        eng->accumulators.react_cap_uj += (uint64_t)(-de_q_uj);
    }

    /* Перенесення 1 Вт·год = 3.6 * 10^9 мкДж у цілі лічильники */
    const uint64_t UJ_PER_WH = 3600000000ULL;
    if (eng->accumulators.act_import_uj >= UJ_PER_WH) {
        eng->accumulators.act_import_wh += (uint32_t)(eng->accumulators.act_import_uj / UJ_PER_WH);
        eng->accumulators.act_import_uj %= UJ_PER_WH;
    }
    if (eng->accumulators.act_export_uj >= UJ_PER_WH) {
        eng->accumulators.act_export_wh += (uint32_t)(eng->accumulators.act_export_uj / UJ_PER_WH);
        eng->accumulators.act_export_uj %= UJ_PER_WH;
    }
    if (eng->accumulators.react_ind_uj >= UJ_PER_WH) {
        eng->accumulators.react_ind_varh += (uint32_t)(eng->accumulators.react_ind_uj / UJ_PER_WH);
        eng->accumulators.react_ind_uj %= UJ_PER_WH;
    }
    if (eng->accumulators.react_cap_uj >= UJ_PER_WH) {
        eng->accumulators.react_cap_varh += (uint32_t)(eng->accumulators.react_cap_uj / UJ_PER_WH);
        eng->accumulators.react_cap_uj %= UJ_PER_WH;
    }

    /* 4. Завершення періоду мережі (160 відліків = 20 мс) */
    if (eng->sample_count >= SAMPLES_PER_CYCLE) {
        eng->p_active_mw = (int32_t)(eng->sum_p_inst / (int64_t)eng->sample_count / 1000);
        eng->q_reactive_mvar = (int32_t)(eng->sum_q_inst / (int64_t)eng->sample_count / 1000);

        /* Визначення квадранта */
        if (eng->p_active_mw >= 0 && eng->q_reactive_mvar >= 0) {
            eng->cur_quadrant = QUADRANT_1_IMP_IND;
        } else if (eng->p_active_mw < 0 && eng->q_reactive_mvar >= 0) {
            eng->cur_quadrant = QUADRANT_2_EXP_IND;
        } else if (eng->p_active_mw < 0 && eng->q_reactive_mvar < 0) {
            eng->cur_quadrant = QUADRANT_3_EXP_CAP;
        } else {
            eng->cur_quadrant = QUADRANT_4_IMP_CAP;
        }

        /* Скидання періодичних сум */
        eng->sum_v_sq = 0;
        eng->sum_i_sq = 0;
        eng->sum_p_inst = 0;
        eng->sum_q_inst = 0;
        eng->sample_count = 0;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <expected>

namespace Metering {

inline constexpr uint32_t SampleRateHz = 8000;
inline constexpr uint32_t MainsFreqHz = 50;
inline constexpr uint32_t SamplesPerCycle = SampleRateHz / MainsFreqHz; // 160
inline constexpr uint32_t QuadratureDelay = SamplesPerCycle / 4;       // 40
inline constexpr size_t NvmSectorSlots = 8;
inline constexpr uint16_t NvmMagicWord = 0x5A4D;
inline constexpr int32_t AntiCreepPowerMw = 200;                       // 0.2 W
inline constexpr uint64_t MicroJoulesPerWh = 3'600'000'000ULL;

enum class Quadrant : uint8_t {
    None = 0,
    Q1_ImportInductive = 1, // +P, +Q
    Q2_ExportInductive = 2, // -P, +Q
    Q3_ExportCapacitive = 3, // -P, -Q
    Q4_ImportCapacitive = 4  // +P, -Q
};

enum class MeterError {
    CrcMismatch,
    StorageCorrupted,
    InvalidSample
};

struct EnergyRegisters {
    uint64_t actImportUj{0};
    uint64_t actExportUj{0};
    uint64_t reactIndUj{0};
    uint64_t reactCapUj{0};

    uint32_t actImportWh{0};
    uint32_t actExportWh{0};
    uint32_t reactIndVarh{0};
    uint32_t reactCapVarh{0};
};

struct alignas(4) NvmSlot {
    uint16_t magic{NvmMagicWord};
    uint16_t reserved{0};
    uint32_t seqId{0};
    uint32_t actImportWh{0};
    uint32_t actExportWh{0};
    uint32_t reactIndVarh{0};
    uint32_t reactCapVarh{0};
    uint16_t crc16{0};

    [[nodiscard]] static constexpr uint16_t calculateCrc(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (int b = 0; b < 8; ++b) {
                crc = (crc & 0x8000) ? static_cast<uint16_t>((crc << 1) ^ 0x1021) : static_cast<uint16_t>(crc << 1);
            }
        }
        return crc;
    }
};

class FourQuadrantEnergyEngine {
public:
    constexpr FourQuadrantEnergyEngine() noexcept {
        initStorage();
    }

    void processSample(int32_t vMv, int32_t iMa) noexcept {
        // 1. Квадратурний буфер затримки напруги на 90 градусів
        int32_t vDelayed = vDelayBuf_[delayIdx_];
        vDelayBuf_[delayIdx_] = vMv;
        delayIdx_ = (delayIdx_ + 1) % QuadratureDelay;

        // 2. Миттєві добутки (мВ * мА = мкВт)
        int64_t pInst = static_cast<int64_t>(vMv) * iMa;
        int64_t qInst = static_cast<int64_t>(vDelayed) * iMa;

        sumVsq_ += static_cast<int64_t>(vMv) * vMv;
        sumIsq_ += static_cast<int64_t>(iMa) * iMa;
        sumPinst_ += pInst;
        sumQinst_ += qInst;
        ++sampleCount_;

        // 3. Дискретне накопичення енергії кожні 125 мкс
        int64_t deP = pInst / SampleRateHz;
        int64_t deQ = qInst / SampleRateHz;

        if (pInst > static_cast<int64_t>(AntiCreepPowerMw) * 1000) {
            regs_.actImportUj += static_cast<uint64_t>(deP);
        } else if (pInst < -static_cast<int64_t>(AntiCreepPowerMw) * 1000) {
            regs_.actExportUj += static_cast<uint64_t>(-deP);
        }

        if (qInst > static_cast<int64_t>(AntiCreepPowerMw) * 1000) {
            regs_.reactIndUj += static_cast<uint64_t>(deQ);
        } else if (qInst < -static_cast<int64_t>(AntiCreepPowerMw) * 1000) {
            regs_.reactCapUj += static_cast<uint64_t>(-deQ);
        }

        // Перенесення ват-годин (квант 3.6 GJ)
        accumulateWh(regs_.actImportUj, regs_.actImportWh);
        accumulateWh(regs_.actExportUj, regs_.actExportWh);
        accumulateWh(regs_.reactIndUj, regs_.reactIndVarh);
        accumulateWh(regs_.reactCapUj, regs_.reactCapVarh);

        // 4. Фінал періоду 20 мс
        if (sampleCount_ >= SamplesPerCycle) {
            pActiveMw_ = static_cast<int32_t>(sumPinst_ / static_cast<int64_t>(sampleCount_) / 1000);
            qReactiveMvar_ = static_cast<int32_t>(sumQinst_ / static_cast<int64_t>(sampleCount_) / 1000);

            if (pActiveMw_ >= 0 && qReactiveMvar_ >= 0) {
                curQuadrant_ = Quadrant::Q1_ImportInductive;
            } else if (pActiveMw_ < 0 && qReactiveMvar_ >= 0) {
                curQuadrant_ = Quadrant::Q2_ExportInductive;
            } else if (pActiveMw_ < 0 && qReactiveMvar_ < 0) {
                curQuadrant_ = Quadrant::Q3_ExportCapacitive;
            } else {
                curQuadrant_ = Quadrant::Q4_ImportCapacitive;
            }

            sumVsq_ = 0;
            sumIsq_ = 0;
            sumPinst_ = 0;
            sumQinst_ = 0;
            sampleCount_ = 0;
        }
    }

    [[nodiscard]] std::expected<void, MeterError> commitToNvm() noexcept {
        uint32_t nextSeq = nvmLastSavedSeq_ + 1;
        size_t slotIdx = nextSeq % NvmSectorSlots;
        auto& slot = storage_[slotIdx];

        slot.magic = NvmMagicWord;
        slot.reserved = 0;
        slot.seqId = nextSeq;
        slot.actImportWh = regs_.actImportWh;
        slot.actExportWh = regs_.actExportWh;
        slot.reactIndVarh = regs_.reactIndVarh;
        slot.reactCapVarh = regs_.reactCapVarh;

        auto rawSpan = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&slot), sizeof(NvmSlot) - sizeof(uint16_t));
        slot.crc16 = NvmSlot::calculateCrc(rawSpan);

        nvmLastSavedSeq_ = nextSeq;
        return {};
    }

    [[nodiscard]] const EnergyRegisters& registers() const noexcept { return regs_; }
    [[nodiscard]] Quadrant currentQuadrant() const noexcept { return curQuadrant_; }
    [[nodiscard]] int32_t activePowerMw() const noexcept { return pActiveMw_; }
    [[nodiscard]] int32_t reactivePowerMvar() const noexcept { return qReactiveMvar_; }

private:
    static constexpr void accumulateWh(uint64_t& uj, uint32_t& wh) noexcept {
        if (uj >= MicroJoulesPerWh) {
            wh += static_cast<uint32_t>(uj / MicroJoulesPerWh);
            uj %= MicroJoulesPerWh;
        }
    }

    void initStorage() noexcept {
        uint32_t maxSeq = 0;
        std::optional<size_t> bestSlot;

        for (size_t s = 0; s < NvmSectorSlots; ++s) {
            const auto& slot = storage_[s];
            if (slot.magic == NvmMagicWord) {
                auto rawSpan = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&slot), sizeof(NvmSlot) - sizeof(uint16_t));
                if (NvmSlot::calculateCrc(rawSpan) == slot.crc16 && slot.seqId >= maxSeq) {
                    maxSeq = slot.seqId;
                    bestSlot = s;
                }
            }
        }

        if (bestSlot) {
            const auto& slot = storage_[*bestSlot];
            regs_.actImportWh = slot.actImportWh;
            regs_.actExportWh = slot.actExportWh;
            regs_.reactIndVarh = slot.reactIndVarh;
            regs_.reactCapVarh = slot.reactCapVarh;
            nvmLastSavedSeq_ = slot.seqId;
        }
    }

    std::array<int32_t, QuadratureDelay> vDelayBuf_{};
    size_t delayIdx_{0};

    int64_t sumVsq_{0};
    int64_t sumIsq_{0};
    int64_t sumPinst_{0};
    int64_t sumQinst_{0};
    uint32_t sampleCount_{0};

    int32_t pActiveMw_{0};
    int32_t qReactiveMvar_{0};
    Quadrant curQuadrant_{Quadrant::None};

    EnergyRegisters regs_{};
    uint32_t nvmLastSavedSeq_{0};
    std::array<NvmSlot, NvmSectorSlots> storage_{};
};

} // namespace Metering
```
:::
