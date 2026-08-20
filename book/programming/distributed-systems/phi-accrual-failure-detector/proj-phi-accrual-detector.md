# ⚙️ Реалізація детектора відмов Phi Accrual

Практична реалізація детектора Phi Accrual вимагає потокового статистичного обліку часових інтервалів, захисту від зникнення порядку при обчисленні додаткової функції помилок Гауса та обробки крайових випадків (холодний старт, нульова дисперсія). Нижче наведено завершену промислову реалізацію детектора на мовах C та C++, готову до вбудовування у мережеві сервіси та протоколи членства.

## Архітектура та структури даних

Алгоритм зберігає фіксовану кількість останніх часових інтервалів `W` (за замовчуванням `1000`) у кільцевому буфері. Для забезпечення складності `O(1)` при додаванні чергового сигналу пульсу алгоритм підтримує поточну суму елементів `sum` та суму їхніх квадратів `sum_sq`.

При витісненні старого значення зі заповненого буфера:
```
sum_new = sum_old - val_evicted + val_new
sum_sq_new = sum_sq_old - (val_evicted)² + (val_new)²
```

Вибіркове середнє `μ` та стандартне відхилення `σ` обчислюються за один арифметичний крок:
```
μ = sum / N
σ = √((sum_sq / N) - μ²)
```

Для запобігання діленню на нуль у синтетичних тестах (де сигнатуру пульсу генерує таймер без джиттеру) вводиться захисний мінімальний поріг `min_std_dev = 0.05` (50 мс).

## Покроковий життєвий цикл обробки подій

Робота детектора ділиться на два взаємодоповнюючі тракти:

1. **Тракт запису (Write Path — метод `heartbeat`):**
   * Викликається асинхронно мережевим потоком при отриманні кожного контрольного повідомлення (UDP/TCP або Gossip ping).
   * Фіксує монотонну мітку часу `now`.
   * Якщо це не перший сигнал, обчислює тривалість інтервалу `interval = now - last_timestamp`.
   * Записує значення `interval` у поточну позицію кільцевого буфера `history[head]`, оновлює змінні `sum` та `sum_sq`, після чого інкрементує індекс `head = (head + 1) % capacity`.
   * Оновлює `last_timestamp = now`. Складність операції строго `O(1)`, вона не вимагає динамічного виділення пам'яті в гарячому циклі.

2. **Тракт читання (Read Path — методи `phi` та `is_available`):**
   * Викликається робочими потоками маршрутизації безпосередньо перед надсиланням клієнтського запиту або періодичним демоном перевірки членства.
   * Обчислює час очікування `diff = now - last_timestamp - acceptable_pause`.
   * Якщо `diff <= 0`, повертає `Φ = 0.0` (вузол вважається ідеально здоровим).
   * Розраховує `μ` та `σ` з накопичених сум. Якщо елементів недостатньо (`size < 2`), використовує консервативні значення за замовчуванням.
   * Виконує чисельно стійке наближення функції `erfc` або асимптотичний розклад Лапласа для запобігання втраті точності при великих значеннях `diff`.
   * Повертає значення підозри `Φ`.

## Робочий код детектора

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>

#define PHI_DEFAULT_WINDOW_SIZE 1000
#define PHI_DEFAULT_THRESHOLD 8.0
#define PHI_MIN_STD_DEV 0.05
#define PHI_ACCEPTABLE_PAUSE 0.0

typedef struct {
    double *history;
    size_t capacity;
    size_t size;
    size_t head;
    double sum;
    double sum_sq;
    double last_timestamp;
    double threshold;
    double min_std_dev;
} phi_detector_t;

static double get_monotonic_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

phi_detector_t *phi_detector_create(size_t window_size, double threshold, double min_std_dev) {
    phi_detector_t *d = (phi_detector_t *)malloc(sizeof(phi_detector_t));
    if (!d) return NULL;

    d->capacity = (window_size > 0) ? window_size : PHI_DEFAULT_WINDOW_SIZE;
    d->history = (double *)malloc(sizeof(double) * d->capacity);
    if (!d->history) {
        free(d);
        return NULL;
    }

    d->size = 0;
    d->head = 0;
    d->sum = 0.0;
    d->sum_sq = 0.0;
    d->last_timestamp = 0.0;
    d->threshold = (threshold > 0.0) ? threshold : PHI_DEFAULT_THRESHOLD;
    d->min_std_dev = (min_std_dev > 0.0) ? min_std_dev : PHI_MIN_STD_DEV;

    return d;
}

