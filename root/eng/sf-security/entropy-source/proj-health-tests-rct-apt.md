# ⚙️ Реалізація онлайнових тестів працездатності NIST SP 800-90B (RCT та APT)

Апаратні генератори випадкових чисел схильні до раптових фізичних відмов під час тривалої експлуатації: мікротріщина в кристалі або обрив резистора перетворює тепловий шум на нуль, паразитна синхронізація генераторів глушить фазовий джиттер, а короткочасне зниження напруги живлення зупиняє коливання. Якщо генератор виходить з ладу непомітно, система продовжує випускати криптографічні ключі з нульовою ентропією, відкриваючи доступ зловмисникам. Цей проєкт розбирає вимоги специфікації NIST SP 800-90B та реалізує повноцінний модуль онлайнового тестування сирого потоку випадковості: тест на повторення (Repetition Count Test, RCT) та адаптивний пропорційний тест (Adaptive Proportion Test, APT).

## Архітектура неперервного контролю працездатності

Згідно з вимогами стандарту NIST SP 800-90B (§4.4), неперервне онлайнове тестування (Online Health Testing) має здійснюватися безпосередньо над сирими некондиціонованими відліками, що надходять з оцифровщика. Розміщення тестів після блоку кондиціонування або криптографічного гешування суворо заборонене: криптографічний геш володіє лавинним ефектом і перетворює навіть стаціонарний потік нулів на псевдовипадковий потік, приховуючи катастрофічну відмову фізичного сенсора.

Контроль складається з двох взаємодоповнюючих алгоритмів:
1. **Швидкий тест на повторення (RCT):** реагує на миттєве залипання виходу на одному фіксованому значенні;
2. **Адаптивний пропорційний тест (APT):** виявляє повільну деградацію фізичного джерела, порушення статистичного балансу та сповзання робочої точки підсилювача.

### 1. Тест на повторення (Repetition Count Test, RCT)

Тест фіксує ситуацію, коли одне й те саме дискретне значення повторюється неприпустиму кількість разів поспіль.

- Приймач зберігає значення попереднього відліку `A` та лічильник послідовних збігів `B`.
- Для кожного нового вхідного відліку `X`:
  - Якщо `X == A`, лічильник збільшується: `B = B + 1`.
  - Якщо `B ≥ C_RCT`, фіксується аварійний стан генератора (Health Test Error) та видається сигнал тривоги.
  - Якщо `X ≠ A`, фіксується новий еталонний відлік `A = X`, а лічильник скидається: `B = 1`.

Поріг відсікання `C_RCT` обчислюється аналітично на основі оціненої мін-ентропії одного відліку `H_∞` та заданої ймовірності хибного спрацьовування `α` (типово `α = 2⁻²⁰` або `α = 2⁻³⁰`):

```
C_RCT = 1 + ⌈ −log₂(α) / H_∞ ⌉
```

Для двійкового джерела (`1 біт` на символ) з оцінкою мін-ентропії `H_∞ = 0.8` біта та ймовірністю хибної тривоги `α = 2⁻³⁰` розрахунок дає:

```
C_RCT = 1 + ⌈ 30 / 0.8 ⌉ = 1 + ⌈ 37.5 ⌉ = 39 послідовних однакових бітів
```

Якщо фізичний генератор видав 39 нулів або 39 одиниць поспіль, тест однозначно сигналізує про відмову або навмисне блокування схеми.

### 2. Адаптивний пропорційний тест (Adaptive Proportion Test, APT)

Тест контролює, наскільки часто одне обране значення з'являється всередині фіксованого вікна з `W` відліків.

- Потік розбивається на послідовні вікна довжиною `W` відліків (стандарт рекомендує `W = 512` для двійкових джерел та `W = 1024` для багаторозрядних символів).
- Перший відлік нового вікна фіксується як цільове значення `A`.
- У наступних `W − 1` відліках підраховується загальна кількість збігів `B = ∑_{i=2}^{W} [X_i == A]`.
- Якщо в будь-який момент всередині вікна лічильник `B` досягає порогу `C_APT`, генератор негайно блокується.
- Після обробки всіх `W` відліків вікно скидається, і наступний відлік стає новим еталоном `A`.

Поріг `C_APT` визначається біноміальним розподілом з параметром успіху `p_max = 2^{−H_∞}` за допомогою наближення нормального розподілу або прямого обчислення квантиля біноміального хвоста:

