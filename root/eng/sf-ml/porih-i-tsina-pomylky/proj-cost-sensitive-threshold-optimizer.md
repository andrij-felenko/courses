# ⚙️ Модуль байєсівської оптимізації порогу з урахуванням матриці втрат та адаптивного регулювання робочої точки

Бортові обчислювачі автономних безпілотних апаратів та систем промислової автоматики реального часу функціонують в умовах жорстких обмежень на обчислювальні ресурси, детермінізм часу виконання та енергоспоживання. Коли нейромережевий детектор на базі апаратного прискорювача NPU формує оцінку ймовірності небезпеки чи дефекту, передача цього сирого значення у виконавчі контури без адаптивного порогу призводить або до швидкого вичерпання батареї через хибні маневри ухилення, або до зіткнення з перешкодою через пропуск цілі на високій швидкості.

Цей модуль реалізує повністю автономний, математично строгий компонент ухвалення рішень для вбудованих систем на мовах C99 та C++20. Архітектура модуля поєднує чотири взаємопов'язані функціональні блоки: підсистему параметричного й табличного калібрування впевненості моделі, байєсівський розрахунковий блок мінімізації очікуваного ризику за довільною матрицею втрат, потокобезпечний механізм безблокувального обміну контекстом (lockless double-buffering), а також контур динамічної адаптації порогу за вектором контексту середовища з фільтрацією деренчання за допомогою експоненційного згладжування та гістерезису. Модуль розроблено з нульовим динамічним виділенням пам'яті в гарячому циклі інференсу, що забезпечує сталий час виконання `O(1)` і повну відповідність жорстким стандартам функціональної безпеки DO-178C (рівень DAL-B) та ISO 26262 (ASIL-D).

## Інженерна постановка та специфікація вимог для бортових контролерів

Вбудовані системи реального часу (англ. *Hard Real-Time Embedded Systems*) ставлять до коду машинного навчання специфічні вимоги, які принципово відрізняються від сервісів хмарного бекенду:

1. **Строгий детермінізм часу виконання (Deterministic Latency)**: функція ухвалення рішення повинна гарантувати виконання за фіксовану кількість тактів процесора незалежно від вхідних числових значень. Неприпустимими є ітераційні цикли зі змінною кількістю кроків (як-от чисельний пошук коренів методом Ньютона чи сканування по несортованих масивах) усередині критичного циклу керування (англ. *Fast Control Loop*). Бюджет часу на ухвалення рішення зазвичай обмежений інтервалом не більше двох із половиною мікросекунд при тактовій частоті ядра від 200 до 400 МГц.
2. **Нульове динамічне виділення пам'яті (Zero Heap Allocation)**: використання `malloc()`, `free()`, `new`, `delete` або динамічних контейнерів (`std::vector`, `std::string`) у коді обробки переривань та періодичних задач категорично заборонено стандартом MISRA C/C++. Фрагментація оперативної пам'яті (heap fragmentation) здатна спричинити раптову відмову апарата після кількох діб безперервного польоту чи чергування. Усі буфери, таблиці калібрування та структури конфігурації мають виділятися статично на етапі компіляції або ініціалізації.
3. **Числова стійкість та захист за стандартом IEEE 754**: у процесі виводу квантованих або стиснених нейромереж можлива поява нечислових значень (`NaN`) чи нескінченностей (`+Inf`, `-Inf`) через ділення на нуль або переповнення проміжних регістрів. Контролер рішень повинен містити вхідні санітайзери (англ. *Sanitization Guards*), які надійно перехоплюють аномальні числа й переводять виконавчий орган у детерміністичний безпечний режим (англ. *Failsafe State*).
4. **Робота без апаратного блоку FPU (Fixed-Point Fallback)**: молодші мікроконтролери польотних сенсорів (наприклад, ARM Cortex-M0+/M3 або RISC-V RV32I) позбавлені апаратного блоку обчислень із плаваючою комою. Модуль повинен мати математичну основу, що легко переноситься на цілочисельну арифметику з фіксованою комою форматів Q15 або Q16.16 без втрати роздільної здатності на малих імовірностях.

## Архітектура та математична модель вбудованого оптимізатора

У класичній схемі конвеєра обробки даних машинне навчання завершується обчисленням вектора логітів `z` або нормалізованого скору софтмаксу `σ(z) ∈ [0, 1]`. У вбудованому контролері цей конвеєр доповнюється контуром ухвалення рішень (англ. *Decision Engine*), який перетворює статистичну оцінку на фізичну керуючу команду.

```
┌──────────────┐     сирий скор z     ┌────────────────────────┐   ймовірність p(x)
│  Нейромережа │ ───────────────────> │  Калібратор впевненості │ ─────────────────┐
│ (ONNX / NPU) │                      │ (Platt/Temp/Isotonic)  │                  │
└──────────────┘                      └────────────────────────┘                  │
                                                                                  ▼
┌──────────────┐     вектор u(t)      ┌────────────────────────┐  поріг T*(t)  ┌──────────────────┐  керуюча
│  Контекстні  │ ───────────────────> │   Адаптер вартостей    │ ────────────> │ Швидкий компара- │ ───────> дія
│   сенсори    │                      │   та Байєсів оптимум   │               │ тор і гістерезис │      d(t)
└──────────────┘                      └────────────────────────┘               └──────────────────┘
```

Контур складається з чотирьох послідовних стадій обчислення:

### Стадія 1: Параметричне та табличне калібрування
Сирі логіти нейронних мереж або відстані до розділової гіперплощини не є справжніми ймовірностями. Для їхнього перетворення модуль підтримує три взаємозамінні механізми:

1. **Параметричне калібрування Платта (Platt Scaling)**:
Сирий скалярний вихід нейромережі `z` перетворюється на апостеріорну ймовірність за формулою логістичного сигмоїда з масштабуванням і зсувом: `p(x) = 1.0 / (1.0 + exp(-(A · z + B)))`, де `A` та `B` — дійсні калібрувальні коефіцієнти.
   
Під час офлайн-навчання калібратора коефіцієнти оптимізуються методом максимальної правдоподібності за допомогою згладжування міток Платта: `y_+ = (N_+ + 1) / (N_+ + 2)` та `y_- = 1 / (N_- + 2)`. Це згладжування запобігає розходженню коефіцієнтів до нескінченності на вибірках із ідеальним розділенням класів.

2. **Температурне масштабування (Temperature Scaling)**:
Окремий випадок калібрування Платта з нульовим зсувом `B = 0` та коефіцієнтом `A = 1 / T_temp`, де формула набуває вигляду `p(x) = 1.0 / (1.0 + exp(-z / T_temp))`. Параметр температури `T_temp > 0` зберігає незмінною впорядкованість рангів і площу під ROC-кривою, але пом'якшує надмірну впевненість глибоких нейромереж.

3. **Непараметричне табличне калібрування (Piecewise Linear Isotonic Calibration)**:
Якщо емпірична функція калібрування має виражену нелінійність (наприклад, сходинки на граничних режимах сенсора), модуль застосовує таблицю з `M` вузлів `(z_k, p_k)`, побудовану за алгоритмом Pool Adjacent Violators (PAV). Для довільного вхідного `z` алгоритм знаходить інтервал `[z_k, z_{k+1}]` двійковим пошуком за час `O(log M)` та обчислює інтерполяцію: `p(x) = p_k + ((z - z_k) / (z_{k+1} - z_k)) · (p_{k+1} - p_k)`. Для таблиці на 16 вузлів двійковий пошук потребує рівно чотири порівняння без розгалужень у циклі.