void phi_detector_destroy(phi_detector_t *d) {
    if (d) {
        free(d->history);
        free(d);
    }
}

void phi_detector_heartbeat(phi_detector_t *d, double now_sec) {
    if (now_sec <= 0.0) {
        now_sec = get_monotonic_time_sec();
    }

    if (d->last_timestamp > 0.0) {
        double interval = now_sec - d->last_timestamp;
        if (interval > 0.0) {
            if (d->size < d->capacity) {
                d->history[d->head] = interval;
                d->sum += interval;
                d->sum_sq += interval * interval;
                d->size++;
            } else {
                double old_val = d->history[d->head];
                d->sum = d->sum - old_val + interval;
                d->sum_sq = d->sum_sq - (old_val * old_val) + (interval * interval);
                d->history[d->head] = interval;
            }
            d->head = (d->head + 1) % d->capacity;
        }
    }

    d->last_timestamp = now_sec;
}

double phi_detector_compute_phi(const phi_detector_t *d, double now_sec) {
    if (d->last_timestamp <= 0.0) {
        return 0.0; // Немає жодного сигналу — вузол вважається доступним
    }

    if (now_sec <= 0.0) {
        now_sec = get_monotonic_time_sec();
    }

    double diff = now_sec - d->last_timestamp;
    if (diff <= 0.0) {
        return 0.0;
    }

    // Якщо накопичено менше 2 вибірок, використовуємо значення за замовчуванням
    double mean = 1.0;
    double std_dev = d->min_std_dev;

    if (d->size >= 2) {
        mean = d->sum / (double)d->size;
        double variance = (d->sum_sq / (double)d->size) - (mean * mean);
        if (variance < 0.0) variance = 0.0;
        std_dev = sqrt(variance);
        if (std_dev < d->min_std_dev) {
            std_dev = d->min_std_dev;
        }
    }

    double y = (diff - mean) / std_dev;
    double e = exp(-y * (1.5976 + 0.070566 * y * y));
    
    // Чисельно стійка апроксимація erfc / p_later
    double p_later;
    if (diff > mean) {
        p_later = e / (1.0 + e);
    } else {
        p_later = 1.0 - (1.0 / (1.0 + e));
    }

    if (p_later <= 0.0) {
        // Асимптотичний захист від зникнення порядку при гігантських затримках
        double z = (diff - mean) / (std_dev * 1.41421356237);
        if (z > 3.0) {
            return ((z * z + log(z) + 0.57236) / 2.302585) - 0.30103;
        }
        return 50.0; // Максимальний поріг при критичному перевищенні
    }

    double phi = -log10(p_later);
    return (phi < 0.0) ? 0.0 : phi;
}

bool phi_detector_is_available(const phi_detector_t *d, double now_sec) {
    return phi_detector_compute_phi(d, now_sec) < d->threshold;
}