```
C_APT = 1 + CRITBINOM(W − 1, 2^{−H_∞}, 1 − α)
```

Для вікна `W = 512`, `H_∞ = 0.6` та `α = 2⁻³⁰` порогове значення становить `C_APT = 312`.

## Вимоги до тестів запуску (Start-up Self Tests)

Окрім неперервного моніторингу під час нормальної роботи, стандарт NIST SP 800-90B (§4.3) вимагає обов'язкового виконання тестів запуску (Start-up Tests) перед початком генерації ключів:

1. Під час подачі живлення або скидання процесора TRNG повинен накопичити початковий буфер мінімум із `1024` сирих відліків (для двійкових джерел — не менше 4096 бітів).
2. Весь стартовий буфер проганяється через тести RCT та APT без передачі відліків у блок кондиціонування.
3. Лише після того, як стартовий блок повністю підтвердив свою відповідність порогам ентропії, драйвер активує вихідний інтерфейс і дозволяє засівання системного CSPRNG.

## Програмна реалізація модуля моніторингу

Нижче наведено виробничий код модуля моніторингу для вбудованих систем, розрахований на роботу з байтовим сирим потоком (`W = 512`, поріг `C_RCT = 35`, поріг `C_APT = 312` при `α = 2⁻³⁰`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define SP90B_RCT_CUTOFF   35
#define SP90B_APT_WINDOW   512
#define SP90B_APT_CUTOFF   312

typedef enum {
    SP90B_OK = 0,
    SP90B_ERR_RCT_FAILED = 1,
    SP90B_ERR_APT_FAILED = 2
} sp90b_status_t;

typedef struct {
    /* Внутрішній стан тесту RCT */
    uint8_t  rct_last_sample;
    uint32_t rct_rep_count;

    /* Внутрішній стан тесту APT */
    uint8_t  apt_target_sample;
    uint32_t apt_match_count;
    uint32_t apt_window_index;

    bool     initialized;
    bool     alarm_latched;
} sp90b_health_monitor_t;

void sp90b_init(sp90b_health_monitor_t *mon) {
    if (!mon) return;
    mon->rct_last_sample = 0;
    mon->rct_rep_count = 0;
    mon->apt_target_sample = 0;
    mon->apt_match_count = 0;
    mon->apt_window_index = 0;
    mon->initialized = false;
    mon->alarm_latched = false;
}

sp90b_status_t sp90b_process_sample(sp90b_health_monitor_t *mon, uint8_t sample) {
    if (!mon) return SP90B_ERR_RCT_FAILED;
    if (mon->alarm_latched) return SP90B_ERR_RCT_FAILED;

    /* Початкова ініціалізація під час першого відліку */
    if (!mon->initialized) {
        mon->rct_last_sample = sample;
        mon->rct_rep_count = 1;
        mon->apt_target_sample = sample;
        mon->apt_match_count = 1;
        mon->apt_window_index = 1;
        mon->initialized = true;
        return SP90B_OK;
    }

    /* 1. Виконання Repetition Count Test */
    if (sample == mon->rct_last_sample) {
        mon->rct_rep_count++;
        if (mon->rct_rep_count >= SP90B_RCT_CUTOFF) {
            mon->alarm_latched = true;
            return SP90B_ERR_RCT_FAILED;
        }
    } else {
        mon->rct_last_sample = sample;
        mon->rct_rep_count = 1;
    }

    /* 2. Виконання Adaptive Proportion Test */
    if (mon->apt_window_index == 0) {
        mon->apt_target_sample = sample;
        mon->apt_match_count = 1;
        mon->apt_window_index = 1;
    } else {
        if (sample == mon->apt_target_sample) {
            mon->apt_match_count++;
            if (mon->apt_match_count >= SP90B_APT_CUTOFF) {
                mon->alarm_latched = true;
                return SP90B_ERR_APT_FAILED;
            }
        }
        mon->apt_window_index++;
        if (mon->apt_window_index >= SP90B_APT_WINDOW) {
            mon->apt_window_index = 0;
        }
    }

    return SP90B_OK;
}

sp90b_status_t sp90b_process_buffer(sp90b_health_monitor_t *mon,
                                    const uint8_t *buf,
                                    size_t len) {
    for (size_t i = 0; i < len; ++i) {
        sp90b_status_t st = sp90b_process_sample(mon, buf[i]);
        if (st != SP90B_OK) {
            return st;
        }
    }
    return SP90B_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace trng::health {

enum class Status : uint8_t {
    Ok,
    RctFailed,
    AptFailed
};

template <uint32_t RctCutoff = 35, uint32_t AptWindow = 512, uint32_t AptCutoff = 312>
class Sp80090bMonitor {
public:
    constexpr Sp80090bMonitor() noexcept = default;

    [[nodiscard]] std::expected<void, Status> process_sample(uint8_t sample) noexcept {
        if (alarm_latched_) {
            return std::unexpected(last_error_);
        }

        if (!initialized_) {
            rct_last_sample_ = sample;
            rct_rep_count_ = 1;
            apt_target_sample_ = sample;
            apt_match_count_ = 1;
            apt_window_index_ = 1;
            initialized_ = true;
            return {};
        }

        // 1. Repetition Count Test
        if (sample == rct_last_sample_) {
            if (++rct_rep_count_ >= RctCutoff) {
                return fail(Status::RctFailed);
            }
        } else {
            rct_last_sample_ = sample;
            rct_rep_count_ = 1;
        }

        // 2. Adaptive Proportion Test
        if (apt_window_index_ == 0) {
            apt_target_sample_ = sample;
            apt_match_count_ = 1;
            apt_window_index_ = 1;
        } else {
            if (sample == apt_target_sample_) {
                if (++apt_match_count_ >= AptCutoff) {
                    return fail(Status::AptFailed);
                }
            }
            if (++apt_window_index_ >= AptWindow) {
                apt_window_index_ = 0;
            }
        }

        return {};
    }

    [[nodiscard]] std::expected<void, Status> process_batch(std::span<const uint8_t> data) noexcept {
        for (const uint8_t byte : data) {
            if (auto res = process_sample(byte); !res) {
                return res;
            }
        }
        return {};
    }

    [[nodiscard]] constexpr bool is_healthy() const noexcept {
        return !alarm_latched_;
    }

    void reset() noexcept {
        initialized_ = false;
        alarm_latched_ = false;
        last_error_ = Status::Ok;
        rct_rep_count_ = 0;
        apt_window_index_ = 0;
    }

private:
    [[nodiscard]] std::expected<void, Status> fail(Status s) noexcept {
        alarm_latched_ = true;
        last_error_ = s;
        return std::unexpected(s);
    }

    uint8_t  rct_last_sample_{0};
    uint32_t rct_rep_count_{0};

    uint8_t  apt_target_sample_{0};
    uint32_t apt_match_count_{0};
    uint32_t apt_window_index_{0};

    bool     initialized_{false};
    bool     alarm_latched_{false};
    Status   last_error_{Status::Ok};
};

} // namespace trng::health
```
:::

## Інженерні правила обробки аварійних станів

1. **Апаратне замикання стану тривоги (Latch-on-Alarm):**  
   Згідно з вимогами сертифікації FIPS 140-3 та BSI AIS 31, прапорець аварії `alarm_latched` не має права автоматично скидатися, якщо наступні відліки повернулися до норми. Короткочасний сплеск або збій у генераторі свідчить про зовнішнє втручання (наприклад, інжекцію завади лазером або мікрохвильовим випромінювачем). Повернення в робочий режим можливе лише після повного апаратного перезапуску (Power-on Reset) та повторного проходження тестів запуску (Start-up Tests).

2. **Захист від витоку дефектних відліків:**  
   Потік сирої ентропії повинен проходити через конвеєрний буфер затримки. Відліки передаються на блок кондиціонування лише після того, як вони повністю пройшли перевірку в поточному вікні APT. Якщо тест виявляє помилку, увесь буфер відліків негайно стирається нулями.

3. **Вимоги до пам'яті та швидкодії:**  
   Модуль онлайнового тестування має фіксовану константну пам'ять `O(1)` і не потребує динамічного виділення пам'яті (без викликів `malloc` або створення динамічних масивів), що робить його придатним для роботи в критичних секціях обробників переривань та мікроконтролерах без операційної системи. Кожен відлік обробляється за константний час `O(1)` з мінімальною кількістю умовних переходів, запобігаючи витокам інформації по каналах побічного часу (timing side-channels).