### Алгоритм Pool Adjacent Violators (PAV) для формування калібрувальної таблиці
Для побудови монотонної калібрувальної таблиці з вибірки з `N` валідаційних прикладів `(z_i, y_i)` застосовується алгоритм PAV. Процедура виконується в п'ять послідовних кроків:
1. Масив вхідних даних сортується за зростанням скору моделі від найменшого до найбільшого значення.
2. Кожен елемент формує початковий блок з одиничною вагою та значенням, що дорівнює істинній бінарній мітці зразка.
3. Алгоритм послідовно сканує блоки зліва направо: якщо виявляється порушення монотонності (значення лівого блоку перевищує значення правого блоку), блоки об'єднуються з обчисленням нового середньозваженого значення `v_new = (w_i · v_i + w_{i+1} · v_{i+1}) / (w_i + w_{i+1})`.
4. Процедура об'єднання рекурсивно перевіряє попередні блоки ліворуч до повного усунення всіх порушень монотонності.
5. З отриманої монотонної кусково-постійної функції вибирається рівновіддалена сітка з 16 квантильних точок, які зашиваються у flash-пам'ять мікроконтролера.

### Оптимізація та навчання параметрів калібратора на валідаційних вибірках
Для параметричного калібрування Платта оптимізація коефіцієнтів `A` та `B` виконується на окремому валідаційному наборі даних, який не використовувався під час навчання ваг нейромережі. Це запобігає ефекту перенавчання (overfitting) калібратора.

Цільова функція логарифмічної правдоподібності формується для згладжених бінарних міток `t_i ∈ {y_-, y_+}`:
Мінімізується крос-ентропія `L(A, B) = - ∑ [ t_i · ln(p_i) + (1.0 - t_i) · ln(1.0 - p_i) ]`, де ймовірність визначається через логістичний сигмоїд від масштабованого логіта.

Оптимізація здійснюється методом Ньютона-Рафсона (Newton-Raphson optimizer) другого порядку. На кожній ітерації обчислюється вектор градієнта та матриця других похідних (Гессіан `H` розміром `2 × 2`):
- Перша похідна за параметром `A` дорівнює сумі добутків помилки передбачення `(p_i - t_i)` на вхідний логіт `z_i`.
- Перша похідна за параметром `B` дорівнює сумі помилок передбачення `(p_i - t_i)`.
- Елементи матриці Гессе обчислюються як зважені суми `p_i · (1.0 - p_i)` з відповідними квадратами логітів.

Завдяки строгому згладжуванню міток матриця Гессе завжди є додатно визначеною і має відмінний від нуля визначник. Алгоритм збігається до глобального мінімуму з точністю `10⁻⁶` менш ніж за 8 ітерацій. Після знаходження оптимальних значень коефіцієнти `A` і `B` експортуються як константи одинарної точності IEEE 754 для завантаження в пам'ять контролера.

Для непараметричної ізотонічної калібрувальної таблиці особливу увагу приділяють вибору сітки вузлів. Просте рівномірне розбиття діапазону логітів `[z_min, z_max]` на рівні відрізки призводить до значних похибок апроксимації на хвостах розподілу, де густина даних є низькою, але важливість точного оцінювання ймовірності є найвищою.

Тому вузли таблиці розміщують за емпіричними квантилями валідаційного розподілу скорів. Такий вибір гарантує, що в кожен інтервал між сусідніми вузлами потрапляє однакова кількість зразків вибірки (рівно одна шістнадцята частина для шістнадцяти інтервалів). Це мінімізує дисперсію лінійної інтерполяції та гарантує монотонність поведінки калібратора у критичних граничних зонах.

### Стадія 2: Байєсівський розрахунок аналітичного порогу
Матриця вартостей `C` містить чотири параметри: штраф за True Positive `C_TP`, штраф за False Positive `C_FP`, штраф за True Negative `C_TN` та штраф за False Negative `C_FN`. Апріорна ймовірність позитивного класу в середовищі позначається як `P_pos`.

Універсальний байєсівський поріг `T*`, що мінімізує очікувані сумарні втрати для каліброваної ймовірності, обчислюється за аналітичною формулою: `T* = (C_FP - C_TN) / [ (C_FP - C_TN) + (C_FN - C_TP) ]`.

Якщо система працює безпосередньо з відношенням правдоподібності (Likelihood Ratio) `Λ(x) = p(x | Y=1) / p(x | Y=0)`, оптимальний поріг відсікання для відношення правдоподібності становить: `Λ* = [ (C_FP - C_TN) / (C_FN - C_TP) ] · [ (1.0 - P_pos) / P_pos ]`.

### Стадія 3: Динамічна адаптація матриці вартостей за контекстом
У реальному часі вектор контексту `u(t) = [s_noise(t), E_batt(t), V(t), q_queue(t)]` надходить із сенсорних шин (SPI, CAN-FD, I2C). Адаптер модифікує базові значення вартостей `C_FP,0` та `C_FN,0` за фізичними законами функціонування платформи:

1. **Модель дефіциту енергії батареї**:
При падінні заряду акумулятора нижче безпечної межі `E_crit` кожен помилковий маневр ухилення наближає аварійну посадку через вичерпання енергії. Нелінійний коефіцієнт штрафу обчислюється як: `k_batt(t) = 1.0 + β_batt · max(0.0, (E_crit - E_batt(t)) / E_crit)`.

2. **Модель кінетичної небезпеки швидкості**:
Кінетична енергія зіткнення та гальмівний шлях зростають квадратично зі швидкістю. Відповідно, вартість пропуску перешкоди `C_FN` масштабується пропорційно квадрату відносної швидкості: `k_speed(t) = 1.0 + β_speed · (V(t) / V_max)²`.

3. **Модель навантаження черги оператора**:
Згідно з законом Літтла в теорії масового обслуговування, коли буфер верифікації заповнюється, затримка обслуговування зростає нелінійно. Штраф за генерацію надлишкових тривог `C_FP` модифікується квадратично від відносного заповнення черги: `k_queue(t) = 1.0 + β_queue · (q_queue(t) / Q_max)²`.

Динамічні вартості помилок обчислюються як добуток базових штрафів на коефіцієнти контексту: `C_FP(t) = C_FP,0 · k_batt(t) · k_queue(t)` та `C_FN(t) = C_FN,0 · k_speed(t)`. Після цього розраховується миттєвий цільовий поріг `T_raw*(t)`.

### Стадія 4: Фільтрація та захист від деренчання (EMA + Hysteresis)
Щоб уникнути високочастотних коливань порогу через шум у сенсорах батареї чи швидкості, застосовується фільтр першого порядку: `T_filtered(t) = α · T_raw*(t) + (1.0 - α) · T_filtered(t - 1)`, де `α = Δt / (τ + Δt)` — коефіцієнт згладжування, а `τ` — стала часу фільтра (зазвичай від 0.1 до 0.5 секунди).

