# ⚙️ Симуляція петлі адаптації лінку з гістерезисом та OLRC

У реальних системних чипсетах (наприклад, у прошивках радіомодемів Qualcomm, MediaTek, Intel або в модулі `mac80211` ядра Linux) селектор модуляції та кодування працює як двоконтурний керований автомат. Він вирішує задачу вибору оптимального індексу MCS в умовах постійних шумів і змін каналу.

Первинна внутрішня петля (англ. *Inner-Loop Rate Control*, ILRC) обирає індекс MCS за таблицею на основі виміряного значення SINR з урахуванням дельта-гістерезису. Друга зовнішня петля (англ. *Outer-Loop Rate Control*, OLRC) аналізує реальне надходження підтверджень ACK та NACK від декодера кадру. Вона автоматично підлаштовує динамічну поправку `sinr_offset_db`, утримуючи цільову ймовірність помилки блоку на рівні `BLER = 10%`.

## Двоконтурна архітектура: ILRC + OLRC

Загальний процес вибору MCS на кожному кадрі складається з кількох послідовних етапів:
1. **Знімання виміру SINR:** Фізичний шар (PHY) вимірює співвідношення сигналу до шуму по пилотних символах кадру.
2. **Застосування поправки OLRC:** До виміряного значення додається поточне зміщення `sinr_offset_db` для отримання ефективного `eff_sinr`.
3. **Табличний пошук із гістерезисом (ILRC):** Поточний індекс MCS порівнюється із сусідніми порогами таблиці `MCS_TABLE`. Перехід вгору вимагає перевищення порогу на `+hysteresis_db`, а перехід вниз — падіння нижче порогу на `-hysteresis_db`.
4. **Зворотне корегування за результатами декодування:** Якщо пакет успішно прийнято (ACK), поправка `sinr_offset_db` плавно піднімається на `STEP_UP`. Якщо виникла помилка (NACK), поправка моментально скидається на `STEP_DOWN`.

Нижче наведено повну реалізацію даного двоконтурного алгоритму мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define NUM_MCS 5
#define TARGET_BLER 0.10f
#define STEP_UP 0.10f   /* Крок підвищення порогової поправки при ACK */
#define STEP_DOWN 0.90f /* Крок зниження порогової поправки при NACK */

typedef struct {
    const char *name;
    float snr_threshold_db; /* Поріг SNR для BLER = 10% */
    float spectral_efficiency; /* біт/с/Гц */
} mcs_config_t;

static const mcs_config_t MCS_TABLE[NUM_MCS] = {
    {"QPSK 1/2",    2.5f,  1.0f},
    {"16-QAM 1/2",  7.3f,  2.0f},
    {"16-QAM 3/4", 10.5f,  3.0f},
    {"64-QAM 2/3", 14.3f,  4.0f},
    {"256-QAM 5/6",22.5f,  6.67f}
};

typedef struct {
    int current_mcs;
    float sinr_offset_db; /* Поправка зовнішньої петлі OLRC */
    float hysteresis_db;
} amc_controller_t;

void amc_init(amc_controller_t *amc, float hysteresis_db) {
    amc->current_mcs = 0; /* Стартуємо з найбезпечнішого QPSK 1/2 */
    amc->sinr_offset_db = 0.0f;
    amc->hysteresis_db = hysteresis_db;
}

/* Оновлення зовнішньої петлі на основі підтвердження ACK/NACK */
void amc_update_olrc(amc_controller_t *amc, bool is_ack) {
    if (is_ack) {
        /* При успіху повільно піднімаємо ефективне SINR */
        amc->sinr_offset_db += STEP_UP;
    } else {
        /* При помилці швидко опускаємо SINR, щоб скинути MCS */
        amc->sinr_offset_db -= STEP_DOWN;
    }
}

/* Оновлення внутрішньої петлі та вибір нового індексу MCS */
int amc_select_mcs(amc_controller_t *amc, float measured_sinr_db) {
    /* Ефективне SINR з урахуванням поправки OLRC */
    float eff_sinr = measured_sinr_db + amc->sinr_offset_db;
    int idx = amc->current_mcs;

    /* Перевірка на підвищення MCS (вгору з урахуванням гістерезису) */
    while (idx < NUM_MCS - 1) {
        if (eff_sinr >= MCS_TABLE[idx + 1].snr_threshold_db + amc->hysteresis_db) {
            idx++;
        } else {
            break;
        }
    }

    /* Перевірка на зниження MCS (вниз із запасом) */
    while (idx > 0) {
        if (eff_sinr < MCS_TABLE[idx].snr_threshold_db - amc->hysteresis_db) {
            idx--;
        } else {
            break;
        }
    }

    amc->current_mcs = idx;
    return idx;
}

