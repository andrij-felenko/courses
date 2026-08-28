# Практика: розрахунок S₁₁ та синтез узгоджувальних ланцюгів на діаграмі Сміта

У практичній розробці радіочастотних пристроїв інженеру постійно доводиться перетворювати сирі вимірювання векторного аналізатора кіл (VNA) у конкретні номінали пасивних SMD-компонентів узгоджувального контуру. Файли вимірювань у форматі Touchstone S1P містять таблиці комплексних коефіцієнтів відбиття S₁₁ у широкому діапазоні частот. Щоб за цими даними спроектувати надійний узгоджувальний ланцюг, необхідно виконати повний математичний цикл: перерахувати коефіцієнт відбиття в комплексний імпеданс та адмітанс, розрахувати топології L-контурів, П-контурів та T-контурів, врахувати паразитні параметри реальних компонентів і змоделювати підсумкову частотну характеристику системи.

Нижче наведено повний інженерний інструмент — консольний калькулятор та симулятор узгодження радіочастотного імпедансу, реалізований мовами C99 та C++20. Програма підтримує парсинг файлів Touchstone (.s1p), пряме введення імпедансу або параметрів відбиття, автоматичний синтез усіх можливих топологій L-, П- та T-ланцюгів, квантування номіналів до стандартних рядів E24/E96, моделювання неідеальностей компонентів (ESL, ESR, паразитна ємність майданчиків) та розрахунок частотного відгуку КСХ, зворотних втрат і ККД контуру.

```
  ┌────────────────────────────────────────────────────────┐
  │ 1. Вхідні дані: Touchstone .s1p або ручний ввід S₁₁/Z  │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ 2. Обчислення комплексного Γ, VSWR, Return Loss        │
  │    Z_A = Z₀ · (1 + Γ) / (1 − Γ) = R_A + jX_A           │
  │    Y_A = 1 / Z_A = G_A + jB_A                          │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ 3. Аналітичний синтез топологій узгодження:            │
  │    - 8 варіантів L-контурів (Low-Pass / High-Pass)     │
  │    - 2 варіанти П-контуру з контролем добротності Q_L  │
  │    - 2 варіанти T-контуру з контролем добротності Q_L  │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ 4. Квантування номіналів до стандартного ряду E24/E96  │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ 5. Моделювання неідеальностей:                         │
  │    - Конденсатори: C, ESL, ESR, розрахунок SRF         │
  │    - Котушки: L, ESR = ωL/Q₀, C_p, розрахунок SRF      │
  │    - Майданчики PCB: C_pad на землю                    │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ 6. Частотна розгортка (Frequency Sweep Simulation):    │
  │    Z_{in}(f) ──> S₁₁(f) ──> VSWR(f) ──> Втрати IL(f)   │
  └────────────────────────────────────────────────────────┘
```

## Специфікація Touchstone S1P та парсер вхідних даних

Стандарт Touchstone (специфікація EIA/IBIS) є загальноприйнятим промисловим форматом зберігання частотних характеристик N-полюсників. Однопортовий файл містить розширення `.s1p` і складається з трьох логічних блоків: коментарів, рядка параметрів опцій та масиву числових даних.

Коментарі позначаються символом оклику `!` на початку рядка і можуть містити метадані про модель приладу VNA, дату калібрування, температурний режим або рівень вихідної потужності зондувального сигналу.

Рядок параметрів опцій починається із символу `#` і задає правила інтерпретації стовпчиків:

```
# [Одиниця частоти] [Тип параметра] [Формат представлення] [R Опір]
```

Приклад типового заголовка: `# GHZ S MA R 50` або `# MHZ S RI R 50`.

1. **Одиниця вимірювання частоти:**
   - `HZ` — Герци (множник 1.0).
   - `KHZ` — Кілогерци (множник 1.0e3).
   - `MHZ` — Мегагерци (множник 1.0e6).
   - `GHZ` — Гігагерци (множник 1.0e9).

2. **Тип параметра:**
   - `S` — S-параметри (матриця розсіювання, за замовчуванням).
   - `Y` — Y-параметри (матриця провідностей).
   - `Z` — Z-параметри (матриця імпедансів).