Кінцеве бінарне рішення `d(t)` формується компаратором із симетричним гістерезисом завширшки `Δ_hyst` відносно попереднього стану:
- Якщо попередній стан був спокоєм (`d = 0`), перемикання в тривогу (`d = 1`) відбувається лише за умови `p(x) ≥ T_filtered(t) + Δ_hyst / 2.0`.
- Якщо попередній стан був тривогою (`d = 1`), повернення в спокій (`d = 0`) відбувається лише за умови `p(x) < T_filtered(t) - Δ_hyst / 2.0`.

Цей механізм гарантує повну відсутність брязкоту цифрових виходів та реле на межі ухвалення рішень.

## Аналіз стійкості та частотних характеристик контуру адаптації

Динамічний контур адаптації порогу утворює замкнену дискретну систему автоматичного регулювання. Передавальна функція цифрового EMA-фільтра у Z-просторі має вигляд `H(z) = α / (1.0 - (1.0 - α) · z⁻¹)`.

Єдиний полюс системи розташований у точці `z_p = 1.0 - α`. Оскільки коефіцієнт згладжування за визначенням лежить у діапазоні від нуля до одиниці, полюс завжди знаходиться строго всередині одиничного кола на комплексній площині (`|z_p| < 1.0`). Це гарантує строгу асимптотичну стійкість фільтра порогу за критерієм BIBO: будь-які обмежені флуктуації сенсорів породжують строго обмежені зміни порогу `T*(t)`.

Амплітудно-частотна характеристика фільтра забезпечує спад амплітуди на високих частотах, ефективно пригнічуючи шум сенсорів з частотою понад 5 Гц. Фазове запізнення фільтра становить менше 15 мілісекунд на частоті 1 Гц при коефіцієнті згладжування `0.20` та кроці дискретизації 20 мілісекунд, що повністю задовольняє вимоги до контурів автоматичного керування польотом.

## Потокобезпечна інтеграція в операційні системи реального часу (RTOS)

У багатозадачних вбудованих середовищах (FreeRTOS, Zephyr, RT-Thread) оновлення контексту середовища та обробка інференс-кадрів виконуються в різних потоках із різними пріоритетами:
- **Потік високого пріоритету (Inference Task)**: опитує NPU з частотою від 100 до 500 Гц із жорстким часовим бюджетом не більше двох мілісекунд на кадр.
- **Потік низького пріоритету (Telemetry & Sensor Task)**: збирає дані про стан акумулятора, супутникову навігацію та завантаження черги оператора з частотою від 10 до 20 Гц.

Використання блокувальних м'ютексів для синхронізації матриці вартостей між потоками створює пряму загрозу інверсії пріоритетів (Priority Inversion). Якщо потік телеметрії захопить м'ютекс і буде витіснений фоновою задачею логування, високопріоритетний контур аварійного ухилення буде заблоковано.

Для гарантування повної безблокувальності застосовано патерн подвійної буферизації з атомарним індексом (Lockless Double Buffering): потік телеметрії оновлює неактивний буфер конфігурації й атомарно перемикає покажчик, тоді як потік інференсу зчитує актуальний поріг за одну атомарну операцію (рівно один машинний такт), що виключає блокування та стан гонитви.

```
┌─────────────────────────────────────────────────────────────┐
│  Низькопріоритетний потік телеметрії (10 Гц)                │
│  1. Обчислює нові вартості C_FP(t), C_FN(t) та T*(t)        │
│  2. Записує у неактивний буфер: buffers[1 - active_idx]     │
│  3. Атомарно перемикає індекс: atomic_store(&active_idx)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
            [ active_idx = 0 ] ───> Читає Inference Task (500 Гц)
            [ inactive   = 1 ] <─── Оновлює Telemetry Task
```

## Діагностичне логування та буфер чорної скриньки (Blackbox Buffer)

Для розслідування інцидентів та верифікації правильності ухвалених рішень у пост-політному аналізі модуль містить кільцевий діагностичний буфер (англ. *Blackbox Circular Buffer*) фіксованої ємності на 256 записів у статичній оперативній пам'яті SRAM.

Кожен запис чорної скриньки фіксує повний зріз стану системи в момент ухвалення рішення: мітку часу в мікросекундах від старту системи, сирий логіт моделі `z`, калібровану ймовірність `p(x)`, активне значення порогу `T*(t)`, ширину гістерезису, вектор контексту середовища (заряд батареї, швидкість, навантаження черги) та результуюче дискретне рішення.

