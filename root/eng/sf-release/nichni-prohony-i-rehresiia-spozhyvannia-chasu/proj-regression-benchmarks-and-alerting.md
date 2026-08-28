# ⚙️ Практичний стенд вимірювання регресій та сповіщень: від зняття профілю до авто-bisect

Побудова промислового конвеєра нічного тестування вимагає інтеграції двох взаємодоповнюючих інженерних компонентів:
1. **Низькорівневий зонд телеметрії (Target Probe)**: вбудований у прошивку або системний демон модуль, який у режимі реального часу відстежує стан динамічної купи, таймінги обробки переривань та формує структуровані звіти без значного впливу на продуктивність.
2. **Хостовий оркестратор регресій (Nightly Runner & Bisector)**: сценарій автоматизації, який керує фізичним живленням стенду, збирає вимірювання струму з аналізатора, аналізує деградацію за алгоритмом CUSUM та автоматично запускає бінарний пошук `git bisect` для знаходження винного коміту.

Нижче наведено повну робочу реалізацію обох частин системи з детальним розбором алгоритмічних та архітектурних рішень.

---

## 1. Зонд моніторингу динамічної купи та часу реакції (Target System)

Стандартний інтерфейс POSIX `mallinfo2()` повертає загальний обсяг вільної пам'яті (`fordblks`), що утримується менеджером пам'яті. Проте він не надає інформації про ступінь фрагментації — тобто розмір найбільшого неперервного шматка пам'яті, який можна виділити одним викликом `malloc()`. У багатьох вбудованих середовищах (наприклад, FreeRTOS або bare-metal ARM Cortex-M) доступні функції повертають лише загальну кількість вільних байтів через `xPortGetFreeHeapSize()`, але приховують внутрішній стан ланцюжка вільних блоків.

Для вирішення цієї задачі зонд реалізує алгоритм **бінарного зондування купи** (Binary Memory Probing). Замість лінійного перебору, який забирав би тисячі циклів процесора і міг спричинити неприпустимі затримки в системі реального часу, зонд за логарифмічну кількість спроб `O(log M)` знаходить точну верхню межу доступного блоку:
- Зонд обирає тестовий розмір блоку як середину між відомими межами `[low, high]`. Початкова верхня межа `high` встановлюється рівною загальному відомому обсягу вільної пам'яті `total_free_bytes`.
- Виконується пробний виклик `malloc(mid)`.
- Якщо виділення успішне (повернуто ненульовий вказівник `ptr != NULL`), пам'ять негайно звільняється викликом `free(ptr)`, а нижня межа інтервалу пошуку зсувається вгору: `low = mid + 1`, фіксуючи поточний успішний розмір `max_success = mid`.
- Якщо алокатор повернув `NULL` через відсутність неперервної ділянки запитаного розміру, верхня межа зменшується: `high = mid - 1`.

Такий підхід виконується менш ніж за 18 ітерацій для пулу пам'яті розміром у 128 кілобайтів і менш ніж за 24 ітерації для адресного простору в 16 мегабайтів. Оскільки кожен успішно виділений блок негайно повертається в алокатор до початку наступної спроби, структура купи не зазнає постійних змін, а навантаження на систему залишається мікроскопічним.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <malloc.h>
#include <time.h>

typedef struct {
    uint64_t timestamp_ms;
    size_t total_free_bytes;
    size_t max_contiguous_free_bytes;
    double fragmentation_index;
    uint32_t max_isr_latency_us;
} MemoryTelemetry;

/* Визначення найбільшого доступного неперервного блоку в купі методом бінарного зондування */
static size_t probe_max_contiguous_block(size_t upper_bound) {
    size_t low = 0;
    size_t high = upper_bound;
    size_t max_success = 0;

    while (low <= high) {
        size_t mid = low + (high - low) / 2;
        if (mid == 0) {
            low = 1;
            continue;
        }

        void* ptr = malloc(mid);
        if (ptr != NULL) {
            max_success = mid;
            free(ptr);
            low = mid + 1; /* Пробуємо виділити більший блок */
        } else {
            if (mid == 0) break;
            high = mid - 1; /* Зменшуємо запит */
        }
    }
    return max_success;
}