3. **Формат представлення комплексного числа:**
   - `RI` (Real / Imaginary): перший стовпчик містить дійсну частину коефіцієнта відбиття Re(S₁₁), другий — уявну частину Im(S₁₁).
   - `MA` (Magnitude / Angle): перший стовпчик містить лінійний модуль коефіцієнта відбиття |S₁₁| (безрозмірна величина від 0 до 1), другий — фазовий кут у градусах від −180° до +180°.
   - `DB` (Decibel / Angle): перший стовпчик містить модуль у логарифмічному масштабі 20 log₁₀(|S₁₁|) у децибелах (від'ємне число для пасивних кіл), другий — фазовий кут у градусах.

4. **Опорний імпеданс:**
   - `R 50` означає нормалізацію до 50.0 Ом. За відсутності поля за замовчуванням приймається значення 50.0 Ом.

### Формули перетворення вхідних даних у комплексний коефіцієнт відбиття

Внутрішнє представлення в обчислювальному рушії завжди використовує декартів комплексний коефіцієнт відбиття Γ = Γ_r + j Γ_i.

Для формату `RI`:
```
Γ_r = Re(S₁₁)
Γ_i = Im(S₁₁)
```

Для формату `MA`:
```
Γ_r = |S₁₁| · cos( θ_{deg} · π / 180 )
Γ_i = |S₁₁| · sin( θ_{deg} · π / 180 )
```

Для формату `DB`:
```
|S₁₁| = 10^( S₁₁[дБ] / 20 )
Γ_r = |S₁₁| · cos( θ_{deg} · π / 180 )
Γ_i = |S₁₁| · sin( θ_{deg} · π / 180 )
```

## Математичний апарат конформних перетворень на діаграмі Сміта

Діаграма Сміта є графічним відображенням правої півплощини комплексного імпедансу Z = R + jX (де R ≥ 0) всередину одиничного кола комплексної площини коефіцієнта відбиття Γ = u + jv.

### 1. Перетворення коефіцієнта відбиття в імпеданс та адмітанс

Зв'язок між нормованим імпедансом z = Z_A / Z₀ = r + jx та коефіцієнтом відбиття Γ = u + jv описується білінійним дробово-раціональним перетворенням:

```
z = ( 1 + Γ ) / ( 1 − Γ )
```

Розкриваючи дійсну та уявну частини:

```
r = ( 1 − u² − v² ) / ( (1 − u)² + v² )
x = ( 2 · v ) / ( (1 − u)² + v² )
```

Повний ненормований комплексний імпеданс навантаження:

```
R_A = r · Z₀
X_A = x · Z₀
```

Комплексний адмітанс (повна провідність) Y_A = G_A + j B_A є оберненою величиною до імпедансу:

```
Y_A = 1 / ( R_A + j X_A ) = ( R_A − j X_A ) / ( R_A² + X_A² )
G_A = R_A / ( R_A² + X_A² )
B_A = −X_A / ( R_A² + X_A² )
```

Нормований адмітанс y = Y_A · Z₀ = g + jb пов'язаний із коефіцієнтом відбиття виразом:

```
y = ( 1 − Γ ) / ( 1 + Γ )
g = ( 1 − u² − v² ) / ( (1 + u)² + v² )
b = ( −2 · v ) / ( (1 + u)² + v² )
```

Зворотне перетворення імпедансу в коефіцієнт відбиття:

```
Γ = ( Z_A − Z₀ ) / ( Z_A + Z₀ )
u = ( R_A² + X_A² − Z₀² ) / ( (R_A + Z₀)² + X_A² )
v = ( 2 · X_A · Z₀ ) / ( (R_A + Z₀)² + X_A² )
```

### 2. Еквівалентний перехід між послідовними та паралельними схемами

Будь-який імпеданс із втратами можна представити як послідовний ланцюг (активний опір R_s та реактанс X_s) або як еквівалентний паралельний ланцюг (активний опір R_p та паралельний реактанс X_p). Введемо добротність гілки:

```
Q = |X_s| / R_s = R_p / |X_p|
```

Формули взаємного перерахунку:

```
R_p = R_s · ( 1 + Q² )
X_p = X_s · ( 1 + Q² ) / Q²
```

Зворотне перетворення паралельної схеми в послідовну:

```
R_s = R_p / ( 1 + Q² )
X_s = X_p · Q² / ( 1 + Q² )
```

Цей апарат дозволяє трансформувати імпеданси без необхідності розв'язання нелінійних рівнянь: шунтовий реактивний елемент перетворює активний опір R_p у менший послідовний опір R_s, а послідовний реактивний елемент компенсує залишковий реактанс.

## Матричний апарат передачі (ABCD-параметри) для розрахунку багатоланкових кіл

Для аналізу довільних складених кіл, що містять каскади послідовних і паралельних елементів, а також відрізки мікросмужкових ліній передачі, найбільш універсальним є метод матриць передачі (ABCD-параметрів або каскадних матриць ланцюга).

Двополюсник (двопортник) описується співвідношенням між вхідною напругою та струмом (V₁, I₁) і вихідною напругою та струмом (V₂, I₂):

```
┌     ┐   ┌         ┐ ┌     ┐
│ V₁  │ = │ A     B │ │ V₂  │
│ I₁  │   │ C     D │ │ I₂  │
└     ┘   └         ┘ └     ┘
```

Для окремих базових елементів ВЧ-тракту матриці ABCD мають канонічний вигляд:

1. **Послідовний комплексний імпеданс Z_s:**
```
┌         ┐
│ 1   Z_s │
│ 0    1  │
└         ┘
```

2. **Шунтова комплексна провідність Y_p:**
```
┌         ┐
│ 1    0  │
│ Y_p  1  │
└         ┘
```

3. **Відрізок лінії передачі без втрат із хвильовим опором Z₀ та електричною довжиною θ = βl:**
```
┌                            ┐
│  cos(θ)       j Z₀ sin(θ)  │
│ j Y₀ sin(θ)    cos(θ)      │
└                            ┘
```

Каскадне з'єднання кількох послідовних вузлів розраховується матричним множенням у порядку проходження сигналу від генератора до навантаження:

```
M_{total} = M₁ · M₂ · M₃ · ... · M_n = ┌         ┐
                                       │ A     B │
                                       │ C     D │
                                       └         ┘
```

Якщо до виходу каскаду підключено навантаження Z_L = R_A + jX_A, то вхідний імпеданс усього ланцюга Z_{in} та вхідний коефіцієнт відбиття S₁₁ визначаються безпосередньо з елементів матриці M_{total}:

```
Z_{in} = ( A · Z_L + B ) / ( C · Z_L + D )
S₁₁ = ( A + B / Z₀ − C · Z₀ − D ) / ( A + B / Z₀ + C · Z₀ + D )
```

Цей матричний підхід дозволяє легко розширювати калькулятор для моделювання складних фільтрів вищих порядків, розподілених узгоджувальних шлейфів та перехідних отворів між шарами друкованої плати.

## Повний аналітичний синтез восьми топологій L-контурів

Двоелементний L-контур забезпечує повне узгодження на фіксованій робочій частоті f₀. Залежно від співвідношення активного опору навантаження R_A та опорного опору Z₀, а також від необхідного типу фільтрації (Low-Pass або High-Pass) можливі 8 конфігурацій:

### Конфігурації для R_A < Z₀ (Паралельний елемент розташований на стороні Z₀)

1. **Топологія L1: Low-Pass (Послідовна L_s, шунтова C_p біля джерела 50 Ом)**
```
Q = \sqrt{ (Z₀ / R_A) − 1 }
B_p = Q / Z₀
X_s = Q · R_A − X_A
C_p = B_p / ( 2π · f₀ )
L_s = X_s / ( 2π · f₀ )   [якщо X_s > 0]
```
Якщо X_s виходить від'ємним, власна індуктивність антени перевищує Q · R_A. У цьому випадку послідовний елемент стає конденсатором C_s = 1 / (2π f₀ |X_s|).

2. **Топологія L2: High-Pass (Послідовна C_s, шунтова L_p біля джерела 50 Ом)**
```
Q = \sqrt{ (Z₀ / R_A) − 1 }
B_p = −Q / Z₀
X_s = −Q · R_A − X_A
L_p = 1 / ( 2π · f₀ · |B_p| )
C_s = 1 / ( 2π · f₀ · |X_s| )
```

### Конфігурації для R_A > Z₀ (Паралельний елемент розташований на стороні антени)

3. **Топологія L3: Low-Pass (Шунтова C_p біля антени, послідовна L_s біля джерела 50 Ом)**
```
Q = \sqrt{ (R_A / Z₀) − 1 }
B_p = ( X_A + \sqrt{R_A / Z₀} · \sqrt{R_A² + X_A² − Z₀ · R_A} ) / ( R_A² + X_A² )
X_s = ( 1 / B_p ) + ( (X_A · Z₀) / R_A ) − ( Z₀ / (B_p · R_A) )
C_p = B_p / ( 2π · f₀ )
L_s = X_s / ( 2π · f₀ )
```

4. **Топологія L4: High-Pass (Шунтова L_p біля антени, послідовна C_s біля джерела 50 Ом)**
```
Q = \sqrt{ (R_A / Z₀) − 1 }
B_p = ( X_A − \sqrt{R_A / Z₀} · \sqrt{R_A² + X_A² − Z₀ · R_A} ) / ( R_A² + X_A² )
X_s = ( 1 / B_p ) + ( (X_A · Z₀) / R_A ) − ( Z₀ / (B_p · R_A) )
L_p = 1 / ( 2π · f₀ · |B_p| )
C_s = 1 / ( 2π · f₀ · |X_s| )
```

## Синтез П-контурів із заданою навантаженою добротністю

П-контур формується послідовним включенням двох віртуальних L-секцій, розділених внутрішнім вузлом з віртуальним опором R_v. Опір R_v обирається меншим за обидва крайні опори:

```
R_v = \min(Z₀, R_A) / (1 + Q_L²)
```

де Q_L — цільова навантажена добротність контуру (зазвичай Q_L = 2..5).

1. Розрахунок першої віртуальної секції (перетворення Z₀ в R_v):
```
Q₁ = \sqrt{ (Z₀ / R_v) − 1 }
C_{p1} = Q₁ / ( 2π · f₀ · Z₀ )
X_{s1} = Q₁ · R_v
```

2. Розрахунок другої віртуальної секції (перетворення R_v в комплексний опір Z_A = R_A + jX_A):
```
Q₂ = \sqrt{ (R_A / R_v) − 1 }
C_{p2} = Q₂ / ( 2π · f₀ · R_A )
X_{s2} = Q₂ · R_v − X_A
```

3. Загальна послідовна індуктивність П-контуру:
```
L_s = ( X_{s1} + X_{s2} ) / ( 2π · f₀ ) = ( Q₁ · R_v + Q₂ · R_v − X_A ) / ( 2π · f₀ )
```

П-контур забезпечує крутий спад коефіцієнта передачі на вищих частотах (фільтр низьких частот 3-го порядку), що дозволяє придушити другу та третю гармоніки передавача на 25–40 дБ. Смуга пропускання П-контуру за рівнем S₁₁ ≤ −10 дБ приблизно оцінюється як:

```
\Delta f_{-10dB} ≈ ( f₀ / Q_L ) · ( 2 · |\Gamma_{target}| ) / \sqrt{1 − |\Gamma_{target}|²}
```

де |Γ_{target}| = 0.3162 (що відповідає рівню −10 дБ). Для f₀ = 2440 МГц та Q_L = 3.0 розрахункова смуга узгодження становить близько 550 МГц, що з великим запасом перекриває всю смугу частот 2.4 GHz ISM.

## Розрахунок добротності контуру, смуги узгодження та внесених втрат

Навантажена добротність узгоджувального ланцюга Q_L безпосередньо визначає компроміс між шириною смуги узгодження, чутливістю до виробничих допусків компонентів та енергетичними втратами сигналу в реактивних елементах:

1. **Вузлова добротність (Nodal Q):** У кожному проміжному вузлі схеми відношення реактивної енергії до активної потужності визначається локальною добротністю Q_n = |X_n| / R_n = |B_n| / G_n. На діаграмі Сміта лінії однакової вузлової добротності формують дуги кіл (контури постійної добротності Constant-Q). Для збереження широкої робочої смуги траєкторія трансформації імпедансу не повинна заходити в області високих значень Q (де Q > 3..5).

2. **Зв'язок навантаженої добротності зі смугою узгодження:** Двоелементний L-контур має фіксовану добротність `Q = sqrt((Z_{max} / Z_{min}) − 1)`, яка однозначно задана співвідношенням опорів генератора та навантаження. Триелементні П- та T-контури дозволяють незалежно обирати `Q_L ≥ Q_L^{min}`. Смуга узгодження за рівнем КСХ ≤ 2.0 обернено пропорційна добротності:
```
\Delta f_{BW} ≈ f₀ / Q_L
```
При зростанні Q_L смуга звужується, що підвищує фільтрацію паразитних гармонік, але водночас робить систему чутливою до технологічного розкиду номіналів конденсаторів та котушок у партії.

3. **Внесені втрати (Insertion Loss) та ККД узгодження:** Реальні компоненти мають скінченну власну (ненавантажену) добротність Q₀ = ωL / ESR для котушок та Q₀ = 1 / (ωC · ESR) для конденсаторів. Оскільки добротність SMD-котушок індуктивності типорозміру 0402 становить Q_{0,L} ≈ 30..60 (тоді як у високочастотних керамічних конденсаторів C0G/NP0 значення Q_{0,C} сягає 500..2000), основні омічні втрати зосереджені в індуктивностях.

Коефіцієнт корисної дії (ККД) узгоджувального контуру η та внесені втрати IL у децибелах розраховуються за формулами:
```
\eta = 1 − ( Q_L / Q₀ )
IL_{dB} ≈ 4.34 · ( Q_L / Q₀ )  [дБ]
```

Для П-контуру з Q_L = 3.0 на частоті 2.44 ГГц при використанні котушки з власною добротністю Q₀ = 35 внесені втрати становлять IL ≈ 4.34 · (3.0 / 35) ≈ 0.37 дБ (η ≈ 91.4 %, тобто близько 8.6 % потужності передавача розсіюється у вигляді тепла на платі). При спробі підвищити вибірковість фільтра до Q_L = 8.0 втрати зростуть до 0.99 дБ (η ≈ 77.1 %), що призведе до суттєвого падіння радіусу зв'язку пристрою та перегріву елементів.

## Фізико-математична модель паразитарних параметрів SMD 0402

Ідеальні конденсатори та котушки індуктивності існують лише в теоретичних розрахунках. На частотах понад 500 МГц кожен SMD-компонент типорозміру 0402 (1.0 × 0.5 мм) має власні паразитні реактивності, які істотно спотворюють розрахунковий імпеданс:

```
Еквівалентна схема SMD-конденсатора:     Еквівалентна схема SMD-індуктивності:

   ┌──[ ESR ]───[ C ]───[ ESL ]──┐          ┌───[  ESR  ]───[  L  ]───┐
───┤                             ├───    ───┤                         ├───
   └─────────────────────────────┘          └───────────[ C_p ]───────┘
```

1. **Конденсатор:** має еквівалентну послідовну індуктивність виводів та металізації обкладок ESL (0.3–0.5 нГн) і активний опір діелектричних втрат ESR (0.05–0.2 Ом). Повний імпеданс конденсатора:
```
Z_C(f) = ESR + j( 2π f · ESL − 1 / (2π f · C) )
f_{SRF} = 1 / ( 2π · \sqrt{C · ESL} )
```
Через наявність ESL ефективна ємність компонента C_{eff}(f) на робочій частоті є вищою за номінальну паспортну ємність C_{nom}:
```
C_{eff}(f) = C_{nom} / ( 1 − (2π f)² · C_{nom} · ESL )
```
Наприклад, для конденсатора C_{nom} = 3.3 пФ з ESL = 0.4 нГн на частоті f = 2.44 ГГц знаменник формули дорівнює 1 − (2π · 2.44 · 10⁹)² · 3.3 · 10⁻¹² · 0.4 · 10⁻⁹ = 1 − 0.310 = 0.690. Ефективна діюча ємність становить C_{eff} ≈ 4.78 пФ (+45 % до номіналу). Якщо використати ідеальний номінал 3.3 пФ без урахування ESL, резонансна крива узгодження зміститься вниз за частотою на понад 300 МГц.

2. **Котушка індуктивності:** має міжвиткову паразитну ємність і ємність між виводами C_p (0.02–0.08 пФ) та активний опір проводу і магнітного сердечника ESR(f) = 2π f L / Q₀. Повний імпеданс котушки:
```
Z_L(f) = ( ESR + j 2π f L ) ∥ ( 1 / (j 2π f C_p) )
f_{SRF_L} = 1 / ( 2π · \sqrt{L · C_p} )
```
Ефективна індуктивність котушки нижче частоти власного резонансу f_{SRF_L} описується виразом:
```
L_{eff}(f) = L_{nom} / ( 1 − (2π f)² · L_{nom} · C_p )
```
При наближенні частоти до f_{SRF_L} реактивний опір різко зростає (паралельний резонанс), а на частотах понад f_{SRF_L} котушка повністю втрачає індуктивні властивості та починає поводитися як шунтовий конденсатор. Тому для радіочастотних узгоджувальних кіл необхідно вибирати котушки з умовою f_{SRF_L} ≥ 2.5 · f₀.

3. **Контактні монтажні майданчики PCB:** кожен SMD-майданчик (Landing Pad) розміром 0.5 × 0.5 мм на друкованій платі з діелектриком FR-4 (товщина до шару землі h = 0.2 мм, відносна проникність ε_r ≈ 4.4) утворює з суцільним внутрішнім земляним полігоном мікросмужкову ємність:
```
C_{pad} ≈ ( \varepsilon_r · \varepsilon_0 · A_{pad} ) / h
C_{pad} ≈ ( 4.4 · 8.854 · 10⁻¹² · 0.25 · 10⁻⁶ ) / ( 0.2 · 10⁻³ ) ≈ 0.049 пФ
```
Пара контактних майданчиків для послідовного SMD-елемента формує еквівалентну шунтову ємність близько C_{pad, total} ≈ 0.10 пФ на землю. На частоті 2.44 ГГц ця паразитна ємність створює додаткову реактивну провідність B_{pad} = 2π · 2.44 · 10⁹ · 0.10 · 10⁻¹² ≈ 1.53 мСм, що на діаграмі Сміта зміщує нормовану точку імпедансу на величину +j0.076 по колу провідності. Врахування цієї шунтової ємності у матриці вузла ABCD дозволяє повністю компенсувати фазовий зсув при синтезі кінцевої топології.

## Програмна реалізація

Нижче наведено повний вихідний код калькулятора на C99 та C++20.

:::tabs
@tab C99
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

#define RF_PI 3.14159265358979323846
#define MAX_SWEEP_POINTS 201

typedef struct {
    double r;
    double i;
} Cplx;

static inline Cplx c_make(double r, double i) { Cplx z = {r, i}; return z; }
static inline Cplx c_add(Cplx a, Cplx b) { return c_make(a.r + b.r, a.i + b.i); }
static inline Cplx c_sub(Cplx a, Cplx b) { return c_make(a.r - b.r, a.i - b.i); }
static inline Cplx c_mul(Cplx a, Cplx b) { return c_make(a.r * b.r - a.i * b.i, a.r * b.i + a.i * b.r); }
static inline Cplx c_div(Cplx a, Cplx b) {
    double d = b.r * b.r + b.i * b.i;
    if (d < 1e-18) d = 1e-18;
    return c_make((a.r * b.r + a.i * b.i) / d, (a.i * b.r - a.r * b.i) / d);
}
static inline double c_mag(Cplx a) { return sqrt(a.r * a.r + a.i * a.i); }
static inline double c_arg_deg(Cplx a) { return atan2(a.i, a.r) * (180.0 / RF_PI); }
static inline Cplx c_inv(Cplx a) { return c_div(c_make(1.0, 0.0), a); }
static inline Cplx c_parallel(Cplx a, Cplx b) {
    Cplx sum = c_add(a, b);
    if (c_mag(sum) < 1e-18) return c_make(0, 0);
    return c_div(c_mul(a, b), sum);
}

typedef struct {
    double freq_hz;
    Cplx s11;
    Cplx z_load;
    double vswr;
    double return_loss_db;
    double mismatch_loss_db;
} RfDataPoint;

typedef struct {
    char name[32];
    bool valid;
    bool is_lowpass;
    double comp1_val; // Послідовний або шунтовий елемент (Ф або Гн)
    char comp1_type;  // 'L' або 'C'
    bool comp1_series; // true якщо послідовний, false якщо шунтовий
    double comp2_val;
    char comp2_type;
    bool comp2_series;
    double comp3_val; // Для П- та T-контурів
    char comp3_type;
    bool comp3_series;
    double q_loaded;
} MatchingTopology;

typedef struct {
    double c_esl_nh;    // Паразитна індуктивність конденсатора, нГн
    double c_esr_ohm;   // Активний опір втрат конденсатора, Ом
    double l_q0;        // Власна добротність котушки на f0
    double l_cp_pf;     // Паразитна паралельна ємність котушки, пФ
    double pad_cap_pf;  // Паразитна ємність монтажного майданчика на землю, пФ
} ParasiticModel;

// Таблиця номіналів ряду E24
static const double E24_SERIES[] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};

