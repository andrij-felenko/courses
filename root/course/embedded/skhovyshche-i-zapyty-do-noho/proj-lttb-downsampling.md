# ⚙️ Алгоритм LTTB: проріджування часових рядів для візуалізації

Коли сервер надсилає браузеру або мобільному застосунку історію телеметрії для побудови графіка, передача мільйона сирих точок перевантажує мережу, споживає сотні мегабайтів пам'яті й заморожує графічний рушій рендерингу. Водночас екранний графік завширшки 1200 пікселів фізично не здатний відобразити понад 1200 незалежних колонок точок. Звичайне наївне децимування (вибірка кожної `N`-ї точки) або обчислення простого середнього (`AVG`) у бакетах зрізає вузькі аварійні спайки й спотворює візуальні екстремуми. Алгоритм LTTB (*Largest Triangle Three Buckets*, Sveinn Steinarsson, 2013) розв'язує цю задачу: він стискає масив із сотень тисяч точок до фіксованої кількості бакетів, гарантовано зберігаючи візуальну форму кривої та всі гострі локальні піки.

Цей інженерний проєкт реалізує високопродуктивне LTTB-проріджування для потокових даних і бекенд-сервісів, розбирає його геометричну математику, порівнює з класичними алгоритмами спрощення ліній та показує пастки обробки нерівномірних часових рядів.

## Чому класичні алгоритми спрощення не підходять для часових рядів

В обчислювальній геометрії десятиліттями використовувалися два відомі алгоритми спрощення поліліній: Рамера–Дугласа–Пекера (*Ramer–Douglas–Peucker, RDP*) та Візвалінгама–Вайатта (*Visvalingam–Whyatt*). Проте для інтерактивних панелей моніторингу та вебграфіків часових рядів обидва мають критичні архітектурні вади:

1. **Недетермінований розмір вибірки (RDP):**
   Алгоритм Рамера–Дугласа–Пекера приймає як параметр просторову похибку `ε` (*epsilon*). Він видаляє точки, доки перпендикулярна відстань до хорди не перевищує `ε`. Проблема в тому, що наперед неможливо передбачити, скільки точок залишиться на виході. Для гладкого сигналу `ε = 0.5` залишить 50 точок, а для зашумленого сигналу той самий `ε` поверне 80 000 точок, що перевантажить клієнтський браузер. Щоб отримати рівно 1200 точок під ширину екрана, довелося б ітеративно підбирати `ε` бінарним пошуком, багаторазово перераховуючи весь масив. Крім того, часова складність RDP у найгіршому випадку становить `O(N²)`, а в середньому — `O(N log N)`.

2. **Втрата локальних екстремумів при глобальному видаленні (Visvalingam–Whyatt):**
   Алгоритм Візвалінгама поступово видаляє вершини з найменшою площею трикутника, утвореного сусідніми точками. Він дозволяє задати точну кількість вихідних точок `K`, але вимагає використання пріоритетної черги (*Min-Heap*), що дає складність `O(N log N)` і високі накладні витрати на виділення динамічної пам'яті. Головний візуальний дефект: якщо на сигналі є локальний високочастотний шум, алгоритм може повністю стерти значущий аварійний імпульс, якщо його трикутник виявився меншим за глобальний тренд.

3. **Перевага LTTB:**
   Алгоритм LTTB розбиває дані на локальні бакети і працює за строгий лінійний час `O(N)` з константною додатковою пам'яттю `O(1)` (без динамічних алокацій у процесі сканування). Він гарантує повернення рівно `K` точок і зберігає як глобальний тренд, так і локальні піки.

## Геометричний принцип максимізації площі трикутника

Вхідний масив складається з `N` пар `(t[i], v[i])`, де `t` — монотонно зростаюча мітка часу, а `v` — виміряна величина (температура, напруга, струм). Нам потрібно отримати вихідний масив із `K` точок (`K < N`).

Перша точка вхідного ряду `(t[0], v[0])` та остання `(t[N-1], v[N-1])` завжди входять до вибірки без змін. Решта `N - 2` внутрішніх точок розбиваються на `K - 2` однакових за розміром бакетів. Розмір одного бакета становить:

```
размір_бакета = (N - 2) / (K - 2)
```

Для кожного поточного бакета `B[i]` алгоритм обирає рівно одну точку `P`. Критерій вибору — максимальна площа трикутника, утвореного трьома вершинами:
1. Точкою `A`, уже зафіксованою на попередньому кроці в бакеті `B[i-1]` (на найпершому кроці це точка `data[0]`).
2. Кандидатом `P ∈ B[i]`.
3. Усередненою віртуальною точкою `C`, розрахованою як центр мас наступного бакета `B[i+1]`:

```
C_t = (1 / |B[i+1]|) · ∑ t[j]    [для всіх j ∈ B[i+1]]
C_v = (1 / |B[i+1]|) · ∑ v[j]    [для всіх j ∈ B[i+1]]
```

Площа трикутника `S(A, P, C)` обчислюється через векторний добуток:

```
S = 0.5 · | (A_t - C_t)·(P_v - A_v) - (A_t - P_t)·(C_v - A_v) |
```

Множник `0.5` є константою і не впливає на точку максимуму, тому в програмній реалізації його відкидають, порівнюючи подвоєні площі. Точка `P`, на якій площа досягає максимуму, додається до результуючого масиву і стає опорною вершиною `A` для наступного кроку.

Оскільки трикутник із витягнутим убік спайком має найбільшу геометричну висоту, алгоритм гарантовано обирає саме аварійні піки та провали, ігноруючи монотонні плато.

## Реалізація алгоритму

Нижче наведено дві взаємодоповнюючі реалізації: оптимізована функція на Python для інтеграції в асинхронні бекенди та високопродуктивна ідіоматична бібліотека на C і C++ для вбудованих шлюзів і швидкісних демонів обробки телеметрії.

:::tabs
```py
from typing import List, Tuple

def lttb_downsample(data: List[Tuple[float, float]], threshold: int) -> List[Tuple[float, float]]:
    """
    Проріджування часового ряду алгоритмом LTTB.
    :param data: список пар (timestamp, value), відсортований за часом.
    :param threshold: бажана кількість точок на виході (K).
    :return: проріджений список пар довжиною threshold.
    """
    n = len(data)
    if threshold >= n or threshold < 3:
        return data

    sampled: List[Tuple[float, float]] = [data[0]]
    bucket_size = (n - 2) / (threshold - 2)

    a_idx = 0  # Індекс зафіксованої точки попереднього кроку (A)

    for i in range(threshold - 2):
        # Межі поточного бакета
        curr_start = int((i * bucket_size) + 1)
        curr_end = int(((i + 1) * bucket_size) + 1)
        curr_end = min(curr_end, n)

        # Межі наступного бакета для обчислення центру мас (C)
        next_start = int(((i + 1) * bucket_size) + 1)
        next_end = int(((i + 2) * bucket_size) + 1)
        next_end = min(next_end, n)

        # Розрахунок центру мас C(avg_t, avg_v)
        avg_t = 0.0
        avg_v = 0.0
        next_count = next_end - next_start

        if next_count > 0:
            for j in range(next_start, next_end):
                avg_t += data[j][0]
                avg_v += data[j][1]
            avg_t /= next_count
            avg_v /= next_count
        else:
            avg_t = data[-1][0]
            avg_v = data[-1][1]

        # Пошук точки P у поточному бакеті з максимальною площею трикутника
        a_t, a_v = data[a_idx]
        max_area = -1.0
        max_idx = curr_start

        for p_idx in range(curr_start, curr_end):
            p_t, p_v = data[p_idx]
            # Подвійна площа трикутника APC
            area = abs((a_t - avg_t) * (p_v - a_v) - (a_t - p_t) * (avg_v - a_v))
            if area > max_area:
                max_area = area
                max_idx = p_idx

        sampled.append(data[max_idx])
        a_idx = max_idx  # Вибрана точка стає точкою A на наступній ітерації

    sampled.append(data[-1])  # Остання точка ряду
    return sampled
```
```c
#include <stddef.h>
#include <math.h>

typedef struct {
    double time;
    double value;
} data_point_t;

size_t lttb_downsample_c(const data_point_t *input, size_t input_len,
                         data_point_t *output, size_t threshold) {
    if (input == NULL || output == NULL || input_len == 0) return 0;
    if (threshold >= input_len || threshold < 3) {
        for (size_t i = 0; i < input_len; ++i) output[i] = input[i];
        return input_len;
    }

    output[0] = input[0];
    size_t out_idx = 1;
    size_t a_idx = 0;
    double bucket_size = (double)(input_len - 2) / (double)(threshold - 2);

    for (size_t i = 0; i < threshold - 2; ++i) {
        size_t curr_start = (size_t)(i * bucket_size) + 1;
        size_t curr_end = (size_t)((i + 1) * bucket_size) + 1;
        if (curr_end > input_len) curr_end = input_len;

        size_t next_start = (size_t)((i + 1) * bucket_size) + 1;
        size_t next_end = (size_t)((i + 2) * bucket_size) + 1;
        if (next_end > input_len) next_end = input_len;

        double avg_t = 0.0, avg_v = 0.0;
        size_t next_count = next_end - next_start;

        if (next_count > 0) {
            for (size_t j = next_start; j < next_end; ++j) {
                avg_t += input[j].time;
                avg_v += input[j].value;
            }
            avg_t /= (double)next_count;
            avg_v /= (double)next_count;
        } else {
            avg_t = input[input_len - 1].time;
            avg_v = input[input_len - 1].value;
        }

        double a_t = input[a_idx].time;
        double a_v = input[a_idx].value;
        double max_area = -1.0;
        size_t max_idx = curr_start;

        for (size_t p = curr_start; p < curr_end; ++p) {
            double p_t = input[p].time;
            double p_v = input[p].value;
            double area = fabs((a_t - avg_t) * (p_v - a_v) - (a_t - p_t) * (avg_v - a_v));
            if (area > max_area) {
                max_area = area;
                max_idx = p;
            }
        }

        output[out_idx++] = input[max_idx];
        a_idx = max_idx;
    }

    output[out_idx++] = input[input_len - 1];
    return out_idx;
}
```
```cpp
#include <span>
#include <vector>
#include <cmath>
#include <algorithm>

struct DataPoint {
    double time;
    double value;
};

std::vector<DataPoint> lttbDownsample(std::span<const DataPoint> input, std::size_t threshold) {
    if (input.empty()) return {};
    if (threshold >= input.size() || threshold < 3) {
        return std::vector<DataPoint>(input.begin(), input.end());
    }

    std::vector<DataPoint> sampled;
    sampled.reserve(threshold);
    sampled.push_back(input.front());

    const double bucket_size = static_cast<double>(input.size() - 2) / static_cast<double>(threshold - 2);
    std::size_t a_idx = 0;

    for (std::size_t i = 0; i < threshold - 2; ++i) {
        const std::size_t curr_start = static_cast<std::size_t>(i * bucket_size) + 1;
        const std::size_t curr_end = std::min(static_cast<std::size_t>((i + 1) * bucket_size) + 1, input.size());

        const std::size_t next_start = std::min(static_cast<std::size_t>((i + 1) * bucket_size) + 1, input.size());
        const std::size_t next_end = std::min(static_cast<std::size_t>((i + 2) * bucket_size) + 1, input.size());

        double avg_t = 0.0;
        double avg_v = 0.0;
        const std::size_t next_count = next_end - next_start;

        if (next_count > 0) {
            for (std::size_t j = next_start; j < next_end; ++j) {
                avg_t += input[j].time;
                avg_v += input[j].value;
            }
            avg_t /= static_cast<double>(next_count);
            avg_v /= static_cast<double>(next_count);
        } else {
            avg_t = input.back().time;
            avg_v = input.back().value;
        }

        const double a_t = input[a_idx].time;
        const double a_v = input[a_idx].value;
        double max_area = -1.0;
        std::size_t max_idx = curr_start;

        for (std::size_t p = curr_start; p < curr_end; ++p) {
            const double p_t = input[p].time;
            const double p_v = input[p].value;
            const double area = std::abs((a_t - avg_t) * (p_v - a_v) - (a_t - p_t) * (avg_v - a_v));
            if (area > max_area) {
                max_area = area;
                max_idx = p;
            }
        }

        sampled.push_back(input[max_idx]);
        a_idx = max_idx;
    }

    sampled.push_back(input.back());
    return sampled;
}
```
:::