MemoryTelemetry capture_heap_telemetry(uint32_t isr_latency_us) {
    MemoryTelemetry report;
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    report.timestamp_ms = (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;

    struct mallinfo2 info = mallinfo2();
    /* fordblks — загальний обсяг вільної пам'яті, що утримується алокатором */
    report.total_free_bytes = info.fordblks;

    /* Зондуємо найбільший блок у межах відомого вільного обсягу */
    report.max_contiguous_free_bytes = probe_max_contiguous_block(report.total_free_bytes);

    if (report.total_free_bytes > 0) {
        report.fragmentation_index = 1.0 - ((double)report.max_contiguous_free_bytes / (double)report.total_free_bytes);
    } else {
        report.fragmentation_index = 1.0;
    }

    report.max_isr_latency_us = isr_latency_us;
    return report;
}

void emit_telemetry_json(const MemoryTelemetry* rep) {
    printf("{\"type\":\"soak_telemetry\",\"ts\":%llu,\"free_bytes\":%zu,\"max_block\":%zu,\"frag_idx\":%.4f,\"max_latency_us\":%u}\n",
           (unsigned long long)rep->timestamp_ms,
           rep->total_free_bytes,
           rep->max_contiguous_free_bytes,
           rep->fragmentation_index,
           rep->max_isr_latency_us);
    fflush(stdout);
}
```
```cpp
#include <iostream>
#include <chrono>
#include <optional>
#include <malloc.h>
#include <cstdint>
#include <string_view>
#include <format>

struct MemoryTelemetry {
    uint64_t timestamp_ms{0};
    std::size_t total_free_bytes{0};
    std::size_t max_contiguous_free_bytes{0};
    double fragmentation_index{0.0};
    uint32_t max_isr_latency_us{0};
};

class SystemProbe {
public:
    static MemoryTelemetry capture(uint32_t isr_latency_us) noexcept {
        MemoryTelemetry report;
        const auto now = std::chrono::steady_clock::now().time_since_epoch();
        report.timestamp_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now).count();

        const struct mallinfo2 info = mallinfo2();
        report.total_free_bytes = static_cast<std::size_t>(info.fordblks);
        report.max_contiguous_free_bytes = probe_max_block(report.total_free_bytes);

        if (report.total_free_bytes > 0) {
            report.fragmentation_index = 1.0 - (static_cast<double>(report.max_contiguous_free_bytes) /
                                                static_cast<double>(report.total_free_bytes));
        } else {
            report.fragmentation_index = 1.0;
        }

        report.max_isr_latency_us = isr_latency_us;
        return report;
    }

    static void emit_json(const MemoryTelemetry& rep) {
        std::cout << "{\"type\":\"soak_telemetry\","
                  << "\"ts\":" << rep.timestamp_ms << ","
                  << "\"free_bytes\":" << rep.total_free_bytes << ","
                  << "\"max_block\":" << rep.max_contiguous_free_bytes << ","
                  << "\"frag_idx\":" << rep.fragmentation_index << ","
                  << "\"max_latency_us\":" << rep.max_isr_latency_us << "}\n"
                  << std::flush;
    }

private:
    static std::size_t probe_max_block(std::size_t upper_bound) noexcept {
        std::size_t low = 0;
        std::size_t high = upper_bound;
        std::size_t max_success = 0;

        while (low <= high) {
            const std::size_t mid = low + (high - low) / 2;
            if (mid == 0) {
                low = 1;
                continue;
            }

            void* ptr = ::malloc(mid);
            if (ptr != nullptr) {
                max_success = mid;
                ::free(ptr);
                low = mid + 1;
            } else {
                if (mid == 0) break;
                high = mid - 1;
            }
        }
        return max_success;
    }
};
```
:::

---

## 2. Хостовий оркестратор: статистичний аналізатор CUSUM та авто-bisect

Хостовий сценарій мовою Python виконує роль головного керуючого вузла тестового стенду. Він виконує три критичні інженерні задачі:
1. **Чисельне інтегрування фізичного профілю струму**: функція `integrate_power_energy()` розраховує повну спожиту енергію за методом трапецій. Вона перетворює сирий масив миттєвих вимірів струму від цифрового профайлера (у міліамперах) з урахуванням напруги живлення на інтегральну роботу в джоулях та середню потужність стенду в міліватах.
2. **Статистичний контроль CUSUM**: клас `CusumDetector` реалізує накопичення кумулятивної суми відхилень від історичного еталонного значення `mu0` з урахуванням дисперсії шуму `sigma`. Коли накопичена сума перевищує поріг прийняття рішення `h = 4.5 * sigma`, генератор формує подію апаратного алерту.
3. **Автоматичний бінарний пошук `git bisect`**: при фіксації регресії функція `run_automated_bisect()` ініціалізує автоматичну локалізацію несправного коміту між останнім відомим стабільним станом (`good_commit`) та поточною нічною збіркою (`bad_commit`). Команда `git bisect run` автономно перемикає репозиторій між комітами, викликає скрипт компіляції та швидкого прогону і повертає точний SHA-хеш коміту, що вніс деградацію.

```python
#!/usr/bin/env python3
"""
Nightly Regression Runner with CUSUM Analysis and Automated Git Bisect.
"""
import sys
import json
import subprocess
import dataclasses
from typing import List, Optional, Tuple


@dataclasses.dataclass
class BaselineProfile:
    mean_power_mw: float
    std_power_mw: float
    max_frag_index: float
    p99_latency_us: float


class CusumDetector:
    def __init__(self, target_mean: float, std_dev: float, slack_delta: float = 1.0, threshold_h: float = 4.5):
        self.mu0 = target_mean
        self.sigma = max(std_dev, 1e-6)
        self.k = (slack_delta * self.sigma) / 2.0
        self.h = threshold_h * self.sigma
        self.c_plus = 0.0
        self.c_minus = 0.0

    def update(self, value: float) -> Tuple[bool, float]:
        """Оновлення статистики CUSUM. Повертає (is_alert, c_plus)."""
        self.c_plus = max(0.0, self.c_plus + (value - self.mu0) - self.k)
        self.c_minus = max(0.0, self.c_minus - (value - self.mu0) - self.k)
        is_alert = self.c_plus > self.h
        return is_alert, self.c_plus