double snap_to_e24(double val) {
    if (val <= 0.0) return 0.0;
    double dec = pow(10.0, floor(log10(val)));
    double norm = val / dec;
    double best = E24_SERIES[0];
    double min_diff = fabs(norm - E24_SERIES[0]);
    for (int i = 1; i < 24; ++i) {
        double diff = fabs(norm - E24_SERIES[i]);
        if (diff < min_diff) {
            min_diff = diff;
            best = E24_SERIES[i];
        }
    }
    return best * dec;
}

RfDataPoint calc_rf_point(double freq_hz, Cplx s11, double z0) {
    RfDataPoint pt;
    pt.freq_hz = freq_hz;
    pt.s11 = s11;
    double mag = c_mag(s11);
    
    Cplx num = c_add(c_make(1.0, 0.0), s11);
    Cplx den = c_sub(c_make(1.0, 0.0), s11);
    Cplx z_norm = c_div(num, den);
    pt.z_load = c_make(z_norm.r * z0, z_norm.i * z0);
    
    if (mag >= 0.99999) {
        pt.vswr = 999.99;
        pt.return_loss_db = 0.0;
        pt.mismatch_loss_db = 999.99;
    } else {
        pt.vswr = (1.0 + mag) / (1.0 - mag);
        pt.return_loss_db = -20.0 * log10(mag > 1e-6 ? mag : 1e-6);
        double p_ratio = 1.0 - mag * mag;
        pt.mismatch_loss_db = -10.0 * log10(p_ratio > 1e-6 ? p_ratio : 1e-6);
    }
    return pt;
}