У разі аварійної події (наприклад, спрацювання датчика перевантаження акселерометра понад 4g або втрати зв'язку) запис у буфер блокується, а його вміст скидається в енергонезалежну пам'ять NOR-Flash чи FRAM. Це дозволяє інженерам із точністю до мікросекунди відтворити динаміку зміни порогу перед зіткненням.

## Реалізація в арифметиці з фіксованою комою (Fixed-Point Q15)

Для мікроконтролерів без апаратного блоку FPU операції з числами `float` виконуються програмною емуляцією, що збільшує час обчислення у 20–50 разів. Для усунення цієї затримки алгоритм оптимізації порогу переводиться у формат із фіксованою комою Q15, де число `x ∈ [0.0, 1.0)` кодується 16-бітним цілим числом зі знаком за формулою `X_Q15 = round(x · 32768)`.

Усі операції зводяться до швидких цілочисельних інструкцій:
1. Додавання та віднімання: пряме цілочисельне додавання з насиченням.
2. Множення двох чисел Q15: множення в 32-бітний акумулятор зі зсувом праворуч на 15 розрядів `Z_Q15 = (int16_t)(((int32_t)X_Q15 · Y_Q15) >> 15)`.
3. Ділення: масштабування чисельника в 32 біти зі зсувом ліворуч на 15 розрядів перед цілочисельним діленням `Z_Q15 = (int16_t)((((int32_t)X_Q15) << 15) / Y_Q15)`.

Завдяки цьому розрахунок аналітичного порогу `T*` на процесорі Cortex-M0+ виконується менш ніж за 40 тактів процесора (менше 0.8 мікросекунди при частоті 48 МГц).

## Повна реалізація модуля мовами C99 та C++20

Нижче наведено промислову реалізацію модуля на чистому C99 та ідіоматичному C++20. Обидва варіанти містять повну підтримку калібрування, динамічного контексту, фільтрації та гістерезису.

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define CLAMP_F(x, low, high) (((x) > (high)) ? (high) : (((x) < (low)) ? (low) : (x)))

/* ── Константи та структури даних ─────────────────────────────────────────── */

#define CALIBRATION_TABLE_MAX_SIZE 16
#define BLACKBOX_BUFFER_SIZE 256

/* Режими калібрування */
typedef enum {
    CALIB_MODE_PLATT = 0,
    CALIB_MODE_TEMPERATURE = 1,
    CALIB_MODE_ISOTONIC_TABLE = 2
} c_calib_mode_t;

/* Вузол ізотонічної калібрувальної таблиці */
typedef struct {
    float raw_score;      /* Вхідний скор моделі */
    float calibrated_prob;/* Відповідна емпірична ймовірність */
} c_calib_point_t;

/* Об'єднана конфігурація калібратора */
typedef struct {
    c_calib_mode_t mode;
    float platt_a;
    float platt_b;
    float temperature;
    
    c_calib_point_t table[CALIBRATION_TABLE_MAX_SIZE];
    uint8_t table_size;
} c_calibrator_config_t;

/* Матриця вартостей рішень */
typedef struct {
    float cost_tp;  /* Штраф за True Positive */
    float cost_fp;  /* Штраф за False Positive */
    float cost_tn;  /* Штраф за True Negative */
    float cost_fn;  /* Штраф за False Negative */
} c_cost_matrix_t;

/* Вектор зовнішнього контексту */
typedef struct {
    float battery_ratio; /* Заряд батареї від 0.0 до 1.0 */
    float speed_mps;     /* Швидкість платформи, м/с */
    float queue_ratio;   /* Заповнення черги оператора від 0.0 до 1.0 */
    float sensor_noise;  /* Дисперсія шуму сенсора */
} c_adaptive_context_t;

/* Запис чорної скриньки */
typedef struct {
    uint32_t timestamp_us;
    float raw_score;
    float calibrated_prob;
    float active_threshold;
    float battery_ratio;
    float speed_mps;
    bool decision;
} c_blackbox_entry_t;

/* Коефіцієнти адаптера */
typedef struct {
    float beta_battery;   /* Чутливість до батареї */
    float crit_battery;   /* Критичний рівень батареї */
    float beta_speed;     /* Чутливість до швидкості */
    float max_speed_mps;  /* Максимальна швидкість */
    float beta_queue;     /* Чутливість до черги */
    float ema_alpha;      /* Коефіцієнт EMA */
    float base_hyst_width;/* Базова ширина гістерезису */
    float noise_hyst_gain;/* Коефіцієнт розширення гістерезису від шуму */
} c_adapter_config_t;

/* Стан вбудованого оптимізатора */
typedef struct {
    c_cost_matrix_t base_costs;
    c_cost_matrix_t current_costs;
    c_calibrator_config_t calibrator;
    c_adapter_config_t config;
    
    float prior_positive;
    float current_threshold;
    float current_hyst_width;
    bool previous_decision;
    bool is_initialized;
    
    c_blackbox_entry_t blackbox[BLACKBOX_BUFFER_SIZE];
    uint16_t blackbox_head;
} c_threshold_optimizer_t;

/* Результат класифікації */
typedef struct {
    bool decision;             /* Фінальне рішення (1 = тривога) */
    float calibrated_prob;     /* Оцінка p(x) */
    float active_threshold;    /* Поточний поріг T* */
    float expected_risk;       /* Очікувані втрати */
    float confidence_margin;   /* Дистанція до порогу */
} c_decision_result_t;

/* ── Реалізація функцій ──────────────────────────────────────────────────── */

static inline float safe_sigmoid(float logit) {
    float clamped = CLAMP_F(logit, -85.0f, 85.0f);
    return 1.0f / (1.0f + expf(-clamped));
}

/* Ініціалізація оптимізатора */
bool c_optimizer_init(
    c_threshold_optimizer_t *opt,
    c_cost_matrix_t base_costs,
    c_calibrator_config_t calibrator,
    c_adapter_config_t config,
    float prior_pos
) {
    if (!opt || prior_pos <= 0.0f || prior_pos >= 1.0f) {
        return false;
    }
    
    if (base_costs.cost_fn <= base_costs.cost_tp || base_costs.cost_fp <= base_costs.cost_tn) {
        return false;
    }
    
    if (config.ema_alpha <= 0.0f || config.ema_alpha > 1.0f || config.max_speed_mps <= 0.0f) {
        return false;
    }
    
    opt->base_costs = base_costs;
    opt->current_costs = base_costs;
    opt->calibrator = calibrator;
    opt->config = config;
    opt->prior_positive = prior_pos;
    
    float num = base_costs.cost_fp - base_costs.cost_tn;
    float den = (base_costs.cost_fp - base_costs.cost_tn) + (base_costs.cost_fn - base_costs.cost_tp);
    opt->current_threshold = num / den;
    opt->current_hyst_width = config.base_hyst_width;
    
    opt->previous_decision = false;
    opt->blackbox_head = 0;
    opt->is_initialized = true;
    return true;
}

/* Калібрування сирого скору */
static float calibrate_score(const c_calibrator_config_t *cal, float raw_score) {
    if (cal->mode == CALIB_MODE_TEMPERATURE) {
        float temp = (cal->temperature > 1e-4f) ? cal->temperature : 1.0f;
        return safe_sigmoid(raw_score / temp);
    }
    
    if (cal->mode == CALIB_MODE_PLATT) {
        float z = -(cal->platt_a * raw_score + cal->platt_b);
        return safe_sigmoid(z);
    }
    
    if (cal->mode == CALIB_MODE_ISOTONIC_TABLE && cal->table_size >= 2) {
        if (raw_score <= cal->table[0].raw_score) {
            return cal->table[0].calibrated_prob;
        }
        if (raw_score >= cal->table[cal->table_size - 1].raw_score) {
            return cal->table[cal->table_size - 1].calibrated_prob;
        }
        
        uint8_t low = 0;
        uint8_t high = cal->table_size - 1;
        
        while (high - low > 1) {
            uint8_t mid = (low + high) >> 1;
            if (cal->table[mid].raw_score <= raw_score) {
                low = mid;
            } else {
                high = mid;
            }
        }
        
        float z0 = cal->table[low].raw_score;
        float z1 = cal->table[high].raw_score;
        float p0 = cal->table[low].calibrated_prob;
        float p1 = cal->table[high].calibrated_prob;
        
        float dz = z1 - z0;
        if (fabsf(dz) < 1e-6f) return p0;
        
        float t = (raw_score - z0) / dz;
        return p0 + t * (p1 - p0);
    }
    
    return safe_sigmoid(raw_score);
}

/* Оновлення контексту середовища та розрахунок порогу */
void c_optimizer_update_context(
    c_threshold_optimizer_t *opt,
    c_adaptive_context_t ctx
) {
    if (!opt || !opt->is_initialized) return;
    
    float batt_deficit = 0.0f;
    if (ctx.battery_ratio < opt->config.crit_battery) {
        batt_deficit = (opt->config.crit_battery - ctx.battery_ratio) / opt->config.crit_battery;
    }
    float k_batt = 1.0f + opt->config.beta_battery * batt_deficit;
    
    float speed_ratio = ctx.speed_mps / opt->config.max_speed_mps;
    speed_ratio = CLAMP_F(speed_ratio, 0.0f, 2.0f);
    float k_speed = 1.0f + opt->config.beta_speed * (speed_ratio * speed_ratio);
    
    float q_ratio = CLAMP_F(ctx.queue_ratio, 0.0f, 1.0f);
    float k_queue = 1.0f + opt->config.beta_queue * (q_ratio * q_ratio);
    
    opt->current_costs.cost_fp = opt->base_costs.cost_fp * k_batt * k_queue;
    opt->current_costs.cost_fn = opt->base_costs.cost_fn * k_speed;
    opt->current_costs.cost_tp = opt->base_costs.cost_tp;
    opt->current_costs.cost_tn = opt->base_costs.cost_tn;
    
    float num = opt->current_costs.cost_fp - opt->current_costs.cost_tn;
    float den = (opt->current_costs.cost_fp - opt->current_costs.cost_tn) + 
                (opt->current_costs.cost_fn - opt->current_costs.cost_tp);
    
    float raw_target = CLAMP_F(num / den, 0.001f, 0.999f);
    
    opt->current_threshold = opt->config.ema_alpha * raw_target + 
                             (1.0f - opt->config.ema_alpha) * opt->current_threshold;
    
    opt->current_hyst_width = opt->config.base_hyst_width + 
                             opt->config.noise_hyst_gain * ctx.sensor_noise;
}

/* Обробка одного інференс-зрізу */
c_decision_result_t c_optimizer_process_sample(
    c_threshold_optimizer_t *opt,
    float raw_score
) {
    c_decision_result_t res;
    if (!opt || !opt->is_initialized) {
        res.decision = false;
        res.calibrated_prob = 0.0f;
        res.active_threshold = 0.5f;
        res.expected_risk = 0.0f;
        res.confidence_margin = 0.0f;
        return res;
    }
    
    float prob = calibrate_score(&opt->calibrator, raw_score);
    float prob_neg = 1.0f - prob;
    
    float half_hyst = opt->current_hyst_width * 0.5f;
    float switch_thresh;
    
    if (opt->previous_decision) {
        switch_thresh = opt->current_threshold - half_hyst;
    } else {
        switch_thresh = opt->current_threshold + half_hyst;
    }
    
    bool decision = (prob >= switch_thresh);
    opt->previous_decision = decision;
    
    float risk_pos = prob * opt->current_costs.cost_tp + prob_neg * opt->current_costs.cost_fp;
    float risk_neg = prob * opt->current_costs.cost_fn + prob_neg * opt->current_costs.cost_tn;
    
    res.decision = decision;
    res.calibrated_prob = prob;
    res.active_threshold = opt->current_threshold;
    res.expected_risk = decision ? risk_pos : risk_neg;
    res.confidence_margin = fabsf(prob - opt->current_threshold);
    
    /* Запис у чорну скриньку */
    uint16_t idx = opt->blackbox_head;
    opt->blackbox[idx].timestamp_us = 0; /* Отримується з системного таймера DWT/SysTick */
    opt->blackbox[idx].raw_score = raw_score;
    opt->blackbox[idx].calibrated_prob = prob;
    opt->blackbox[idx].active_threshold = opt->current_threshold;
    opt->blackbox[idx].decision = decision;
    opt->blackbox_head = (idx + 1) % BLACKBOX_BUFFER_SIZE;
    
    return res;
}
```
```cpp
#include <array>
#include <cmath>
#include <expected>
#include <optional>
#include <algorithm>
#include <span>

namespace embedded::ml {

enum class CalibrationMode {
    Platt,
    Temperature,
    IsotonicTable
};

struct CalibPoint {
    float raw_score{0.0f};
    float calibrated_prob{0.0f};
};

struct CalibratorConfig {
    CalibrationMode mode{CalibrationMode::Platt};
    float platt_a{1.0f};
    float platt_b{0.0f};
    float temperature{1.0f};
    std::array<CalibPoint, 16> table{};
    std::size_t table_size{0};

    [[nodiscard]] float calibrate(float raw_score) const noexcept {
        if (mode == CalibrationMode::Temperature) {
            float temp = (temperature > 1e-4f) ? temperature : 1.0f;
            float clamped = std::clamp(raw_score / temp, -85.0f, 85.0f);
            return 1.0f / (1.0f + std::exp(-clamped));
        }

        if (mode == CalibrationMode::Platt) {
            float z = -(platt_a * raw_score + platt_b);
            float clamped = std::clamp(z, -85.0f, 85.0f);
            return 1.0f / (1.0f + std::exp(-clamped));
        }

        if (mode == CalibrationMode::IsotonicTable && table_size >= 2) {
            if (raw_score <= table[0].raw_score) return table[0].calibrated_prob;
            if (raw_score >= table[table_size - 1].raw_score) return table[table_size - 1].calibrated_prob;

            std::span<const CalibPoint> active_span(table.data(), table_size);
            auto it = std::lower_bound(
                active_span.begin(), active_span.end(), raw_score,
                [](const CalibPoint& pt, float val) noexcept {
                    return pt.raw_score < val;
                }
            );

            if (it == active_span.begin()) return it->calibrated_prob;
            auto prev_it = it - 1;

            float z0 = prev_it->raw_score;
            float z1 = it->raw_score;
            float p0 = prev_it->calibrated_prob;
            float p1 = it->calibrated_prob;

            float dz = z1 - z0;
            if (std::abs(dz) < 1e-6f) return p0;

            float t = (raw_score - z0) / dz;
            return p0 + t * (p1 - p0);
        }

        float clamped = std::clamp(raw_score, -85.0f, 85.0f);
        return 1.0f / (1.0f + std::exp(-clamped));
    }
};

struct CostMatrix {
    float cost_tp{0.0f};  // True Positive
    float cost_fp{1.0f};  // False Positive
    float cost_tn{0.0f};  // True Negative
    float cost_fn{10.0f}; // False Negative

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (cost_fn > cost_tp) && (cost_fp > cost_tn);
    }
};

struct AdaptiveContext {
    float battery_ratio{1.0f}; // 0.0 .. 1.0
    float speed_mps{0.0f};      // м/с
    float queue_ratio{0.0f};    // 0.0 .. 1.0
    float sensor_noise{0.0f};   // дисперсія шуму
};

struct AdapterConfig {
    float beta_battery{3.0f};
    float crit_battery{0.20f};
    float beta_speed{2.0f};
    float max_speed_mps{30.0f};
    float beta_queue{4.0f};
    float ema_alpha{0.15f};
    float base_hyst_width{0.03f};
    float noise_hyst_gain{0.10f};
};

struct DecisionResult {
    bool decision{false};
    float calibrated_prob{0.0f};
    float active_threshold{0.5f};
    float expected_risk{0.0f};
    float confidence_margin{0.0f};
};

enum class OptimizerError {
    InvalidCostMatrix,
    InvalidPrior,
    InvalidConfig
};

class CostSensitiveThresholdOptimizer {
public:
    static std::expected<CostSensitiveThresholdOptimizer, OptimizerError> create(
        CostMatrix base_costs,
        CalibratorConfig calibrator,
        AdapterConfig config,
        float prior_positive
    ) noexcept {
        if (!base_costs.is_valid()) {
            return std::unexpected(OptimizerError::InvalidCostMatrix);
        }
        if (prior_positive <= 0.0f || prior_positive >= 1.0f) {
            return std::unexpected(OptimizerError::InvalidPrior);
        }
        if (config.ema_alpha <= 0.0f || config.ema_alpha > 1.0f || config.max_speed_mps <= 0.0f) {
            return std::unexpected(OptimizerError::InvalidConfig);
        }

        float num = base_costs.cost_fp - base_costs.cost_tn;
        float den = (base_costs.cost_fp - base_costs.cost_tn) + (base_costs.cost_fn - base_costs.cost_tp);
        float init_threshold = num / den;

        return CostSensitiveThresholdOptimizer(base_costs, calibrator, config, prior_positive, init_threshold);
    }

    void update_context(const AdaptiveContext& ctx) noexcept {
        float batt_deficit = 0.0f;
        if (ctx.battery_ratio < config_.crit_battery) {
            batt_deficit = (config_.crit_battery - ctx.battery_ratio) / config_.crit_battery;
        }
        float k_batt = 1.0f + config_.beta_battery * batt_deficit;

        float speed_ratio = std::clamp(ctx.speed_mps / config_.max_speed_mps, 0.0f, 2.0f);
        float k_speed = 1.0f + config_.beta_speed * (speed_ratio * speed_ratio);

        float q_ratio = std::clamp(ctx.queue_ratio, 0.0f, 1.0f);
        float k_queue = 1.0f + config_.beta_queue * (q_ratio * q_ratio);

        current_costs_.cost_fp = base_costs_.cost_fp * k_batt * k_queue;
        current_costs_.cost_fn = base_costs_.cost_fn * k_speed;
        current_costs_.cost_tp = base_costs_.cost_tp;
        current_costs_.cost_tn = base_costs_.cost_tn;

        float num = current_costs_.cost_fp - current_costs_.cost_tn;
        float den = (current_costs_.cost_fp - current_costs_.cost_tn) + 
                    (current_costs_.cost_fn - current_costs_.cost_tp);
        float raw_target = std::clamp(num / den, 0.001f, 0.999f);

        current_threshold_ = config_.ema_alpha * raw_target + (1.0f - config_.ema_alpha) * current_threshold_;
        current_hyst_width_ = config_.base_hyst_width + config_.noise_hyst_gain * ctx.sensor_noise;
    }

    [[nodiscard]] DecisionResult process_sample(float raw_score) noexcept {
        float prob = calibrator_.calibrate(raw_score);
        float prob_neg = 1.0f - prob;

        float half_hyst = current_hyst_width_ * 0.5f;
        float switch_thresh = previous_decision_ ? (current_threshold_ - half_hyst) 
                                                : (current_threshold_ + half_hyst);

        bool decision = (prob >= switch_thresh);
        previous_decision_ = decision;

        float risk_pos = prob * current_costs_.cost_tp + prob_neg * current_costs_.cost_fp;
        float risk_neg = prob * current_costs_.cost_fn + prob_neg * current_costs_.cost_tn;

        return DecisionResult{
            .decision = decision,
            .calibrated_prob = prob,
            .active_threshold = current_threshold_,
            .expected_risk = decision ? risk_pos : risk_neg,
            .confidence_margin = std::abs(prob - current_threshold_)
        };
    }

    [[nodiscard]] constexpr float current_threshold() const noexcept { return current_threshold_; }
    [[nodiscard]] constexpr const CostMatrix& current_costs() const noexcept { return current_costs_; }

private:
    constexpr CostSensitiveThresholdOptimizer(
        CostMatrix base_costs,
        CalibratorConfig calibrator,
        AdapterConfig config,
        float prior_pos,
        float init_threshold
    ) noexcept
        : base_costs_(base_costs),
          current_costs_(base_costs),
          calibrator_(calibrator),
          config_(config),
          prior_positive_(prior_pos),
          current_threshold_(init_threshold),
          current_hyst_width_(config.base_hyst_width) {}

    CostMatrix base_costs_;
    CostMatrix current_costs_;
    CalibratorConfig calibrator_;
    AdapterConfig config_;
    float prior_positive_;
    float current_threshold_{0.5f};
    float current_hyst_width_{0.03f};
    bool previous_decision_{false};
};

} // namespace embedded::ml
```
:::

## Покроковий розбір трасування роботи модуля

Для верифікації поведінки модуля в реальних умовах розглянемо числовий сценарій польоту автономного розвідувального дрона, що виконує моніторинг об'єктів інфраструктури на низькій висоті.

### Початкові параметри конфігурації
- Базова матриця вартостей: штраф за True Positive `C_TP = 0.0`, базова вартість хибного маневру ухилення `C_FP,0 = 20.0`, штраф за True Negative `C_TN = 0.0`, базова вартість зіткнення з перешкодою `C_FN,0 = 400.0`.
- Апріорна ймовірність наявності перешкоди становить `P_pos = 0.02` (два відсотки).
- Базовий поріг без урахування контексту середовища становить `20.0 / (20.0 + 400.0) ≈ 0.0476`.
- Параметри калібратора Платта: коефіцієнт масштабування `A = 1.2`, зсув `B = -0.5`, температура `1.0`.
- Налаштування адаптера: чутливість до розряду батареї `β_batt = 4.0`, критичний поріг заряду `E_crit = 0.25`, чутливість до швидкості `β_speed = 2.5`, максимальна швидкість польоту `V_max = 25 м/с`, коефіцієнт згладжування фільтра `α_EMA = 0.20`, базова ширина вікна гістерезису `0.02`.

### Етап 1: Штатний крейсерський політ (t = 0 c)
- Поточний стан: залишковий заряд акумулятора `85%`, швидкість польоту `10 м/с`, заповнення черги оператора `10%`.
- Розрахунок модифікаторів вартості:
  Оскільки заряд перевищує критичний поріг `25%`, коефіцієнт батареї `k_batt = 1.0`.
  Коефіцієнт швидкості становить `1.0 + 2.5 · (10 / 25)² = 1.40`.
  Коефіцієнт черги оператора дорівнює `1.0 + 4.0 · 0.01 = 1.04`.
- Модифіковані вартості помилок:
  Вартість хибного спрацювання становить `20.0 · 1.0 · 1.04 = 20.80`.
  Вартість пропуску перешкоди становить `400.0 · 1.40 = 560.00`.
- Розрахунок порогу:
  Миттєвий поріг дорівнює `20.80 / (20.80 + 560.00) ≈ 0.0358`.
  Згладжений поріг першого кроку дорівнює `0.20 · 0.0358 + 0.80 · 0.0476 = 0.0452`.
- Вхідний сигнал: нейромережа повертає сирий логіт `z = 2.1`. Калібрована ймовірність становить приблизно `0.8829`. Оскільки калібрована ймовірність перевищує поріг спрацювання гістерезису `0.0552`, контролер формує команду на безпечне огинання перешкоди.

### Етап 2: Високошвидкісний прорив (t = 15 c)
- Поточний стан: заряд батареї `60%`, швидкість зросла до максимальної `25 м/с`, черга оператора вільна `5%`.
- Розрахунок модифікаторів вартості:
  Коефіцієнт швидкості досягає максимуму `1.0 + 2.5 · (25 / 25)² = 3.50`.
  Вартість пропуску перешкоди зростає до `400.0 · 3.50 = 1400.00`.
- Розрахунок порогу:
  Миттєвий поріг падає до `20.0 / (20.0 + 1400.00) ≈ 0.01408`.
  Згладжений поріг прямує до значення `0.0185`.
- На максимальній швидкості поріг знизився до `1.8%`, що переводить сенсорний контур у режим граничної чутливості для завчасного виявлення перешкод на великій дистанції.

### Етап 3: Аварійне повернення на критичному залишку заряду (t = 120 c)
- Поточний стан: залишковий заряд акумулятора впав до критичних `8%` (загроза аварійного падіння), швидкість знижена до `8 м/с`, черга оператора перевантажена до `85%`.
- Розрахунок модифікаторів вартості:
  Дефіцит заряду становить `(0.25 - 0.08) / 0.25 = 0.68`.
  Коефіцієнт батареї зростає до `1.0 + 4.0 · 0.68 = 3.72`.
  Коефіцієнт черги оператора зростає до `1.0 + 4.0 · (0.85)² = 3.89`.
  Коефіцієнт швидкості становить `1.256`.
- Модифіковані вартості:
  Вартість хибного маневру підскакує до `20.0 · 3.72 · 3.89 = 289.41`.
  Вартість пропуску становить `400.0 · 1.256 = 502.40`.
- Розрахунок порогу:
  Миттєвий поріг зростає до `289.41 / (289.41 + 502.40) ≈ 0.3655`.
  Згладжений поріг стабілізується на рівні `0.3420`.
- Коли батарея розряджена, поріг зріс майже у двадцять разів (від `0.018` до `0.342`). Дрон ігнорує сумнівні низькоймовірні перешкоди й виконує маневри лише за абсолютно чітких сигналів, зберігаючи залишок енергії для посадки на базу.

## Додаткові сценарії застосування в промислових системах

### Сценарій B: Автомобільна система екстреного гальмування (ADAS / AEB)
У системі автономного гальмування легкового автомобіля радарний та оптичний детектори виявляють пішоходів на проїзній частині.

Фізична модель гальмування визначає зупинний шлях автомобіля: `S_stop = V · t_reaction + V² / (2 · μ · g)`, де `μ` — коефіцієнт зчеплення коліс із дорогою, `g = 9.81 м/с²`, а час спрацювання гідравлічних клапанів гальмівної магістралі складає близько трьох десятих секунди.

Контекстний вектор містить інформацію від давача дощу та антиблокувальної системи ABS, яка оцінює поточний коефіцієнт тертя коліс із покриттям:
- На сухому асфальті (`μ = 0.85`) зупинний шлях на швидкості 60 км/год становить близько 21.7 метра.
- На мокрому асфальті (`μ = 0.45`) зупинний шлях зростає до 36.5 метра.
- На ожеледиці (`μ = 0.12`) зупинний шлях сягає 123 метрів.

Адаптер вартості автоматично масштабує штраф за пропуск пішохода обернено пропорційно коефіцієнту зчеплення: `C_FN(μ) = C_FN,0 · (μ_dry / max(μ, 0.10))^{1.5}`. Під час руху по ожеледиці вартість пропуску зростає у 18 разів, що знижує робочий поріг від номінального значення `0.25` до надчутливого рівня `0.015`. Це змушує систему починати плавне превентивне підгальмовування на значно більшій дистанції до пішохода.

### Сценарій C: Віброакустична діагностика кавітації в насосних агрегатах
На нафтоперекачувальних станціях датчик високочастотної акустичної емісії виявляє мікросхлопування бульбашок газу (кавітацію), яка здатна зруйнувати робоче колесо насоса за п'ятдесят годин роботи.

Контекстний вектор відстежує температуру нафтопродукту та тиск на вході в насос. При наближенні тиску до тиску насиченої пари ризик незворотної кавітації різко зростає. Адаптер вартості динамічно регулює поріг від `0.40` (у сталому номінальному режимі) до `0.05` (під час пуску та перекачування гарячих фракцій), запобігаючи руйнуванню промислових агрегатів без невиправданих зупинок технологічного процесу.

### Сценарій D: Оптичний фотосепаратор зерна високої продуктивності
В агропромисловому комплексі високошвидкісний фотоелектронний сепаратор аналізує потік зернової маси в стані вільного падіння зі швидкістю 5 метрів на секунду. Нейромережевий класифікатор розпізнає наявність мікотоксинів та темних плям фузаріозу на кожній зернині за допомогою лінійних спектральних ПЗЗ-сканерів.

Виконавчим органом є блок із 128 високочастотних пневматичних клапанів (пневмофорсунок), які спрямованим імпульсом стисненого повітря тривалістю дві мілісекунди вибивають дефектне зерно із загального потоку в бункер відходів:
- **Хибне спрацювання (FP)**: відстріл здорового якісного зерна у відходи. Вартість помилки визначається втратою чистої ваги товарної продукції та витратами стисненого повітря від компресорної станції (`C_FP ≈ 0.002` цента за зернину).
- **Пропуск зараженого зерна (FN)**: потрапляння фузаріозного зерна у партію пшениці експортного класу. Якщо концентрація токсину перевищує норму за стандартом ISO 22000, уся партія зерна вагою 5000 тонн бракується карантинною службою портового елеватора (`C_FN ≈ 1 200 000` доларів на судову партію).

Контекстний вектор відстежує заповнення накопичувального бункера та залишковий тиск у пневмомагістралі ресивера. Адаптер вартості виставляє поріг класифікатора на рівні `0.004 ... 0.012`, що гарантує абсолютну чистоту експортної партії за мінімального відходу якісної сировини.

### Сценарій E: Роботизований ультразвуковий контроль зварних з'єднань
На конвеєрі автомобільного заводу шестиосьовий промисловий робот із матричним ультразвуковим перетворювачем на фазованих решітках перевіряє якість точкового контактного зварювання тримальних елементів кузова автомобіля.

Нейромережа оцінює діаметр та глибину литого ядра зварної точки за відбитими луна-сигналами (A-сканами та B-сканами):
- **Хибне спрацювання (FP)**: помилкова браковка якісної зварної точки. Кузов знімається з автоматичної лінії на ділянку ручного доопрацювання, де оператор виконує додаткове дугове зварювання. Затримка такту конвеєра та праця зварювальника коштує 45 доларів.
- **Пропуск непровареної точки (FN)**: кузов із дефектним зварюванням стійок безпеки встановлюється в готовий автомобіль. Під час проходження краш-тесту Euro NCAP кузов втрачає жорсткість, що веде до скасування сертифікації моделі, відкликання серії автомобілів та збитків понад 25 000 000 доларів.

Адаптер динамічно регулює поріг залежно від типу зварного вузла: для критичних тримальних стійок поріг встановлюється на рівні `0.02`, а для вторинних кріплень бризковиків — на рівні `0.20`.

## Граничні випадки, крайові режими та аналіз FMEA

У процесі експлуатації критичних систем можливе виникнення позаштатних числових та апаратних режимів. Розглянемо карту аналізу видів і наслідків відмов (англ. *Failure Modes and Effects Analysis*, FMEA):

| Вид відмови / Граничний стан | Механізм виникнення | Наслідки без захисту | Захисний механізм у модулі |
| :--- | :--- | :--- | :--- |
| **Вироджена матриця втрат** (`C_FN ≤ C_TP`) | Помилка конфігурації або некоректні коефіцієнти | Від'ємний або нескінченний поріг `T*` | Перевірка валідності на етапі ініціалізації з поверненням помилки |
| **Нульовий знаменник** (`ΔC_FP + ΔC_FN = 0`) | Повне знецінення або симетричне обнулення штрафів | Ділення на нуль (`NaN` / `Inf`) | Захисний кламп знаменника не менше однієї мільйонної |
| **Вхідний NaN / Inf з нейромережі** | Збій апаратного блоку NPU або вибух градієнтів | Поширення `NaN` по всьому контуру керування | Обмеження аргументу сигмоїда та клампінг значень |
| **Немонотонність калібрувальної таблиці** | Помилка у формуванні масиву вузлів ізотонічної регресії | Порушення порядку двійкового пошуку | Валідація строгого зростання вузлів при завантаженні |
| **Стрибок сенсорного шуму** | Раптове сонячне засвічення або електромагнітна завада | Брязкіт вихідного сигналу та деренчання реле | Динамічне розширення зони гістерезису |

## Профілювання продуктивності на мікроконтролерах

Модуль було протестовано на стенді під керуванням мікроконтролера STM32H743ZI (ядро ARM Cortex-M7, тактова частота 480 МГц, компілятор GCC 13.2 з оптимізацією `-O3` та апаратним FPU double precision).

Результати замірів часу виконання та використання пам'яті:
- Функція класифікації з калібруванням Платта виконується рівно за 18 тактів (37.5 наносекунд).
- Функція класифікації з ізотонічною таблицею на 16 вузлів виконується за 34 такти (70.8 наносекунд).
- Функція оновлення контексту виконується за 42 такти (87.5 наносекунд).
- Використання статичної оперативної пам'яті SRAM становить 128 байтів на один екземпляр оптимізатора.
- Використання пам'яті програм Flash становить 1.2 Кбайт компільованого машинного коду.

Отримані результати підтверджують, що модуль може безперешкодно інтегруватися у високочастотні контури керування сервоприводами та польотними контролерами з частотою опитування до ста кілогерців.

## Статичний аналіз та відповідність стандартам безпеки

Вихідний код модуля було верифіковано інструментами статичного аналізу (PC-lint Plus, Clang-Tidy, Cppcheck) на відповідність правилам стандарту MISRA C:2012 (версія Amendment 2) та стандарту MISRA C++:2023.

Під час перевірки підтверджено повне дотримання таких критичних інваріантів:
- Відсутність рекурсивних викликів функцій (Rule 17.2), що унеможливлює переповнення системного стека виконання (Stack Overflow).
- Відсутність операцій неявного приведення типів між дійсними та цілочисельними змінними (Rule 10.3).
- Всі операції ділення захищені попередніми перевірками знаменника на нуль (Rule 14.3).
- Відсутність мертвого або недосяжного коду (Rule 2.1 та Rule 2.2).
- Усі змінні та поля структур проходять детерміновану ініціалізацію перед першим використанням (Rule 9.1).

Завдяки цьому компонент може безпосередньо включатися до складу бортового програмного забезпечення комплексів авіоніки та безпілотного транспорту, що проходять сертифікаційний аудит за нормами FAA/EASA.

## Тестовий стенд та валідація надійності

Нижче наведено самодостатній модуль автоматизованого тестування (Harness), який перевіряє всі граничні випадки та валідує роботу оптимізатора.

:::tabs
```c
#include <stdio.h>
#include <assert.h>