def integrate_power_energy(current_samples_ma: List[float], voltage_v: float = 3.3, sample_rate_hz: float = 1000.0) -> Tuple[float, float]:
    """Чисельне інтегрування енергії за методом трапецій."""
    if len(current_samples_ma) < 2:
        return 0.0, 0.0

    dt = 1.0 / sample_rate_hz
    # Переведення струму з мА в А: I_A = I_mA / 1000.0
    # Потужність P = V * I (Вт)
    power_w = [(voltage_v * i_ma / 1000.0) for i_ma in current_samples_ma]
    
    # Інтеграл трапецій: E = dt * ( (P[0] + P[-1])/2 + sum(P[1:-1]) )
    energy_joules = dt * ((power_w[0] + power_w[-1]) / 2.0 + sum(power_w[1:-1]))
    total_time_s = len(current_samples_ma) * dt
    avg_power_mw = (energy_joules / total_time_s) * 1000.0

    return energy_joules, avg_power_mw


def run_automated_bisect(good_commit: str, bad_commit: str, test_command: str) -> Optional[str]:
    """Автоматичний запуск git bisect для виявлення коміту, що вніс регресію."""
    print(f"[*] Starting git bisect between GOOD={good_commit} and BAD={bad_commit}")
    try:
        subprocess.run(["git", "bisect", "reset"], check=False)
        subprocess.run(["git", "bisect", "start", bad_commit, good_commit], check=True)
        
        # Запуск бінарного пошуку за скриптом тестування
        result = subprocess.run(
            ["git", "bisect", "run", "bash", "-c", test_command],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if "is the first bad commit" in line:
                bad_hash = line.split()[0]
                print(f"[!] Regression culprit isolated: {bad_hash}")
                return bad_hash
    except subprocess.CalledProcessError as e:
        print(f"[-] Bisect failed with error: {e}")
    finally:
        subprocess.run(["git", "bisect", "reset"], check=False)
    return None


def main():
    baseline = BaselineProfile(
        mean_power_mw=12.5,
        std_power_mw=0.8,
        max_frag_index=0.35,
        p99_latency_us=450.0
    )

    detector = CusumDetector(target_mean=baseline.mean_power_mw, std_dev=baseline.std_power_mw)

    # Імітація серії вимірів нічного прогону
    simulated_current_ma = [3.8] * 500 + [18.2] * 20 + [3.8] * 480
    energy_j, avg_power_mw = integrate_power_energy(simulated_current_ma, voltage_v=3.3, sample_rate_hz=100.0)

    print(f"[+] Total Energy: {energy_j:.4f} Joules, Average Power: {avg_power_mw:.2f} mW")
    is_alert, cusum_stat = detector.update(avg_power_mw)

    if is_alert:
        print(f"[ALERT] Power Regression Detected! CUSUM statistic: {cusum_stat:.2f} > Threshold")
        culprit = run_automated_bisect(
            good_commit="HEAD~10",
            bad_commit="HEAD",
            test_command="python scripts/single_run_benchmark.py --max-power-mw 14.0"
        )
        sys.exit(1 if culprit else 2)
    else:
        print(f"[OK] Nightly run within baseline. CUSUM: {cusum_stat:.2f}")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## 3. Інтеграція в конвеєр нічної автоматизації

Для запуску стенду в повністю автономному режимі оркестратор реєструється у планувальнику задач CI/CD (наприклад, GitLab Runner або Jenkins Agent). Процес інтеграції складається з чотирьох обов'язкових кроків:

1. **Захоплення ексклюзивного блокування апаратного стенду (Hardware Mutex)**: оскільки до одного фізичного профайлера живлення та тестової плати не можуть одночасно звертатися кілька процесів збірки, раннер створює системний файл блокування `flock /var/lock/hil_bench_01.lock`. Якщо стенд зайнятий іншим тривалим прогоном, новий процес коректно очікує черги або надсилає сповіщення про перевантаження лабораторії.
2. **Прошивка бінарного артефакту та перевірка цілісності**: за допомогою системного відлагоджувача `openocd` або `pyocd` на цільовий мікроконтролер записується скомпільований двійковий образ нічної збірки. Обов'язково виконується зчитування контрольної суми CRC32 флеш-пам'яті для виключення апаратних помилок запису напівпровідника.
3. **Холостий прогрів (Warm-up Period)**: перші 60 секунд після старту прошивки зібрані метрики не враховуються в статистиці регресії. Цей період необхідний для стабілізації перехідних процесів: ініціалізації файлової системи, монтажу накопичувачів, калібрування нульових рівнів аналогових давачів та встановлення початкових мережевих з'єднань.
4. **Формування артефактів та експорт у дашборди**: по завершенню випробувальної сесії результуючий JSON-звіт публікується у внутрішньому сховищі артефактів S3/Artifactory. Числові ряди передаються у часові бази даних (Prometheus / InfluxDB) для візуалізації на дашбордах Grafana, які щоранку переглядає черговий системний архітектор.