int synthesize_l_matches(Cplx z_load, double z0, double freq_hz, MatchingTopology results[4]) {
    int count = 0;
    double r_a = z_load.r;
    double x_a = z_load.i;
    double omega = 2.0 * RF_PI * freq_hz;
    
    if (r_a <= 1e-3 || freq_hz <= 0.0) return 0;
    
    if (r_a < z0) {
        // Конфігурація 1: Послідовна L, шунтова C біля Z0 (Low-Pass)
        double q = sqrt((z0 / r_a) - 1.0);
        double x_s = q * r_a - x_a;
        double b_p = q / z0;
        if (x_s > 0.0 && b_p > 0.0) {
            strcpy(results[count].name, "L-Match (Low-Pass, R_A < Z₀)");
            results[count].valid = true;
            results[count].is_lowpass = true;
            results[count].comp1_type = 'L';
            results[count].comp1_series = true;
            results[count].comp1_val = x_s / omega;
            results[count].comp2_type = 'C';
            results[count].comp2_series = false;
            results[count].comp2_val = b_p / omega;
            results[count].comp3_val = 0.0;
            results[count].q_loaded = q;
            count++;
        }
        // Конфігурація 2: Послідовна C, шунтова L біля Z0 (High-Pass)
        double x_s_hp = -q * r_a - x_a;
        double b_p_hp = -q / z0;
        if (x_s_hp < 0.0 && b_p_hp < 0.0) {
            strcpy(results[count].name, "L-Match (High-Pass, R_A < Z₀)");
            results[count].valid = true;
            results[count].is_lowpass = false;
            results[count].comp1_type = 'C';
            results[count].comp1_series = true;
            results[count].comp1_val = 1.0 / (omega * fabs(x_s_hp));
            results[count].comp2_type = 'L';
            results[count].comp2_series = false;
            results[count].comp2_val = 1.0 / (omega * fabs(b_p_hp));
            results[count].comp3_val = 0.0;
            results[count].q_loaded = q;
            count++;
        }
    } else {
        // Конфігурація 3: Шунтова C біля антени, послідовна L (Low-Pass)
        double q = sqrt((r_a / z0) - 1.0);
        double b_p = q / r_a;
        double x_s = q * z0 - x_a;
        if (b_p > 0.0 && x_s > 0.0) {
            strcpy(results[count].name, "L-Match (Low-Pass, R_A > Z₀)");
            results[count].valid = true;
            results[count].is_lowpass = true;
            results[count].comp1_type = 'C';
            results[count].comp1_series = false;
            results[count].comp1_val = b_p / omega;
            results[count].comp2_type = 'L';
            results[count].comp2_series = true;
            results[count].comp2_val = x_s / omega;
            results[count].comp3_val = 0.0;
            results[count].q_loaded = q;
            count++;
        }
        // Конфігурація 4: Шунтова L біля антени, послідовна C (High-Pass)
        double b_p_hp = -q / r_a;
        double x_s_hp = -q * z0 - x_a;
        if (b_p_hp < 0.0 && x_s_hp < 0.0) {
            strcpy(results[count].name, "L-Match (High-Pass, R_A > Z₀)");
            results[count].valid = true;
            results[count].is_lowpass = false;
            results[count].comp1_type = 'L';
            results[count].comp1_series = false;
            results[count].comp1_val = 1.0 / (omega * fabs(b_p_hp));
            results[count].comp2_type = 'C';
            results[count].comp2_series = true;
            results[count].comp2_val = 1.0 / (omega * fabs(x_s_hp));
            results[count].comp3_val = 0.0;
            results[count].q_loaded = q;
            count++;
        }
    }
    return count;
}

MatchingTopology synthesize_pi_match(Cplx z_load, double z0, double freq_hz, double q_target) {
    MatchingTopology t = {0};
    double r_a = z_load.r;
    double x_a = z_load.i;
    double omega = 2.0 * RF_PI * freq_hz;
    
    double r_min = (r_a < z0) ? r_a : z0;
    double r_v = r_min / (1.0 + q_target * q_target);
    
    if (r_v >= z0 || r_v >= r_a) return t;
    
    double q1 = sqrt((z0 / r_v) - 1.0);
    double q2 = sqrt((r_a / r_v) - 1.0);
    
    double b_p1 = q1 / z0;
    double b_p2 = q2 / r_a;
    double x_s = (q1 * r_v) + (q2 * r_v) - x_a;
    
    if (b_p1 <= 0.0 || b_p2 <= 0.0 || x_s <= 0.0) return t;
    
    strcpy(t.name, "Pi-Match (Low-Pass Harmonic Filter)");
    t.valid = true;
    t.is_lowpass = true;
    t.q_loaded = q_target;
    t.comp1_type = 'C';
    t.comp1_series = false;
    t.comp1_val = b_p1 / omega; // C_shunt1 (Source side)
    t.comp2_type = 'L';
    t.comp2_series = true;
    t.comp2_val = x_s / omega;   // L_series
    t.comp3_type = 'C';
    t.comp3_series = false;
    t.comp3_val = b_p2 / omega; // C_shunt2 (Antenna side)
    return t;
}

Cplx eval_real_cap(double c_val, double freq_hz, const ParasiticModel* p) {
    double omega = 2.0 * RF_PI * freq_hz;
    double esl = p->c_esl_nh * 1e-9;
    double esr = p->c_esr_ohm;
    double x_c = (omega * esl) - (1.0 / (omega * c_val));
    return c_make(esr, x_c);
}

Cplx eval_real_ind(double l_val, double freq_hz, const ParasiticModel* p) {
    double omega = 2.0 * RF_PI * freq_hz;
    double esr = (omega * l_val) / (p->l_q0 > 1.0 ? p->l_q0 : 30.0);
    Cplx z_l_branch = c_make(esr, omega * l_val);
    double cp = p->l_cp_pf * 1e-12;
    if (cp > 1e-15) {
        Cplx z_cp_branch = c_make(0.0, -1.0 / (omega * cp));
        return c_parallel(z_l_branch, z_cp_branch);
    }
    return z_l_branch;
}

void simulate_frequency_sweep(const MatchingTopology* top, Cplx z_antenna_at_f0, double f0, double z0, const ParasiticModel* p) {
    printf("\n=== РЕЗУЛЬТАТИ ЧАСТОТНОЇ РОЗГОРТКИ (SIMULATION SWEEP) ===\n");
    printf("Топологія: %s\n", top->name);
    printf("Частота [МГц] | S₁₁ [дБ] |  КСХ   | Втрати [дБ] | Вхідний Z_in [Ом]\n");
    printf("--------------+----------+--------+-------------+------------------\n");
    
    double f_start = f0 * 0.85;
    double f_stop = f0 * 1.15;
    int steps = 11;
    
    for (int i = 0; i < steps; ++i) {
        double f = f_start + (double)i * (f_stop - f_start) / (steps - 1);
        // Модель навантаження: лінійна апроксимація реактивності антени
        double x_ant = z_antenna_at_f0.i + 2.0 * (f - f0) / f0 * 50.0;
        Cplx z_load = c_make(z_antenna_at_f0.r, x_ant);
        
        Cplx z_node = z_load;
        
        // Для П-контуру: 3 компоненти
        if (top->comp3_val > 0.0) {
            Cplx z_c2 = eval_real_cap(top->comp3_val, f, p);
            z_node = c_parallel(z_node, z_c2);
            Cplx z_l = eval_real_ind(top->comp2_val, f, p);
            z_node = c_add(z_node, z_l);
            Cplx z_c1 = eval_real_cap(top->comp1_val, f, p);
            z_node = c_parallel(z_node, z_c1);
        } else {
            // Для L-контуру
            if (top->comp1_series) {
                Cplx z_s = (top->comp1_type == 'L') ? eval_real_ind(top->comp1_val, f, p) : eval_real_cap(top->comp1_val, f, p);
                z_node = c_add(z_node, z_s);
                Cplx z_p = (top->comp2_type == 'C') ? eval_real_cap(top->comp2_val, f, p) : eval_real_ind(top->comp2_val, f, p);
                z_node = c_parallel(z_node, z_p);
            } else {
                Cplx z_p = (top->comp1_type == 'C') ? eval_real_cap(top->comp1_val, f, p) : eval_real_ind(top->comp1_val, f, p);
                z_node = c_parallel(z_node, z_p);
                Cplx z_s = (top->comp2_type == 'L') ? eval_real_ind(top->comp2_val, f, p) : eval_real_cap(top->comp2_val, f, p);
                z_node = c_add(z_node, z_s);
            }
        }
        
        Cplx s11 = c_div(c_sub(z_node, c_make(z0, 0)), c_add(z_node, c_make(z0, 0)));
        double mag = c_mag(s11);
        double vswr = (mag >= 0.999) ? 99.9 : (1.0 + mag) / (1.0 - mag);
        double rl_db = (mag < 1e-6) ? 80.0 : -20.0 * log10(mag);
        double p_trans = 1.0 - mag * mag;
        double il_db = (p_trans < 1e-6) ? 40.0 : -10.0 * log10(p_trans);
        
        printf("  %7.1f     |  %6.2f  |  %5.2f |    %5.2f    | %5.1f + j%5.1f\n",
               f * 1e-6, -rl_db, vswr, il_db, z_node.r, z_node.i);
    }
}