int main(void) {
    amc_controller_t amc;
    amc_init(&amc, 1.2f); /* Гістерезис 1.2 дБ */

    float channel_sinr[] = {3.0f, 4.5f, 9.0f, 12.0f, 16.0f, 24.0f, 20.0f, 8.0f, 2.0f};
    size_t num_steps = sizeof(channel_sinr) / sizeof(channel_sinr[0]);

    printf("=== Симуляція адаптації лінку (C) ===\n");
    for (size_t i = 0; i < num_steps; i++) {
        float sinr = channel_sinr[i];
        int mcs = amc_select_mcs(&amc, sinr);

        /* Симулюємо результат: якщо SINR >= порогу — ACK, інакше NACK */
        bool ack = (sinr >= MCS_TABLE[mcs].snr_threshold_db);
        amc_update_olrc(&amc, ack);

        printf("Крок %2zu: SINR = %4.1f дБ -> MCS %d [%s] (η = %.2f, ACK = %s)\n",
               i, sinr, mcs, MCS_TABLE[mcs].name,
               MCS_TABLE[mcs].spectral_efficiency, ack ? "ТАК" : "НІ");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <iomanip>
#include <span>

struct McsProfile {
    std::string_view name;
    float snr_threshold_db;
    float spectral_efficiency;
};

class AmcController {
public:
    static constexpr float kTargetBler = 0.10f;
    static constexpr float kStepUp = 0.10f;
    static constexpr float kStepDown = 0.90f;

    explicit AmcController(float hysteresis_db = 1.2f)
        : hysteresis_db_(hysteresis_db) {}

    void updateOlrc(bool is_ack) noexcept {
        if (is_ack) {
            sinr_offset_db_ += kStepUp;
        } else {
            sinr_offset_db_ -= kStepDown;
        }
    }

    [[nodiscard]] std::size_t selectMcs(float measured_sinr_db, std::span<const McsProfile> mcs_table) noexcept {
        const float eff_sinr = measured_sinr_db + sinr_offset_db_;
        
        // Збільшуємо MCS якщо SINR перевищує поріг + гістерезис
        while (current_mcs_ + 1 < mcs_table.size() &&
               eff_sinr >= mcs_table[current_mcs_ + 1].snr_threshold_db + hysteresis_db_) {
            current_mcs_++;
        }

        // Зменшуємо MCS якщо SINR нижче порогу - гістерезис
        while (current_mcs_ > 0 &&
               eff_sinr < mcs_table[current_mcs_].snr_threshold_db - hysteresis_db_) {
            current_mcs_--;
        }

        return current_mcs_;
    }

    [[nodiscard]] std::size_t currentMcsIndex() const noexcept { return current_mcs_; }
    [[nodiscard]] float offsetDb() const noexcept { return sinr_offset_db_; }

private:
    std::size_t current_mcs_{0};
    float sinr_offset_db_{0.0f};
    float hysteresis_db_{1.2f};
};

int main() {
    constexpr static McsProfile kMcsTable[] = {
        {"QPSK 1/2",    2.5f,  1.0f},
        {"16-QAM 1/2",  7.3f,  2.0f},
        {"16-QAM 3/4", 10.5f,  3.0f},
        {"64-QAM 2/3", 14.3f,  4.0f},
        {"256-QAM 5/6",22.5f,  6.67f}
    };

    AmcController controller(1.2f);
    const std::vector<float> channel_sinr_timeline = {
        3.0f, 4.5f, 9.0f, 12.0f, 16.0f, 24.0f, 20.0f, 8.0f, 2.0f
    };

    std::cout << "=== Симуляція адаптації лінку (C++) ===\n";
    for (std::size_t i = 0; i < channel_sinr_timeline.size(); ++i) {
        const float sinr = channel_sinr_timeline[i];
        const auto mcs_idx = controller.selectMcs(sinr, kMcsTable);
        const auto& profile = kMcsTable[mcs_idx];

        const bool is_ack = (sinr >= profile.snr_threshold_db);
        controller.updateOlrc(is_ack);

        std::cout << "Крок " << std::setw(2) << i << ": SINR = "
                  << std::setw(4) << std::fixed << std::setprecision(1) << sinr << " дБ -> MCS "
                  << mcs_idx << " [" << profile.name << "] (η = "
                  << std::setprecision(2) << profile.spectral_efficiency
                  << ", ACK = " << (is_ack ? "ТАК" : "НІ") << ")\n";
    }

    return 0;
}
```
:::

## Детальний аналіз та математичні тонкощі реалізації

### 1. Асиметрія кроків OLRC (`STEP_UP` vs `STEP_DOWN`)
Для підтримки стійкого рівня помилок кадру `BLER = 10%` співвідношення кроків зобов'язане відповідати умові рівноваги в стаціонарному стані:

```
P_ACK · STEP_UP = P_NACK · STEP_DOWN
(1 − BLER) · STEP_UP = BLER · STEP_DOWN
```

Підставляючи `BLER = 0.10`:

```
0.90 · STEP_UP = 0.10 · STEP_DOWN
STEP_DOWN = 9 · STEP_UP
```

Саме тому в коді обрано `STEP_UP = 0.10 дБ` та `STEP_DOWN = 0.90 дБ`. Поява хоча б одного NACK миттєво збиває оцінку ефективного SINR майже на 1 дБ вниз, що змушує автомат скинути MCS, захищаючи потік від серійних втрат.

### 2. Приборкання ефекту брязкання (Hysteresis)
Значення `hysteresis_db = 1.2 дБ` створює розрив між умовами входу та виходу з режимів:
* Перехід з MCS 0 на MCS 1 (поріг 7.3 дБ) відбудеться тільки тоді, коли `eff_sinr ≥ 7.3 + 1.2 = 8.5 дБ`.
* Повернення з MCS 1 на MCS 0 відбудеться лише при падінні `eff_sinr < 7.3 − 1.2 = 6.1 дБ`.

Цей коридор у `2.4 дБ` надійно гасить шумові коливання каналу й упереджує паразитна перемикання сузір'їв.

## Апаратне знімання метрик та інтеграція у драйвери SOC

У реальних мікроконтролерах та SOC (наприклад, ESP32, Semtech SX1276/SX1280 або трансіверах STM32WL) замір швидкості та оцінка завад виконуються апаратно на фізичному рівні (PHY). 

Після прийому кожного пакета переривання від демодулятора оновлює внутрішні регістри оцінки сигналу:
* `REG_PKT_SNR_VALUE`: регістр значення SNR останнього прийнятого кадру (з роздільною здатністю 0.25 дБ).
* `REG_PKT_RSSI_VALUE`: абсолютний рівень потужності сигналу на апертурі антени у дБм.

Драйвер прошивки викликає функцію `amc_select_mcs` у контексті обробника переривання або завдання обробки кадрів. Отриманий індекс MCS записується у заголовок наступного випромінюваного кадру (наприклад, у полі PLCP Header standards 802.11 або MAC Header 4G/5G).

## Простеження та діагностика в операційній системі Linux

У системі Linux для аналізу роботи адаптації бітрейту використовується інструментарій `ftrace` та підсистема `debugfs`. Усі події вибору MCS драйвером `mac80211` надсилають трасування у ядро:

```bash
# Увімкнення трасування подій адаптації бітрейту
echo 1 > /sys/kernel/debug/tracing/events/mac80211/mac80211_tx_status/enable

# Перегляд журналу перемикання MCS у реальному часі
cat /sys/kernel/debug/tracing/trace_pipe | grep "bitrate"
```

Кожен рядок журналу показує поточний вибраний індекс MCS, кількість випробувальних повторів (retries) та результат підтвердження ACK. Якщо в журналі видно постійні коливання між сусідніми індексами через кожні 2–3 кадри, це є чітким симптомом недостатнього значення гістерезису `hysteresis_db` або надмірного кроку `STEP_UP` у драйвері радіокарти.

## Обробка крайніх випадків у прошивці

1. **Холодний старт (Initial Rate Selection):** При встановленні нового з'єднання автомат не має інформації про CQI. Безпечний підхід — почати з найнижчого MCS 0. Проте для прискорення розгону застосовують режим **швидкого розгону** (англ. *Fast Start*): при серії з 3 послідовних ACK автомат піднімає MCS вгору без вичікування накопичення лічильників.
2. **Агрегація кадрів (A-MPDU / Block ACK):** У сучасних Wi-Fi мережах передаються не поодинокі кадри, а агреговані пачки по 32–64 кадрики. Приймач повертає маску бітів (Block ACK Bitmask). Контролер AMC розраховує частку втрачених кадриків у пачці та коригує `sinr_offset_db` пропорційно до коефіцієнта втрат.
3. **Обмеження знизу та згори (Saturation):** Якщо рівень SNR впав нижче MCS 0, `sinr_offset_db` продовжує знижуватись у мінус. Щоб уникнути «глибокого насичення» акумулятора (коли для повернення до MCS 1 доведеться чекати 100 послідовних ACK), значення `sinr_offset_db` жорстко затискають у діапазоні `[-10.0 дБ ... +5.0 дБ]`.