## Інженерні пастки та оптимізація продуктивності

1. **Неспівмірні шкали осей X та Y:**
   Мітка часу `t` вимірюється в секундах від початку епохи Unix (порядку `1.7 · 10⁹`), тоді як напруга чи температура — невеликі числа (`20.5`, `3.3`). Якщо обчислювати площу напряму в абсолютних значеннях без нормалізації, великі числа `t` можуть призвести до переповнення проміжних значень або втрати точності в операціях з плаваючою комою. У C/C++ коді мітки часу перед обчисленням площі рекомендується зсувати відносно `input[0].time`, щоб `t` стартувало з нуля.

2. **Недійсні значення (`NaN` / `NULL`):**
   Якщо давач дав збій і повернув `NaN`, будь-яке порівняння `area > max_area` повертатиме `false`. У результаті `max_idx` не оновиться, і алгоритм візьме першу точку бакета або спричинить розрив графіка. Перед проріджуванням значення `NaN` або видаляють із масиву, або замінюють лінійною інтерполяцією між сусідніми валідними точками.

3. **Потокове проріджування великих файлів (Streaming Chunks):**
   Коли розмір сирого масиву перевищує обсяг оперативної пам'яті (наприклад, файл експорту на 50 мільйонів точок), LTTB застосовують блочно: читають файл порціями по 100 000 точок, кожну порцію проріджують до 2000 точок, а потім фінально проріджують накопичений проміжний масив до бажаних 1200 точок. Двопрохідне проріджування зберігає форму сигналу з точністю понад 99.5%, але вкладається в лічені мегабайти оперативної пам'яті.