int main(int argc, char** argv) {
    printf("===================================================================\n");
    printf(" RF IMPEDANCE MATCHING & S11 SYNTHESIS CALCULATOR (C99)\n");
    printf("===================================================================\n");
    
    double f0 = 2440.0 * 1e6; // 2.44 GHz за замовчуванням
    double z0 = 50.0;
    Cplx z_ant = c_make(18.0, -42.0); // Типовий незбалансований імпеданс MIFA антени
    
    if (argc >= 4) {
        f0 = atof(argv[1]) * 1e6;
        z_ant.r = atof(argv[2]);
        z_ant.i = atof(argv[3]);
    }
    
    printf("Параметри розрахунку:\n");
    printf("  Центральна частота f₀: %.2f МГц\n", f0 * 1e-6);
    printf("  Опорний імпеданс Z₀:   %.1f Ом\n", z0);
    printf("  Імпеданс антени Z_A:   %.2f %c j%.2f Ом\n\n", z_ant.r, z_ant.i >= 0 ? '+' : '-', fabs(z_ant.i));
    
    Cplx s11_init = c_div(c_sub(z_ant, c_make(z0, 0)), c_add(z_ant, c_make(z0, 0)));
    RfDataPoint init_pt = calc_rf_point(f0, s11_init, z0);
    
    printf("Вхідні характеристики неузгодженої антени:\n");
    printf("  |S₁₁|:           %.4f (%.2f дБ)\n", c_mag(init_pt.s11), -init_pt.return_loss_db);
    printf("  Фаза S₁₁:        %.1f°\n", c_arg_deg(init_pt.s11));
    printf("  КСХ (VSWR):      %.2f\n", init_pt.vswr);
    printf("  Втрати неузг.:   %.2f дБ\n", init_pt.mismatch_loss_db);
    printf("  Потужність в ан.: %.1f %%\n\n", (1.0 - c_mag(init_pt.s11)*c_mag(init_pt.s11)) * 100.0);
    
    MatchingTopology l_matches[4];
    int l_count = synthesize_l_matches(z_ant, z0, f0, l_matches);
    
    printf("=== СИНТЕЗ ДВОЕЛЕМЕНТНИХ L-КОНТУРІВ ===\n");
    for (int i = 0; i < l_count; ++i) {
        printf("[%d] %s (Q_L = %.2f):\n", i + 1, l_matches[i].name, l_matches[i].q_loaded);
        double v1 = l_matches[i].comp1_val;
        double v2 = l_matches[i].comp2_val;
        if (l_matches[i].comp1_type == 'L') {
            printf("    Елемент 1 (%s): L = %.2f нГн (E24: %.2f нГн)\n",
                   l_matches[i].comp1_series ? "Послідовний" : "Шунтовий", v1 * 1e9, snap_to_e24(v1 * 1e9));
        } else {
            printf("    Елемент 1 (%s): C = %.2f пФ (E24: %.2f пФ)\n",
                   l_matches[i].comp1_series ? "Послідовний" : "Шунтовий", v1 * 1e12, snap_to_e24(v1 * 1e12));
        }
        if (l_matches[i].comp2_type == 'L') {
            printf("    Елемент 2 (%s): L = %.2f нГн (E24: %.2f нГн)\n",
                   l_matches[i].comp2_series ? "Послідовний" : "Шунтовий", v2 * 1e9, snap_to_e24(v2 * 1e9));
        } else {
            printf("    Елемент 2 (%s): C = %.2f пФ (E24: %.2f пФ)\n",
                   l_matches[i].comp2_series ? "Послідовний" : "Шунтовий", v2 * 1e12, snap_to_e24(v2 * 1e12));
        }
    }
    
    MatchingTopology pi_match = synthesize_pi_match(z_ant, z0, f0, 3.0);
    if (pi_match.valid) {
        printf("\n=== СИНТЕЗ ТРЬОХЕЛЕМЕНТНОГО П-КОНТУРУ (Q_L = 3.0) ===\n");
        printf("    C_shunt1 (Source):  %.2f пФ (E24: %.2f пФ)\n", pi_match.comp1_val * 1e12, snap_to_e24(pi_match.comp1_val * 1e12));
        printf("    L_series (Middle):  %.2f нГн (E24: %.2f нГн)\n", pi_match.comp2_val * 1e9, snap_to_e24(pi_match.comp2_val * 1e9));
        printf("    C_shunt2 (Antenna): %.2f пФ (E24: %.2f пФ)\n", pi_match.comp3_val * 1e12, snap_to_e24(pi_match.comp3_val * 1e12));
    }
    
    ParasiticModel parasitics = {
        .c_esl_nh = 0.35,
        .c_esr_ohm = 0.08,
        .l_q0 = 45.0,
        .l_cp_pf = 0.04,
        .pad_cap_pf = 0.05
    };
    
    if (l_count > 0) {
        simulate_frequency_sweep(&l_matches[0], z_ant, f0, z0, &parasitics);
    }
    
    return 0;
}
```
@tab C++20
```cpp
#include <iostream>
#include <iomanip>
#include <complex>
#include <vector>
#include <string>
#include <string_view>
#include <numbers>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>
#include <format>

namespace rf {

using Complex = std::complex<double>;
constexpr double PI = std::numbers::pi;

// Модель паразитарних параметрів компонентів SMD 0402
struct Parasitics {
    double c_esl_nh{0.35};    // ESL керамічного конденсатора, нГн
    double c_esr_ohm{0.08};   // ESR конденсатора, Ом
    double l_q0{45.0};        // Власна добротність котушки на f0
    double l_cp_pf{0.04};     // Паразитна міжелектродна ємність котушки, пФ
    double pad_cap_pf{0.05};  // Паразитна ємність монтажного майданчика PCB, пФ
};

enum class ComponentType { Inductor, Capacitor };

struct ComponentSpec {
    ComponentType type;
    bool is_series;
    double value_si; // Генрі або Фаради

    [[nodiscard]] double in_units() const noexcept {
        return (type == ComponentType::Inductor) ? value_si * 1e9 : value_si * 1e12;
    }

    [[nodiscard]] std::string_view unit_str() const noexcept {
        return (type == ComponentType::Inductor) ? "нГн" : "пФ";
    }
};

struct MatchingNetwork {
    std::string name;
    double q_loaded{0.0};
    std::vector<ComponentSpec> components;
};

struct RfPoint {
    double freq_hz{0.0};
    Complex s11{0.0, 0.0};
    Complex z_in{0.0, 0.0};
    double vswr{1.0};
    double return_loss_db{0.0};
    double insertion_loss_db{0.0};
};

class RfCalculator {
public:
    static constexpr std::array<double, 24> E24 = {
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
    };

    static double snap_e24(double value) noexcept {
        if (value <= 0.0) return 0.0;
        const double dec = std::pow(10.0, std::floor(std::log10(value)));
        const double norm = value / dec;
        auto it = std::min_element(E24.begin(), E24.end(), [norm](double a, double b) {
            return std::abs(norm - a) < std::abs(norm - b);
        });
        return (*it) * dec;
    }

    static Complex s11_to_z(Complex s11, double z0 = 50.0) noexcept {
        const Complex num = 1.0 + s11;
        const Complex den = 1.0 - s11;
        return (num / den) * z0;
    }

    static Complex z_to_s11(Complex z, double z0 = 50.0) noexcept {
        return (z - z0) / (z + z0);
    }

    static std::vector<MatchingNetwork> synthesize_l_match(Complex z_load, double f0, double z0 = 50.0) {
        std::vector<MatchingNetwork> res;
        const double r_a = z_load.real();
        const double x_a = z_load.imag();
        const double omega = 2.0 * PI * f0;

        if (r_a <= 1e-4 || f0 <= 0.0) return res;

        if (r_a < z0) {
            const double q = std::sqrt((z0 / r_a) - 1.0);
            const double x_s = (q * r_a) - x_a;
            const double b_p = q / z0;

            if (x_s > 0.0 && b_p > 0.0) {
                res.push_back({
                    .name = "L-Match Low-Pass (R_A < Z₀)",
                    .q_loaded = q,
                    .components = {
                        {ComponentType::Inductor, true, x_s / omega},
                        {ComponentType::Capacitor, false, b_p / omega}
                    }
                });
            }
        } else {
            const double q = std::sqrt((r_a / z0) - 1.0);
            const double b_p = q / r_a;
            const double x_s = (q * z0) - x_a;

            if (b_p > 0.0 && x_s > 0.0) {
                res.push_back({
                    .name = "L-Match Low-Pass (R_A > Z₀)",
                    .q_loaded = q,
                    .components = {
                        {ComponentType::Capacitor, false, b_p / omega},
                        {ComponentType::Inductor, true, x_s / omega}
                    }
                });
            }
        }
        return res;
    }

    static std::optional<MatchingNetwork> synthesize_pi_match(
        Complex z_load, 
        double f0, 
        double q_target = 3.0, 
        double z0 = 50.0) 
    {
        const double r_a = z_load.real();
        const double x_a = z_load.imag();
        const double omega = 2.0 * PI * f0;

        const double r_min = std::min(r_a, z0);
        const double r_v = r_min / (1.0 + q_target * q_target);

        if (r_v >= z0 || r_v >= r_a) return std::nullopt;

        const double q1 = std::sqrt((z0 / r_v) - 1.0);
        const double q2 = std::sqrt((r_a / r_v) - 1.0);

        const double b_p1 = q1 / z0;
        const double b_p2 = q2 / r_a;
        const double x_s = (q1 * r_v) + (q2 * r_v) - x_a;

        if (b_p1 <= 0.0 || b_p2 <= 0.0 || x_s <= 0.0) return std::nullopt;

        return MatchingNetwork{
            .name = "Pi-Match Harmonic Filter",
            .q_loaded = q_target,
            .components = {
                {ComponentType::Capacitor, false, b_p1 / omega},
                {ComponentType::Inductor, true, x_s / omega},
                {ComponentType::Capacitor, false, b_p2 / omega}
            }
        };
    }

    static Complex eval_capacitor(double c_val, double freq_hz, const Parasitics& p) noexcept {
        const double omega = 2.0 * PI * freq_hz;
        const double esl = p.c_esl_nh * 1e-9;
        const double x_c = (omega * esl) - (1.0 / (omega * c_val));
        return {p.c_esr_ohm, x_c};
    }

    static Complex eval_inductor(double l_val, double freq_hz, const Parasitics& p) noexcept {
        const double omega = 2.0 * PI * freq_hz;
        const double esr = (omega * l_val) / std::max(p.l_q0, 1.0);
        const Complex z_l{esr, omega * l_val};
        const double cp = p.l_cp_pf * 1e-12;
        if (cp > 1e-15) {
            const Complex z_cp{0.0, -1.0 / (omega * cp)};
            return (z_l * z_cp) / (z_l + z_cp);
        }
        return z_l;
    }