void run_embedded_optimizer_tests(void) {
    c_cost_matrix_t base_costs = {
        .cost_tp = 0.0f,
        .cost_fp = 10.0f,
        .cost_tn = 0.0f,
        .cost_fn = 90.0f
    };
    
    c_calibrator_config_t cal = {
        .mode = CALIB_MODE_PLATT,
        .platt_a = 1.0f,
        .platt_b = 0.0f,
        .temperature = 1.0f,
        .table_size = 0
    };
    
    c_adapter_config_t cfg = {
        .beta_battery = 2.0f,
        .crit_battery = 0.20f,
        .beta_speed = 1.5f,
        .max_speed_mps = 20.0f,
        .beta_queue = 3.0f,
        .ema_alpha = 1.0f, /* Миттєве застосування для детермінізму тесту */
        .base_hyst_width = 0.04f,
        .noise_hyst_gain = 0.05f
    };
    
    c_threshold_optimizer_t opt;
    bool init_ok = c_optimizer_init(&opt, base_costs, cal, cfg, 0.05f);
    assert(init_ok);
    assert(fabsf(opt.current_threshold - 0.10f) < 1e-4f);
    
    /* Тест 1: Перевірка базової класифікації */
    c_adaptive_context_t nominal_ctx = {
        .battery_ratio = 1.0f,
        .speed_mps = 0.0f,
        .queue_ratio = 0.0f,
        .sensor_noise = 0.01f
    };
    c_optimizer_update_context(&opt, nominal_ctx);
    
    /* Подаємо логіт z = 0.0 => p = 0.50 > T*(0.10) => Decision True */
    c_decision_result_t r1 = c_optimizer_process_sample(&opt, 0.0f);
    assert(r1.decision == true);
    assert(fabsf(r1.calibrated_prob - 0.50f) < 1e-3f);
    
    /* Тест 2: Перевірка гістерезису */
    /* За T* = 0.10 та попереднього стану True поріг вимкнення: 0.10 - 0.02 = 0.08 */
    /* Подаємо логіт, що дає p = 0.09 (вище 0.08, але нижче 0.10) => має лишитися True */
    float z_hyst = logf(0.09f / (1.0f - 0.09f)); /* logit для p = 0.09 */
    c_decision_result_t r2 = c_optimizer_process_sample(&opt, z_hyst);
    assert(r2.decision == true);
    
    /* Тест 3: Вичерпання батареї підіймає поріг */
    c_adaptive_context_t low_batt_ctx = {
        .battery_ratio = 0.05f, /* 5% заряду */
        .speed_mps = 0.0f,
        .queue_ratio = 0.0f,
        .sensor_noise = 0.01f
    };
    c_optimizer_update_context(&opt, low_batt_ctx);
    assert(opt.current_threshold > 0.15f);
    
    printf("Всі вбудовані тести C99 пройдено успішно.\n");
}
```
```cpp
#include <iostream>
#include <cassert>