int main(void) {
    phi_detector_t *det = phi_detector_create(1000, 8.0, 0.05);

    double t = 100.0;
    // Імітація регулярного пульсу (T = 1.0 с) з джиттером ±0.04 с
    for (int i = 0; i < 50; ++i) {
        double jitter = ((double)(i % 5) - 2.0) * 0.02;
        t += 1.0 + jitter;
        phi_detector_heartbeat(det, t);
    }

    printf("Поточний стан після регулярного пульсу:\n");
    printf("Час очікування 1.0с -> Phi = %.4f (Доступний: %s)\n",
           phi_detector_compute_phi(det, t + 1.0),
           phi_detector_is_available(det, t + 1.0) ? "ТАК" : "НІ");

    printf("Час очікування 1.5с -> Phi = %.4f (Доступний: %s)\n",
           phi_detector_compute_phi(det, t + 1.5),
           phi_detector_is_available(det, t + 1.5) ? "ТАК" : "НІ");

    printf("Час очікування 2.5с -> Phi = %.4f (Доступний: %s)\n",
           phi_detector_compute_phi(det, t + 2.5),
           phi_detector_is_available(det, t + 2.5) ? "ТАК" : "НІ");

    phi_detector_destroy(det);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <algorithm>
#include <numbers>

class PhiAccrualFailureDetector {
public:
    explicit PhiAccrualFailureDetector(
        size_t window_size = 1000,
        double threshold = 8.0,
        double min_std_dev_sec = 0.05,
        double acceptable_heartbeat_pause_sec = 0.0
    ) : capacity_(std::max<size_t>(window_size, 10)),
        threshold_(threshold),
        min_std_dev_(min_std_dev_sec),
        acceptable_pause_(acceptable_heartbeat_pause_sec),
        history_(capacity_, 0.0) {}

    void heartbeat(std::chrono::duration<double> timestamp) noexcept {
        const double now = timestamp.count();
        if (last_timestamp_ > 0.0) {
            const double interval = now - last_timestamp_;
            if (interval > 0.0) {
                push_interval(interval);
            }
        }
        last_timestamp_ = now;
    }

    void heartbeat() noexcept {
        const auto now = std::chrono::steady_clock::now().time_since_epoch();
        heartbeat(std::chrono::duration<double>(now));
    }

    [[nodiscard]] double phi(std::chrono::duration<double> timestamp) const noexcept {
        if (last_timestamp_ <= 0.0) {
            return 0.0;
        }

        const double now = timestamp.count();
        const double diff = now - last_timestamp_ - acceptable_pause_;
        if (diff <= 0.0) {
            return 0.0;
        }

        double mean = 1.0;
        double std_dev = min_std_dev_;

        if (size_ >= 2) {
            mean = sum_ / static_cast<double>(size_);
            const double variance = (sum_sq_ / static_cast<double>(size_)) - (mean * mean);
            std_dev = std::max(std::sqrt(std::max(0.0, variance)), min_std_dev_);
        }

        const double y = (diff - mean) / std_dev;
        const double e = std::exp(-y * (1.5976 + 0.070566 * y * y));

        double p_later = (diff > mean) ? (e / (1.0 + e)) : (1.0 - (1.0 / (1.0 + e)));

        if (p_later <= 0.0) {
            // Асимптотичне обчислення при великих затримках для запобігання underflow
            const double z = (diff - mean) / (std_dev * std::numbers::sqrt2);
            if (z > 3.0) {
                return ((z * z + std::log(z) + 0.57236) / std::numbers::ln10) - 0.30103;
            }
            return 50.0;
        }

        const double val = -std::log10(p_later);
        return std::max(0.0, val);
    }

    [[nodiscard]] double phi() const noexcept {
        const auto now = std::chrono::steady_clock::now().time_since_epoch();
        return phi(std::chrono::duration<double>(now));
    }

    [[nodiscard]] bool is_available(std::chrono::duration<double> timestamp) const noexcept {
        return phi(timestamp) < threshold_;
    }

    [[nodiscard]] bool is_available() const noexcept {
        return phi() < threshold_;
    }

    [[nodiscard]] double threshold() const noexcept { return threshold_; }

private:
    void push_interval(double interval) noexcept {
        if (size_ < capacity_) {
            history_[head_] = interval;
            sum_ += interval;
            sum_sq_ += interval * interval;
            ++size_;
        } else {
            const double old_val = history_[head_];
            sum_ = sum_ - old_val + interval;
            sum_sq_ = sum_sq_ - (old_val * old_val) + (interval * interval);
            history_[head_] = interval;
        }
        head_ = (head_ + 1) % capacity_;
    }

    size_t capacity_;
    double threshold_;
    double min_std_dev_;
    double acceptable_pause_;

    std::vector<double> history_;
    size_t size_{0};
    size_t head_{0};
    double sum_{0.0};
    double sum_sq_{0.0};
    double last_timestamp_{0.0};
};

int main() {
    PhiAccrualFailureDetector detector(1000, 8.0, 0.05);

    double sim_time = 500.0;
    // Імітація регулярного пульсу (T = 1.0 с)
    for (int i = 0; i < 50; ++i) {
        sim_time += 1.0 + (i % 3 - 1) * 0.01;
        detector.heartbeat(std::chrono::duration<double>(sim_time));
    }

    std::cout << "Аналіз стану після 50 сигналів пульсу:\n";
    for (double delay : {0.8, 1.0, 1.3, 1.8, 2.5}) {
        const auto check_time = std::chrono::duration<double>(sim_time + delay);
        const double current_phi = detector.phi(check_time);
        const bool alive = detector.is_available(check_time);

        std::cout << "Затримка " << delay << " с -> Phi = " 
                  << current_phi << " | Статус: " 
                  << (alive ? "ONLINE" : "OFFLINE (SUSPECTED)") << "\n";
    }

    return 0;
}
```
:::

## Детальний аналіз підводних каменів та виробничі оптимізації

### 1. Накопичення похибки округлення з плаваючою комою

При тривалій роботі у режимі 24/7 (мільйони оновлень вікна) операції `sum = sum - old_val + new_val` у форматі IEEE 754 подвійної точності неминуче накопичують похибку молодших бітів мантиси. 

У рідкісних випадках, коли всі інтервали у вікні стають строго ідентичними, різниця:
```
variance = (sum_sq / N) - (mean * mean)
```
через похибку округлення може дати мікроскопічне від'ємне число порядку `-1e-17`. Пряма передача такого аргументу у функцію `sqrt()` повертає `NaN` (Not a Number), що руйнує подальші обчислення детектора. Щоб гарантувати надійність, дисперсію завжди примусово відсікають знизу нулем за допомогою `fmax(0.0, variance)`. Крім того, у довгоживучих процесах рекомендується раз на `100 000` викликів виконувати повний перерахунок сум безпосереднім сумуванням масиву `history`.

### 2. Вплив пауз планувальника ОС та збирача сміття (Observer Pause)

Якщо вузол-спостерігач зазнає блокуючої паузи збирача сміття (Stop-the-World GC) або зависання віртуальної машини тривалістю 2 секунди, локальний монотонний час зросте на 2 секунди, поки потік спав. Під час пробудження виявиться, що повідомлення від усіх віддалених серверів прострочені на 2 секунди. Якщо не вжити заходів, спостерігач одночасно вважатиме весь кластер мертвим.

Параметр `acceptable_heartbeat_pause_sec` або динамічне відстеження тривалості циклу диспетчера подій (Event Loop Lag) дозволяє автоматично компенсувати затримки на стороні клієнта: час паузи просто віднімається від `diff` перед розрахунком `Φ`.

### 3. Монотонність годинника та системний час

Категорично заборонено використовувати функції астрономічного часу (`gettimeofday()`, `time(NULL)`, `CLOCK_REALTIME`). Демон синхронізації часу NTP може будь-якої миті скоригувати системний годинник назад, що зробить `now < last_timestamp` і дасть від'ємний інтервал `interval < 0`. Детектор зобов'язаний спиратися виключно на монотонний таймер, такий як `CLOCK_MONOTONIC` у Linux або `std::chrono::steady_clock` у C++, які гарантують сувору неспадучість показів незалежно від налаштувань часових поясів та корекцій високосних секунд.

### 4. Продуктивність та масштабування пам'яті на тисячі вузлів

У великих хмарних кластерах на тисячі серверів кожен вузол підтримує окремий екземпляр детектора для кожного віддаленого сусіда:
* **Накладні витрати пам'яті:** Буфер із `W = 1000` значень `double` займає рівно 8 кілобайтів. Для кластера з `N = 1000` вузлів сумарний обсяг пам'яті під усі детектори становить приблизно `8 МБ`, що повністю поміщається в кеш L3 сучасного серверного процесора.
* **Обчислювальна складність:** Виклик `phi()` вимагає близько 15–20 наносекунд на архітектурі x86_64 завдяки швидкій раціональній апроксимації експоненти, що дозволяє виконувати понад 50 мільйонів перевірок на секунду на одне процесорне ядро.

### 5. Патерни багатопотоковості без блокувань (Lock-Free Read Path)

Коли сотні робочих потоків одночасно перевіряють стан віддалених серверів перед надсиланням запитів, класичні м'ютекси стають джерелом конкуренції (lock contention).

Оптимальний архітектурний шаблон передбачає поділ стану на дві частини:
1. Кільцевий буфер та змінні накопичувачів `sum` і `sum_sq` оновлюються виключно одним мережевим потоком при виклику `heartbeat()`.
2. Поточні вибіркове середнє `μ`, стандартне відхилення `σ` та мітка `last_timestamp` публікуються у вигляді незмінної структури через атомарний покажчик `std::atomic<const Snapshot*>`. Робочі потоки зчитують знімок без блокувань, обчислюють `phi()` локально на стеку потоку і не створюють жодних затримок для інших запитів.