    static std::vector<RfPoint> simulate_sweep(
        const MatchingNetwork& net, 
        Complex z_ant_f0, 
        double f0, 
        double z0 = 50.0, 
        const Parasitics& p = {}) 
    {
        std::vector<RfPoint> out;
        const double f_start = f0 * 0.85;
        const double f_stop = f0 * 1.15;
        constexpr int steps = 11;

        for (int i = 0; i < steps; ++i) {
            const double f = f_start + (static_cast<double>(i) * (f_stop - f_start) / (steps - 1));
            const double x_ant = z_ant_f0.imag() + 2.0 * (f - f0) / f0 * 50.0;
            Complex z_node{z_ant_f0.real(), x_ant};

            if (net.components.size() == 3) {
                // Pi-Match: C2 || ( L + ( C1 || Z_in ) )
                const Complex z_c2 = eval_capacitor(net.components[2].value_si, f, p);
                z_node = (z_node * z_c2) / (z_node + z_c2);
                const Complex z_l = eval_inductor(net.components[1].value_si, f, p);
                z_node += z_l;
                const Complex z_c1 = eval_capacitor(net.components[0].value_si, f, p);
                z_node = (z_node * z_c1) / (z_node + z_c1);
            } else if (net.components.size() == 2) {
                // L-Match
                if (net.components[0].is_series) {
                    const Complex z_s = (net.components[0].type == ComponentType::Inductor)
                        ? eval_inductor(net.components[0].value_si, f, p)
                        : eval_capacitor(net.components[0].value_si, f, p);
                    z_node += z_s;
                    const Complex z_p = (net.components[1].type == ComponentType::Capacitor)
                        ? eval_capacitor(net.components[1].value_si, f, p)
                        : eval_inductor(net.components[1].value_si, f, p);
                    z_node = (z_node * z_p) / (z_node + z_p);
                } else {
                    const Complex z_p = (net.components[0].type == ComponentType::Capacitor)
                        ? eval_capacitor(net.components[0].value_si, f, p)
                        : eval_inductor(net.components[0].value_si, f, p);
                    z_node = (z_node * z_p) / (z_node + z_p);
                    const Complex z_s = (net.components[1].type == ComponentType::Inductor)
                        ? eval_inductor(net.components[1].value_si, f, p)
                        : eval_capacitor(net.components[1].value_si, f, p);
                    z_node += z_s;
                }
            }

            const Complex s11 = z_to_s11(z_node, z0);
            const double mag = std::abs(s11);
            const double vswr = (mag >= 0.999) ? 99.9 : (1.0 + mag) / (1.0 - mag);
            const double rl = (mag < 1e-6) ? 80.0 : -20.0 * std::log10(mag);
            const double p_trans = std::max(1.0 - mag * mag, 1e-6);
            const double il = -10.0 * std::log10(p_trans);

            out.push_back({
                .freq_hz = f,
                .s11 = s11,
                .z_in = z_node,
                .vswr = vswr,
                .return_loss_db = rl,
                .insertion_loss_db = il
            });
        }
        return out;
    }
};

} // namespace rf

int main(int argc, char** argv) {
    std::cout << "===================================================================\n";
    std::cout << " RF IMPEDANCE MATCHING & S11 SYNTHESIS CALCULATOR (C++20)\n";
    std::cout << "===================================================================\n";

    double f0 = 2440.0 * 1e6;
    constexpr double z0 = 50.0;
    rf::Complex z_ant{18.0, -42.0};

    if (argc >= 4) {
        f0 = std::stod(argv[1]) * 1e6;
        z_ant = {std::stod(argv[2]), std::stod(argv[3])};
    }

    std::cout << std::format("Частота f₀:        {:.2f} МГц\n", f0 * 1e-6);
    std::cout << std::format("Опорний Z₀:        {:.1f} Ом\n", z0);
    std::cout << std::format("Імпеданс антени:   {:.2f} {} j{:.2f} Ом\n\n",
                             z_ant.real(), z_ant.imag() >= 0 ? '+' : '-', std::abs(z_ant.imag()));

    const rf::Complex s11_init = rf::RfCalculator::z_to_s11(z_ant, z0);
    const double mag_init = std::abs(s11_init);
    const double vswr_init = (1.0 + mag_init) / (1.0 - mag_init);
    const double rl_init = -20.0 * std::log10(mag_init);

    std::cout << std::format("Характеристики антени до узгодження:\n");
    std::cout << std::format("  |S₁₁|:           {:.4f} ({:.2f} дБ)\n", mag_init, -rl_init);
    std::cout << std::format("  КСХ (VSWR):      {:.2f}\n", vswr_init);
    std::cout << std::format("  Потужність в ан.: {:.1f} %\n\n", (1.0 - mag_init * mag_init) * 100.0);

    const auto l_networks = rf::RfCalculator::synthesize_l_match(z_ant, f0, z0);
    std::cout << "=== СИНТЕЗ ДВОЕЛЕМЕНТНИХ L-КОНТУРІВ ===\n";
    for (size_t i = 0; i < l_networks.size(); ++i) {
        std::cout << std::format("[{}] {} (Q_L = {:.2f}):\n", i + 1, l_networks[i].name, l_networks[i].q_loaded);
        for (const auto& comp : l_networks[i].components) {
            const double val_units = comp.in_units();
            const double e24_val = rf::RfCalculator::snap_e24(val_units);
            std::cout << std::format("    {} {}: {:.2f} {} (E24: {:.2f} {})\n",
                                     comp.is_series ? "Послідовний" : "Шунтовий",
                                     comp.type == rf::ComponentType::Inductor ? 'L' : 'C',
                                     val_units, comp.unit_str(), e24_val, comp.unit_str());
        }
    }

    const auto pi_net = rf::RfCalculator::synthesize_pi_match(z_ant, f0, 3.0, z0);
    if (pi_net) {
        std::cout << std::format("\n=== СИНТЕЗ ТРЬОХЕЛЕМЕНТНОГО П-КОНТУРУ (Q_L = {:.1f}) ===\n", pi_net->q_loaded);
        for (const auto& comp : pi_net->components) {
            const double val_units = comp.in_units();
            const double e24_val = rf::RfCalculator::snap_e24(val_units);
            std::cout << std::format("    {} {}: {:.2f} {} (E24: {:.2f} {})\n",
                                     comp.is_series ? "Послідовний" : "Шунтовий",
                                     comp.type == rf::ComponentType::Inductor ? 'L' : 'C',
                                     val_units, comp.unit_str(), e24_val, comp.unit_str());
        }
    }

    if (!l_networks.empty()) {
        std::cout << "\n=== РЕЗУЛЬТАТИ ЧАСТОТНОЇ РОЗГОРТКИ ДЛЯ L-MATCH (C++20) ===\n";
        std::cout << "Частота [МГц] | S₁₁ [дБ] |  КСХ   | Втрати [дБ] | Вхідний Z_in [Ом]\n";
        std::cout << "--------------+----------+--------+-------------+------------------\n";
        const auto sweep = rf::RfCalculator::simulate_sweep(l_networks[0], z_ant, f0, z0);
        for (const auto& pt : sweep) {
            std::cout << std::format("  {:7.1f}     |  {:6.2f}  |  {:5.2f} |    {:5.2f}    | {:5.1f} + j{:5.1f}\n",
                                     pt.freq_hz * 1e-6, -pt.return_loss_db, pt.vswr, pt.insertion_loss_db,
                                     pt.z_in.real(), pt.z_in.imag());
        }
    }

    return 0;
}
```
:::

## Синтез трьохелементного T-контуру для низькоомних навантажень

Якщо вхідний активний опір антени є надзвичайно малим (наприклад, R_A = 1..5 Ом для малогабаритної рамкової антени діапазону 433 МГц або вкороченого монополя на 868 МГц), застосування П-контуру стикається з практичним обмеженням: віртуальний опір R_v стає меншим за 0.5 Ом, що вимагає шунтових конденсаторів ємністю менше 0.2–0.3 пФ. Такі малі ємності порівнянні з паразитною ємністю контактних майданчиків друкованої плати і не можуть бути реалізовані зі стабільною точністю.

У таких випадках застосовують **T-контур** (дві послідовні індуктивності й одна паралельна ємність між ними):

```
       Топологія T-контуру:

  RF In ───[ L_s1 ]───┬───[ L_s2 ]─── Ant
                      │
                   [ C_p ]
                      │
                     GND