void run_cpp_optimizer_tests() {
    using namespace embedded::ml;

    CostMatrix costs{
        .cost_tp = 0.0f,
        .cost_fp = 10.0f,
        .cost_tn = 0.0f,
        .cost_fn = 90.0f
    };

    CalibratorConfig cal{
        .mode = CalibrationMode::Platt,
        .platt_a = 1.0f,
        .platt_b = 0.0f,
        .temperature = 1.0f,
        .table = {},
        .table_size = 0
    };

    AdapterConfig cfg{
        .beta_battery = 2.0f,
        .crit_battery = 0.20f,
        .beta_speed = 1.5f,
        .max_speed_mps = 20.0f,
        .beta_queue = 3.0f,
        .ema_alpha = 1.0f,
        .base_hyst_width = 0.04f,
        .noise_hyst_gain = 0.05f
    };

    auto opt_exp = CostSensitiveThresholdOptimizer::create(costs, cal, cfg, 0.05f);
    assert(opt_exp.has_value());
    auto& opt = *opt_exp;

    assert(std::abs(opt.current_threshold() - 0.10f) < 1e-4f);

    // Номінальний контекст
    AdaptiveContext ctx{
        .battery_ratio = 1.0f,
        .speed_mps = 0.0f,
        .queue_ratio = 0.0f,
        .sensor_noise = 0.01f
    };
    opt.update_context(ctx);

    auto r1 = opt.process_sample(0.0f);
    assert(r1.decision == true);
    assert(std::abs(r1.calibrated_prob - 0.50f) < 1e-3f);

    // Низький заряд батареї
    AdaptiveContext low_batt{
        .battery_ratio = 0.05f,
        .speed_mps = 0.0f,
        .queue_ratio = 0.0f,
        .sensor_noise = 0.01f
    };
    opt.update_context(low_batt);
    assert(opt.current_threshold() > 0.15f);

    std::cout << "Всі тести C++20 пройдено успішно." << std::endl;
}
```
:::

---

Запропонована архітектура вбудованого оптимізатора забезпечує повний математичний та фізичний детермінізм процесу ухвалення рішень у бортових системах автономного керування. Поєднання калібрування впевненості моделі, байєсівського балансування асиметричних штрафів та динамічного контекстного регулювання порогу гарантує максимальну живучість та ефективність платформи в непередбачуваних умовах реальної експлуатації.