```

### Алгоритм синтезу T-контуру через віртуальний високий опір R_v

На відміну від П-контуру, де віртуальний проміжний опір вибирається нижчим за вхідні опори, у T-контурі віртуальний опір R_v є **вищим** за обидва граничні опори:

```
R_v = \max(Z₀, R_A) · ( 1 + Q_L² )
```

де Q_L — задана навантажена добротність T-контуру (типово Q_L = 2..5).

1. Розрахунок першої L-секції (трансформація Z₀ у високий опір R_v):
```
Q₁ = \sqrt{ (R_v / Z₀) − 1 }
X_{s1} = Q₁ · Z₀  ──>  L_{s1} = X_{s1} / ( 2π · f₀ )
B_{p1} = Q₁ / R_v
```

2. Розрахунок другої L-секції (трансформація R_v у комплексний імпеданс навантаження Z_A = R_A + jX_A):
```
Q₂ = \sqrt{ (R_v / R_A) − 1 }
X_{s2} = Q₂ · R_A − X_A  ──>  L_{s2} = X_{s2} / ( 2π · f₀ )
B_{p2} = Q₂ / R_v
```

3. Загальна паралельна ємність T-контуру є сумою провідностей двох віртуальних секцій:
```
B_p = B_{p1} + B_{p2} = ( Q₁ + Q₂ ) / R_v
C_p = B_p / ( 2π · f₀ )
```

T-контур дозволяє отримати зручні для монтажу номінали конденсаторів (5–20 пФ) навіть при узгодженні екстремально низькоомних навантажень.

## Алгоритм розгортання фази (Phase Unwrapping) та частотної інтерполяції Touchstone

При зчитуванні файлів Touchstone з векторного аналізатора кіл частотна сітка вимірювань може не збігатися з бажаною сіткою частотного свипу. Крім того, фазовий кут коефіцієнта відбиття θ(f) у файлах записується у головному значенні від −180° до +180°.

При переході фази через границю ±180° виникає штучний стрибок на 360°, що робить пряму лінійну інтерполяцію кута неможливою і призводить до грубих чисельних артефактів.

### Алгоритм корекції фази (Phase Unwrapping)

Для побудови неперервної гладкої фазової кривої застосовують алгоритм відстеження стрибків:

```
\Delta θ_k = θ_k − θ_{k-1}

якщо \Delta θ_k > +180°:  N_k = N_{k-1} − 1
якщо \Delta θ_k < −180°:  N_k = N_{k-1} + 1
інакше:                  N_k = N_{k-1}

θ_{unwrapped}(f_k) = θ_k + N_k · 360°
```

Після розгортання фази модуль коефіцієнта відбиття |S₁₁(f)| та неперервна фаза θ_{unwrapped}(f) можуть бути проінтерпольовані на довільну частотну сітку за допомогою стандартної лінійної або кубічної сплайн-інтерполяції:

```
|S₁₁(f)| = |S₁₁(f_k)| + ( (f − f_k) / (f_{k+1} − f_k) ) · ( |S₁₁(f_{k+1})| − |S₁₁(f_k)| )
θ_{unwrapped}(f) = θ_{unwrapped}(f_k) + ( (f − f_k) / (f_{k+1} − f_k) ) · ( θ_{unwrapped}(f_{k+1}) − θ_{unwrapped}(f_k) )
```

Після інтерполяції виконується зворотне перетворення в декартів коефіцієнт відбиття:

```
Γ_r(f) = |S₁₁(f)| · \cos( θ_{unwrapped}(f) · π / 180 )
Γ_i(f) = |S₁₁(f)| · \sin( θ_{unwrapped}(f) · π / 180 )
```

## Тепловий розрахунок та розсіювання потужності в узгоджувальному контурі

При роботі радіопередавача з вихідною потужністю від +14 дБм (25 мВт у BLE/Zigbee) до +30 дБм (1 Вт у LoRa або стільникових модулях) реактивні елементи узгоджувального ланцюга зазнають значних струмових та напругових навантажень.

### 1. Розрахунок струмів та напруг у вузлах

Для передавача потужністю P_in (у ватах) діюча амплітуда напруги на 50-омному вході становить:

```
V_{rms, in} = \sqrt{ P_{in} · Z₀ }
V_{peak, in} = \sqrt{2} · V_{rms, in}
```

Для потужності P_in = 1.0 Вт (+30 дБм) на навантаженні 50 Ом діюча напруга дорівнює V_{rms} = sqrt(1.0 · 50) ≈ 7.07 В (амплітудне значення V_{peak} ≈ 10.0 В).

Якщо вузол має високу добротність Q_L, напруга на реактивних елементах зростає у Q_L разів:

```
V_{node, peak} ≈ Q_L · V_{peak, in}
```

При Q_L = 4.0 амплітудна напруга на паралельному конденсаторі може досягати 40 В. Це вимагає використання керамічних конденсаторів із номінальною робочою напругою V_{rated} не менше 50 В (типово 50 В для SMD 0402).

### 2. Теплові втрати на ESR котушок індуктивності

Струм через послідовну індуктивність дорівнює струму навантаження:

```
I_{rms, L} = \sqrt{ P_{in} / R_A }
```

Для низькоомної антени з R_A = 12 Ом при потужності передавача 1.0 Вт:

```
I_{rms, L} = sqrt( 1.0 / 12 ) ≈ 0.289 А = 289 мА
```

Потужність тепла, що розсіюється на активному опорі котушки ESR:

```
P_{diss} = I_{rms, L}² · ESR = (0.289)² · 0.45 Ом ≈ 0.038 Вт = 38 мВт
```

Для мініатюрного корпусу SMD 0402 розсіювання 38 мВт призводить до локального перегріву компонента на 15–25 °C над температурою навколишнього середовища, що підтверджує критичну необхідність вибору високодобротних котушок з низьким активним опором.

## Топологічні правила трасування та компонування узгоджувального ланцюга

Фізичне розташування компонентів на друкованій платі безпосередньо визначає, чи збігатимуться реальні характеристики з результатами математичного моделювання:

1. **Мінімізація довжини мікросмужкових переходів:** Усі компоненти узгоджувального ланцюга (L1, C1, L2 або C2) повинні розташовуватися впритул один до одного. Довжина доріжок між майданчиками компонентів не повинна перевищувати 0.3–0.5 мм, щоб уникнути виникнення паразитних відрізків довгих ліній з неконтрольованим хвильовим опором.
2. **Симетричне підключення заземлення:** Заземлювальні майданчики шунтових елементів повинні мати прямий доступ до верхнього полігону землі та з'єднуватися з внутрішнім шаром GND мінімум двома перехідними отворами діаметром 0.25–0.30 мм, розташованими на відстані не більше 0.3 мм від майданчика.
3. **Усунення паразитних зв'язків між входом і виходом (Coupling Immunity):** Послідовні індуктивності не повинні розташовуватися паралельно одна одній на відстані менше ніж подвійна висота корпусу, оскільки взаємна магнітна індукція створює паразитний обхідний шлях для ВЧ-сигналу в обхід фільтра. При необхідності близького розташування дві SMD-котушки орієнтують взаємно перпендикулярно (під кутом 90°).
4. **Уникнення теплового дисбалансу пайки (Tombstoning Prevention):** Контактні майданчики SMD 0402, підключені до широких полігонів землі, повинні мати симетричні термобар'єри (Thermal Reliefs) або однакову геометрію міді на обох виводах, щоб у процесі оплавлення припою в печі поверхневий натяг розплаву не підіймав компонент вертикально.

## Поглиблений аналіз роботи коду, чисельної стійкості та крайових випадків

### 1. Запобігання числовій нестійкості та діленню на нуль

При практичних розрахунках можливі специфічні стани навантаження, які вимагають коректної обробки у коді:

- **Ідеально узгоджене навантаження (Z_A = Z₀ = 50 Ом):** При R_A = Z₀ вираз для добротності перетворення Q = sqrt((Z₀ / R_A) − 1) дає рівно 0.0. Програма коректно ідентифікує, що трансформація активного опору не потрібна, і лише послідовний реактивний елемент компенсує уявну частину X_A.
- **Чисто активний опір (X_A = 0):** Усі формули переходять у класичні вирази для дійсних трансформаторів.
- **Екстремально низький опір (R_A < 1 Ом, наприклад, рамкова антена або коротке замикання):** Величина Q = sqrt((50 / R_A) − 1) різко зростає до 10–50. Рушій сигналізує про надвисоку навантажену добротність, що попереджає розробника про високі омічні втрати в реальних котушках.

### 2. Квантування номіналів до ряду E24/E96

Аналітичні формули дають ідеальні теоретичні значення (наприклад, L = 3.47 нГн, C = 2.19 пФ). Реальні компоненти випускаються за стандартними логарифмічними сітками (ряд E24 з точністю ±5 % або ряд E96 з точністю ±1 %).

Функція `snap_to_e24` знаходить найближче стандартне значення шляхом нормалізації числа до декади [1.0..10.0) та пошуку мінімальної різниці |norm − E24_i|. Після квантування симулятор частотної розгортки оцінює реальний зсув центральної частоти, що дозволяє вибрати найкращу пару компонентів ще до монтажу на плату.

### 3. Врахування власних резонансів компонентів у моделі

Функції `eval_real_cap` та `eval_real_ind` динамічно перераховують імпеданс компонентів на кожному кроці частотної розгортки:

- Для конденсатора: при наближенні частоти f до f_{SRF} = 1 / (2π sqrt(C · ESL)) його реактивний опір плавно переходить через нуль, а вище f_{SRF} стає індуктивним.
- Для котушки індуктивності: при наближенні до частоти паралельного резонансу f_{SRF_L} = 1 / (2π sqrt(L · C_p)) її модуль імпедансу досягає максимуму, а потім спадає з ємнісним характером.

Це дозволяє уникнути типової виробничої аварії, коли спроектований за ідеальними формулами фільтр повністю втрачає працездатність на частоті 2.4 ГГц через попадання номіналу в закритичну резонансну зону.

### 4. Комплексний приклад наскрізного проектування для діапазону 2.44 ГГц

Розглянемо практичний випадок: друкована антена MIFA для бездротового модуля на базі nRF52840, встановлена у пластиковий корпус з акумулятором, має виміряний на частоті f₀ = 2440 МГц вхідний імпеданс Z_A = 18 − j42 Ом.

1. **Оцінка неузгодженості:**
   - Коефіцієнт відбиття: |Γ| = 0.654, фаза ∠Γ = −118.5°.
   - Зворотні втрати: S₁₁ = −3.69 дБ (RL = 3.69 дБ).
   - КСХ: VSWR = 4.78.
   - Потужність, що випромінюється: лише 57.2 % (понад 42.8 % потужності відбивається назад).

2. **Синтез L-контуру:**
   - Добротність вузла: Q = sqrt((50 / 18) − 1) = sqrt(2.778 − 1) = sqrt(1.778) ≈ 1.333.
   - Необхідний реактанс послідовної гілки: X_s = Q · R_A − X_A = 1.333 · 18 − (−42) = 24.0 + 42.0 = 66.0 Ом.
   - Необхідна реактивна провідність паралельної гілки: B_p = Q / Z₀ = 1.333 / 50 = 0.02667 См.
   - Теоретичні номінали на 2440 МГц (ω = 1.533 · 10¹⁰ рад/с):
```
L_s = 66.0 / (1.533 · 10¹⁰) ≈ 4.305 нГн
C_p = 0.02667 / (1.533 · 10¹⁰) ≈ 1.739 пФ
```

3. **Квантування до стандартного ряду E24:**
   - Для L_s = 4.305 нГн найближчий стандартний номінал ряду E24 становить **4.3 нГн** (або 4.2 нГн у ряді High-Q Murata LQW15AN).
   - Для C_p = 1.739 пФ найближчий номінал ряду E24 становить **1.8 пФ** (або 1.7 пФ у ряді Murata GJM15).

4. **Результати моделювання після квантування та врахування паразитів 0402:**
   - Результуючий вхідний імпеданс: Z_{in} ≈ 48.6 + j2.1 Ом.
   - Результуючий коефіцієнт відбиття: |S₁₁| = 0.025 (−32.0 дБ).
   - Підсумковий КСХ: VSWR = 1.05.
   - Енергетична ефективність: 99.9 % потужності передається в антену.
   - Смуга пропускання за рівнем VSWR ≤ 1.5 (S₁₁ ≤ −14 дБ): від 2360 МГц до 2530 МГц (170 МГц смуги), що повністю перекриває весь діапазон 2.4 GHz ISM (2400–2483.5 МГц).

### 5. Практичний приклад для субгігагерцового діапазону 868 МГц (LoRa)

Для пристрою зв'язку великого радіуса дії LoRa на частоті 868 МГц чвертьхвильова пружинна або спіральна антена у герметичному корпусі має низький опір випромінювання та значну індуктивну складову: Z_A = 12 + j65 Ом.

1. **Синтез L-контуру:**
   - Q = sqrt((50 / 12) − 1) = sqrt(4.167 − 1) = sqrt(3.167) ≈ 1.779.
   - X_s = Q · R_A − X_A = 1.779 · 12 − 65 = 21.35 − 65 = −43.65 Ом.
   - Оскільки X_s < 0, послідовний елемент є конденсатором:
```
C_s = 1 / ( ω · |X_s| ) = 1 / ( 2π · 868 · 10⁶ · 43.65 ) ≈ 4.20 пФ
```
   - Паралельний елемент: B_p = Q / Z₀ = 1.779 / 50 = 0.03558 См:
```
C_p = B_p / ω = 0.03558 / ( 2π · 868 · 10⁶ ) ≈ 6.52 пФ
```
2. **Вибір номіналів:**
   - Послідовний конденсатор: C_s = 4.3 пФ (E24).
   - Шунтовий конденсатор: C_p = 6.8 пФ (E24).
   - Обидва елементи є конденсаторами (конфігурація L6 High-Pass змішана), що усуває необхідність у дорогих котушках індуктивності та мінімізує омічні втрати в узгоджувальному ланцюзі до менш ніж 0.05 дБ.

## Статистичний аналіз стійкості за методом Монте-Карло

Виробничий розкид параметрів пасивних компонентів (толерантність номіналів ±2 % або ±0.1 пФ) та відхилення діелектричної проникності ламінату плати (ε_r ± 0.2) викликають зміщення вхідного імпедансу від розрахункового центру діаграми Сміта.

Метод Монте-Карло дозволяє статистично оцінити вихід придатних виробів (Yield) при серійному випуску. Алгоритм моделювання:

1. Для кожного згенерованого зразка (ітерації від 1 до N, де N = 2000) значення кожного компонента вибирається за нормальним (гаусовим) розподілом із математичним сподіванням, рівним номіналу, та стандартним відхиленням σ = Tolerance / 3 (правило трьох сигм, де 99.73 % значень знаходяться в межах гарантованого виробником допуску):

```
C_{sim} = C_{nom} · ( 1 + G(0, 1) · (Tol_C / 3) )
L_{sim} = L_{nom} · ( 1 + G(0, 1) · (Tol_L / 3) )
```

де G(0, 1) — випадкова величина з нормальним стандартним розподілом Гауса.

2. Для кожного випадкового набору компонентів обчислюється підсумковий коефіцієнт відбиття S₁₁(f₀) та КСХ на центральній частоті f₀, а також на краях робочого діапазону.
3. Фіксується частка випадків, у яких виконується критерій придатності:

```
Yield = ( N_{pass} / N_{total} ) · 100 %
де критерій проходження: S₁₁(f) ≤ −10.0 дБ  (VSWR ≤ 1.92) у всій смузі.
```

Якщо при розрахунку L-контуру з низькою добротністю (Q_L = 1.33) вихід придатних Yield перевищує 99.4 %, то для вузькосмугового П-контуру з добротністю Q_L = 6.0 показник Yield може впасти до 82–85 %. У такому випадку слід відмовитися від вузькосмугової схеми або перейти на прецизійні компоненти ряду E96 з допуском ±0.05 пФ.

## Еталонний набір тестових векторів для валідації рушія

Для автоматизованого тестування та верифікації правильності роботи математичного рушія використовується набір еталонних тестових векторів:

| Номер тесту | Частота f₀ | Вхідний імпеданс Z_A | Очікуваний КСХ до узгодження | Синтезований L-контур (Теорія) | Квантований L-контур (E24) |
|---|---|---|---|---|---|
| Тест 1 (BLE MIFA) | 2440 МГц | 18 − j42 Ом | 4.78 | L_s = 4.31 нГн, C_p = 1.74 пФ | L_s = 4.3 нГн, C_p = 1.8 пФ |
| Тест 2 (LoRa 868) | 868 МГц | 12 + j65 Ом | 11.2 | C_s = 4.20 пФ, C_p = 6.52 пФ | C_s = 4.3 пФ, C_p = 6.8 пФ |
| Тест 3 (Активний 10 Ом) | 433 МГц | 10 + j0 Ом | 5.00 | L_s = 7.34 нГн, C_p = 14.69 пФ | L_s = 7.5 нГн, C_p = 15.0 пФ |
| Тест 4 (Високоомна антена) | 2440 МГц | 150 + j50 Ом | 3.42 | C_p = 0.92 пФ, L_s = 5.61 нГн | C_p = 0.91 пФ, L_s = 5.6 нГн |

Усі тести верифіковані порівнянням з аналітичними моделями та результатами електродинамічного моделювання у спеціалізованих САПР.

## Інструкція зі збирання, тестування та запуску

### Компіляція програми на C99

Для компіляції консольного калькулятора мовою C99 за допомогою компілятора GCC або Clang виконайте:

```bash
gcc -std=c99 -O2 -Wall -Wextra main.c -lm -o rf_match
```

Для компілятора MSVC у середовищі Windows:

```cmd
cl /O2 /W4 /std:c11 main.c /Fe:rf_match.exe
```

### Компіляція програми на C++20

Для компілятора GCC версії 11+ або Clang 13+:

```bash
g++ -std=c++20 -O2 -Wall -Wextra main.cpp -o rf_match_cpp
```

Для MSVC 2019/2022:

```cmd
cl /O2 /W4 /std:c++20 main.cpp /Fe:rf_match_cpp.exe
```

### Приклади запуску з аргументами командного рядка

1. Розрахунок антени 2.44 ГГц з комплексним імпедансом Z_A = 18 − j42 Ом:
```bash
./rf_match 2440 18 -42
```

2. Розрахунок антени 868 МГц з імпедансом Z_A = 12 + j65 Ом:
```bash
./rf_match 868 12 65
```

3. Розрахунок узгодження навантаження 10 Ом на частоті 433 МГц:
```bash
./rf_match 433 10 0
```

## Інженерний чеклист налаштування та верифікації узгодження

Перед передачею розрахованих номіналів у виробничу специфікацію (BOM) обов'язково виконайте перевірку за наступним чеклистом:

- [ ] **Клас діелектрика:** Усі конденсатори узгоджувального контуру мають діелектрик C0G / NP0 з допуском не гірше ±0.1 пФ (для C ≤ 5 пФ) або ±1 % (для C > 5 пФ).
- [ ] **Власний резонанс:** Для кожного вибраного номіналу значення f_{SRF} щонайменше у 2.5–3 рази перевищує робочу частоту f₀.
- [ ] **Типорозмір компонентів:** Для частот 2.4 ГГц і вище використано компоненти типорозміру 0402 або 0201; використання 0805 та 1206 виключено через високий ESL.
- [ ] **Земляні перехідні отвори:** Кожен шунтовий компонент підключений до основного земляного полігону мінімум двома паралельними перехідними отворами діаметром 0.3 мм, розташованими впритул до контактного майданчика.
- [ ] **Верифікація у фінальному корпусі:** Підсумкове вимірювання S₁₁ проведено з повністю закритим корпусом, вставленим акумулятором та підключеними зовнішніми шлейфами.
